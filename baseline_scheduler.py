from config import MAX_DATA_HUB_POWER

class BaselineScheduler:
    def __init__(self):
        self.jobs = []

    def add_job(self, job):
        self.jobs.append(job)

    def schedule(self, solar, temp, hour=None):
        running = []
        used = 0

        for job in self.jobs:
            if job.status == "DONE":
                continue
            if used + job.power_kw <= MAX_DATA_HUB_POWER:
                running.append(job)
                used += job.power_kw

        return running
