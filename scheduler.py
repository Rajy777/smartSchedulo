"""
Smart Scheduler - Intelligent job scheduling with multi-objective optimization.

Scheduling priorities:
1. High-priority jobs: Always run (even in high temp)
2. Deadline urgency: Jobs close to deadline run first
3. Solar optimization: Medium-priority jobs prefer solar hours
4. Thermal management: Low-priority jobs skip when temp > threshold
"""

from config import MAX_DATA_HUB_POWER, THERMAL_THRESHOLD


class SmartScheduler:
    """
    Smart scheduler that optimizes for:
    - SLA compliance (deadline adherence)
    - Solar energy utilization
    - Thermal management
    - Carbon reduction
    """

    def __init__(self):
        self.jobs = []

    def add_job(self, job):
        """Add a job to the scheduler's queue."""
        self.jobs.append(job)

    def schedule(self, solar_available_kw, current_temp, current_hour):
        """
        Intelligently schedule jobs based on current conditions.

        Scheduling algorithm:
        1. Filter to WAITING jobs only
        2. Sort by urgency score (deadline proximity, priority)
        3. Apply thermal and solar constraints
        4. Pack jobs until power limit reached

        Args:
            solar_available_kw (float): Available solar power in kW
            current_temp (float): Current hub temperature in °C
            current_hour (float): Current simulation hour

        Returns:
            list[Job]: List of jobs selected to run this timestep
        """
        running_jobs = []
        total_power_used = 0.0

        # Only consider jobs that are waiting (not done, not already running)
        waiting_jobs = [j for j in self.jobs if j.is_waiting()]

        # Sort jobs by scheduling priority
        sorted_jobs = self._prioritize_jobs(waiting_jobs, current_hour, solar_available_kw)

        # Schedule jobs in priority order
        for job in sorted_jobs:
            # Check thermal constraint: skip low-priority jobs if too hot
            if current_temp > THERMAL_THRESHOLD and job.priority == "low":
                continue

            # Check solar constraint: medium-priority jobs prefer solar availability
            # Only run medium jobs if reasonable solar power is available
            if job.priority == "medium" and solar_available_kw < 1.0:
                continue

            # Check power capacity constraint
            if total_power_used + job.power_kw <= MAX_DATA_HUB_POWER:
                running_jobs.append(job)
                job.start(current_hour)  # Mark as running
                total_power_used += job.power_kw
            # Note: If power limit reached, higher-priority jobs already scheduled

        return running_jobs

    def _prioritize_jobs(self, jobs, current_hour, solar_available_kw):
        """
        Sort jobs by scheduling priority.

        Priority rules (highest to lowest):
        1. High-priority jobs (critical workloads)
        2. Jobs past deadline (already violated, need to complete ASAP)
        3. Jobs approaching deadline (by urgency score)
        4. Medium-priority jobs during good solar (maximize solar usage)
        5. Low-priority jobs (best-effort)

        Args:
            jobs (list[Job]): Jobs to prioritize
            current_hour (float): Current hour
            solar_available_kw (float): Available solar power

        Returns:
            list[Job]: Sorted jobs (highest priority first)
        """
        def priority_key(job):
            """
            Generate priority tuple for sorting.
            Python sorts tuples lexicographically, so first element is most important.
            Returns tuple of (sort_value_1, sort_value_2, ...)
            Lower values = higher priority (will be sorted first)
            """
            # Priority level encoding (lower = higher priority)
            priority_levels = {"high": 0, "medium": 1, "low": 2}
            priority_level = priority_levels.get(job.priority, 3)

            # Deadline urgency (negative urgency = less urgent, sorts later)
            urgency = -job.urgency_score(current_hour)

            # Solar preference for medium jobs (encourage solar usage)
            solar_bonus = 0
            if job.priority == "medium" and solar_available_kw > 2.0:
                solar_bonus = -1  # Negative = higher priority

            return (
                priority_level,     # 1st: high=0, medium=1, low=2
                urgency,            # 2nd: more urgent jobs first (lower value)
                solar_bonus,        # 3rd: bonus for solar-friendly scheduling
                job.power_kw        # 4th: prefer smaller jobs (better packing)
            )

        return sorted(jobs, key=priority_key)

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
        return (f"SmartScheduler({stats['total_jobs']} jobs: "
                f"{stats['completed']} done, "
                f"{stats['running']} running, "
                f"{stats['waiting']} waiting)")


if __name__ == "__main__":
    # Test the scheduler
    from job import Job

    print("Testing SmartScheduler...")
    scheduler = SmartScheduler()

    # Add test jobs
    scheduler.add_job(Job("HighPrio", 3, 60, "high", deadline_hour=12))
    scheduler.add_job(Job("MediumPrio", 2, 120, "medium", deadline_hour=18))
    scheduler.add_job(Job("LowPrio", 1, 180, "low"))
    scheduler.add_job(Job("Urgent", 2, 90, "medium", deadline_hour=10))

    print(f"\n{scheduler}")

    # Simulate scheduling at hour 9 (good solar, normal temp)
    print("\n--- Hour 9: Good solar (5 kW), normal temp (28°C) ---")
    running = scheduler.schedule(solar_available_kw=5, current_temp=28, current_hour=9)
    for job in running:
        print(f"  Running: {job.name} ({job.priority}, {job.power_kw} kW)")

    # Simulate scheduling at hour 19 (no solar, high temp)
    print("\n--- Hour 19: No solar (0 kW), high temp (35°C) ---")
    running = scheduler.schedule(solar_available_kw=0, current_temp=35, current_hour=19)
    for job in running:
        print(f"  Running: {job.name} ({job.priority}, {job.power_kw} kW)")

    print(f"\nFinal stats: {scheduler.get_statistics()}")