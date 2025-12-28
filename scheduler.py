# scheduler.py

from config import MAX_DATA_HUB_POWER

PEAK_HEAT_TEMP = 38  # °C

class SmartScheduler:
    def __init__(self):
        self.jobs = []

    def add_job(self, job):
        self.jobs.append(job)

    def schedule(self, solar_kw, temp, current_hour):
        running_jobs = []
        used_power = 0.0

        # Sort by priority
        priority_order = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}
        sorted_jobs = sorted(self.jobs, key=lambda j: priority_order[j.priority])

        grid_allowance = 2.0  # kW limit
        available_power = solar_kw + grid_allowance

        for job in sorted_jobs:
            if job.status == "DONE":
                continue

            # Check deadline: skip if cannot finish before deadline
            remaining_hours = (job.deadline - current_hour) if job.deadline else None
            if remaining_hours is not None:
                max_power_time = remaining_hours * 60  # convert to minutes
                if job.remaining_time > max_power_time:
                    # Cannot finish in time even at full power, skip this step
                    continue

            # HIGH priority always allowed
            if job.priority == "HIGH":
                if used_power + job.power_kw <= available_power:
                    running_jobs.append(job)
                    used_power += job.power_kw

            # MEDIUM prefers solar or safe temp
            elif job.priority == "MEDIUM":
                if solar_kw >= 2.0 and temp < PEAK_HEAT_TEMP:
                    if used_power + job.power_kw <= available_power:
                        running_jobs.append(job)
                        used_power += job.power_kw

            # LOW strictly solar-driven
            elif job.priority == "LOW":
                if solar_kw >= job.power_kw:
                    if used_power + job.power_kw <= available_power:
                        running_jobs.append(job)
                        used_power += job.power_kw

        return running_jobs
