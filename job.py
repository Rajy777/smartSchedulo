"""
Job class for data hub scheduling simulation.
Each job has power requirements, duration, priority, and optional deadline.
"""

class Job:
    """
    Represents a computational job in the data hub.

    Attributes:
        name (str): Job identifier
        power_kw (float): Power consumption in kW
        duration (int): Total duration in minutes
        remaining (int): Remaining duration in minutes
        priority (str): 'high', 'medium', or 'low'
        deadline (int): Deadline hour (0-24), or None for no deadline
        status (str): 'WAITING', 'RUNNING', or 'DONE'
        penalized (bool): Whether SLA penalty has been applied
        start_hour (float): When job actually started (for timeline tracking)
    """

    def __init__(self, name, power_kw, duration_min, priority, deadline_hour=None):
        self.name = name
        self.power_kw = power_kw
        self.duration = duration_min  # Original duration (immutable)
        self.remaining = duration_min  # Decreases as job runs
        self.priority = priority.lower()  # Normalize to lowercase
        self.deadline = deadline_hour
        self.status = "WAITING"
        self.penalized = False
        self.start_hour = None  # Track when job started

        # Validate priority
        if self.priority not in ['high', 'medium', 'low']:
            raise ValueError(f"Invalid priority '{priority}'. Must be 'high', 'medium', or 'low'")

    def start(self, current_hour):
        """Mark job as running and record start time."""
        if self.status == "WAITING":
            self.status = "RUNNING"
            if self.start_hour is None:
                self.start_hour = current_hour

    def run_step(self, dt_min, current_hour):
        """
        Execute one time step of the job.

        Args:
            dt_min (int): Time step duration in minutes
            current_hour (float): Current simulation hour
        """
        if self.status == "DONE":
            return

        # Mark as running if not already
        if self.status == "WAITING":
            self.start(current_hour)

        # Reduce remaining time
        self.remaining -= dt_min

        # Check if completed
        if self.remaining <= 0:
            self.remaining = 0
            self.status = "DONE"

    def deadline_missed(self, current_hour):
        """
        Check if job missed its deadline.
        Only returns True once per job (when first detected).

        Args:
            current_hour (float): Current simulation hour

        Returns:
            bool: True if deadline just missed and not yet penalized
        """
        if self.deadline is None:
            return False

        # Deadline missed if: past deadline AND not done AND not already penalized
        if current_hour > self.deadline and self.status != "DONE" and not self.penalized:
            self.penalized = True
            return True

        return False

    def is_waiting(self):
        """Check if job is waiting to run."""
        return self.status == "WAITING"

    def is_running(self):
        """Check if job is currently running."""
        return self.status == "RUNNING"

    def is_done(self):
        """Check if job is completed."""
        return self.status == "DONE"

    def urgency_score(self, current_hour):
        """
        Calculate urgency score for scheduling priority.
        Higher score = more urgent.

        Returns:
            float: Urgency score (higher is more urgent)
        """
        if self.deadline is None:
            return 0.0

        hours_until_deadline = self.deadline - current_hour
        hours_needed = self.remaining / 60.0

        # If already past deadline, maximum urgency
        if hours_until_deadline <= 0:
            return float('inf')

        # Urgency increases as deadline approaches relative to time needed
        return hours_needed / hours_until_deadline

    def __repr__(self):
        deadline_str = f"{self.deadline}h" if self.deadline else "None"
        return (f"Job('{self.name}', {self.power_kw}kW, "
                f"{self.remaining}/{self.duration}min, "
                f"priority={self.priority}, deadline={deadline_str}, "
                f"status={self.status})")