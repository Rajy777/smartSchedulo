"""
Baseline Scheduler - Simple FIFO (First-In-First-Out) scheduling.

This is the naive reference scheduler that:
- Ignores solar availability (always uses grid)
- Ignores temperature (no thermal management)
- Ignores job priorities (treats all equal)
- Ignores deadlines (no urgency consideration)
- Simply runs jobs in order added until power limit reached

Used as comparison baseline to quantify smart scheduler benefits.
"""

from config import MAX_DATA_HUB_POWER, BASELINE_BACKGROUND_LOAD


class BaselineScheduler:
    """
    Naive FIFO scheduler with no optimization.

    Represents typical data hub scheduling without intelligence:
    - Jobs scheduled in arrival order
    - No awareness of energy sources
    - No thermal constraints
    - Only respects power capacity limit
    """

    def __init__(self):
        self.jobs = []

    def add_job(self, job):
        """
        Add a job to the scheduler's queue.
        Jobs are scheduled in the order they're added (FIFO).
        """
        self.jobs.append(job)

    def schedule(self, solar, temp, hour=None):
        """
        Schedule jobs using simple FIFO logic.

        Baseline logic:
        1. Ignore solar, temp, hour (parameters accepted for interface compatibility)
        2. Filter to WAITING jobs only
        3. Schedule jobs in order added
        4. Stop when power capacity reached

        Args:
            solar (float): Available solar power - IGNORED by baseline
            temp (float): Current temperature - IGNORED by baseline
            hour (float): Current hour - IGNORED by baseline

        Returns:
            list[Job]: List of jobs selected to run this timestep

        Note:
            Baseline schedulers are intentionally naive to serve as comparison point.
            They represent "business as usual" without smart optimization.
        """
        running_jobs = []

        # Account for background load (infrastructure, cooling, networking, etc.)
        total_power_used = BASELINE_BACKGROUND_LOAD

        # Only consider jobs that are waiting (not done, not already running)
        waiting_jobs = [j for j in self.jobs if j.is_waiting()]

        # Simple FIFO: schedule jobs in order added
        for job in waiting_jobs:
            # Check if adding this job would exceed power capacity
            if total_power_used + job.power_kw <= MAX_DATA_HUB_POWER:
                running_jobs.append(job)
                job.start(hour if hour is not None else 0)  # Mark as running
                total_power_used += job.power_kw
            else:
                # Power limit reached, stop scheduling
                break

        return running_jobs

    def get_statistics(self):
        """
        Get scheduling statistics.

        Returns:
            dict: Statistics about job queue and completion
        """
        total = len(self.jobs)
        done = sum(1 for j in self.jobs if j.is_done())
        running = sum(1 for j in self.jobs if j.is_running())
        waiting = sum(1 for j in self.jobs if j.is_waiting())
        penalized = sum(1 for j in self.jobs if j.penalized)

        return {
            "total_jobs": total,
            "completed": done,
            "running": running,
            "waiting": waiting,
            "deadline_violations": penalized,
            "completion_rate": done / total if total > 0 else 0.0
        }

    def __repr__(self):
        stats = self.get_statistics()
        return (f"BaselineScheduler({stats['total_jobs']} jobs: "
                f"{stats['completed']} done, "
                f"{stats['running']} running, "
                f"{stats['waiting']} waiting)")


if __name__ == "__main__":
    # Test the baseline scheduler
    from job import Job

    print("Testing BaselineScheduler...")
    scheduler = BaselineScheduler()

    # Add test jobs
    scheduler.add_job(Job("Job1", 4, 60, "low"))
    scheduler.add_job(Job("Job2", 3, 90, "high", deadline_hour=10))
    scheduler.add_job(Job("Job3", 2, 120, "medium"))
    scheduler.add_job(Job("Job4", 5, 180, "low"))

    print(f"\n{scheduler}")
    print(f"Background load: {BASELINE_BACKGROUND_LOAD} kW")
    print(f"Max capacity: {MAX_DATA_HUB_POWER} kW")
    print(f"Available for jobs: {MAX_DATA_HUB_POWER - BASELINE_BACKGROUND_LOAD} kW")

    # Simulate scheduling (baseline ignores these parameters)
    print("\n--- Scheduling (solar=5 kW, temp=35°C, hour=9) ---")
    print("(Baseline ignores solar, temp, hour)")
    running = scheduler.schedule(solar=5, temp=35, hour=9)

    print(f"\nScheduled {len(running)} jobs:")
    for job in running:
        print(f"  {job.name}: {job.power_kw} kW, {job.priority} priority, "
              f"deadline={job.deadline or 'None'}")

    total_power = sum(j.power_kw for j in running) + BASELINE_BACKGROUND_LOAD
    print(f"\nTotal power: {total_power} kW (includes {BASELINE_BACKGROUND_LOAD} kW background)")

    # Show what didn't fit
    not_scheduled = [j for j in scheduler.jobs if j.is_waiting()]
    if not_scheduled:
        print(f"\nNot scheduled (insufficient capacity):")
        for job in not_scheduled:
            print(f"  {job.name}: {job.power_kw} kW")