from config import MAX_DATA_HUB_POWER

PEAK_TEMP = 38  # °C

class SmartScheduler:
    def __init__(self):
        self.jobs = []

    def add_job(self, job):
        self.jobs.append(job)

    def schedule(self, solar, temp, hour):
        running = []
        used = 0

        # 🔑 urgency score: deadline > priority > conditions
        sorted_jobs = sorted(
            self.jobs,
            key=lambda j: (
                j.deadline is not None and hour > j.deadline,
                j.priority == "HIGH",
                -(j.deadline or 99)
            ),
            reverse=True,
        )

        for job in sorted_jobs:
            if job.status == "DONE":
                continue

            # Avoid overheating
            if temp > PEAK_TEMP and job.priority == "LOW":
                continue

            # Prefer solar for medium jobs
            if job.priority == "MEDIUM" and solar < 2:
                continue

            if used + job.power_kw <= MAX_DATA_HUB_POWER:
                running.append(job)
                used += job.power_kw

        return running
