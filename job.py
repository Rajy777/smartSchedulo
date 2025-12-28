class Job:
    def __init__(self, name, power_kw, duration_minutes, priority, deadline=None):
        self.name = name
        self.power_kw = power_kw
        self.total_time = duration_minutes  # total duration
        self.remaining_time = duration_minutes
        self.priority = priority  # HIGH, MEDIUM, LOW
        self.status = "PENDING"  # PENDING / RUNNING / DONE
        self.deadline = deadline  # hour by which job must finish

    def run_step(self, step_minutes):
        if self.status == "DONE":
            return
        self.remaining_time -= step_minutes
        if self.remaining_time <= 0:
            self.remaining_time = 0
            self.status = "DONE"
        else:
            self.status = "RUNNING"
