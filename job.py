class Job:
    def __init__(self, name, power_kw, duration_min, priority, deadline_hour=None):
        self.name = name
        self.power_kw = power_kw
        self.remaining = duration_min
        self.priority = priority
        self.deadline = deadline_hour
        self.status = "WAITING"
        self.penalized = False

    def run_step(self, minutes):
        if self.remaining <= 0:
            self.status = "DONE"
            return

        self.remaining -= minutes
        self.status = "RUNNING"

        if self.remaining <= 0:
            self.status = "DONE"

    def deadline_missed(self, hour):
        return (
            self.deadline is not None
            and hour > self.deadline
            and self.status != "DONE"
            and not self.penalized
        )
