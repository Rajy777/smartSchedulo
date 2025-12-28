# baseline_scheduler.py

from config import MAX_DATA_HUB_POWER

class BaselineScheduler:
    def __init__(self):
        self.jobs = []

    def add_job(self, job):
        self.jobs.append(job)

    # Make schedule accept same arguments as SmartScheduler
    def schedule(self, solar_kw=None, temp=None, current_hour=None):
        running_jobs = []
        used_power = 0
        for job in self.jobs:
            if job.status == "DONE":
                continue
            if used_power + job.power_kw <= 10:  # MAX_DATA_HUB_POWER
                running_jobs.append(job)
                used_power += job.power_kw
        return running_jobs
