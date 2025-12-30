"""
Simulation runner with dataset support.

✅ BACKWARD COMPATIBLE: Works with or without datasets.
✅ NO LOGIC CHANGES: Only data source location changed.
"""

from config import (
    SIMULATION_START_HOUR,
    SIMULATION_END_HOUR,
    TIME_STEP_MINUTES,
    HEAT_ACCUMULATION,
    COOLING_EFFICIENCY,
    THERMAL_DISSIPATION,
    IDEAL_TEMP
)
from metrics import Metrics
from cooling_model import cooling_power_kw

# Import data adapters
from data_adapter import create_solar_source, create_temperature_source


def run_simulation(scheduler, use_smart_features=True,
                   solar_source=None, temperature_source=None):
    """
    Run scheduling simulation with optional dataset support.

    ✅ CRITICAL: If no datasets provided, uses hardcoded models (backward compatible).

    Args:
        scheduler: Scheduler instance (BaselineScheduler or SmartScheduler)
        use_smart_features (bool): If True, scheduler receives solar/temp info
        solar_source (DataSource): Solar data source (None = use model)
        temperature_source (DataSource): Temperature data source (None = use model)

    Returns:
        tuple: (metrics, time_log, grid_log, solar_log, cooling_log, temp_log)
    """
    # ✅ Create data sources (fallback to models if None)
    if solar_source is None:
        solar_source = create_solar_source(csv_path=None)

    if temperature_source is None:
        temperature_source = create_temperature_source(csv_path=None)

    # Initialize metrics tracker
    metrics = Metrics()

    # Initialize time series logs
    time_log = []
    grid_log = []
    solar_log = []
    cooling_log = []
    temp_log = []

    # Initialize hub temperature at ambient starting temp
    current_temp = temperature_source.get(SIMULATION_START_HOUR)
    current_hour = SIMULATION_START_HOUR

    # Time step in hours
    dt_hours = TIME_STEP_MINUTES / 60.0

    # Track currently running jobs across timesteps
    currently_running = []

    # Main simulation loop
    while current_hour < SIMULATION_END_HOUR:
        # ===== 1. ENVIRONMENTAL CONDITIONS (FROM DATA SOURCES) =====
        ambient_temp = temperature_source.get(current_hour)
        solar_available = solar_source.get(current_hour)

        # ===== 2. EXECUTE RUNNING JOBS =====
        for job in currently_running[:]:
            job.run_step(TIME_STEP_MINUTES, current_hour)
            if job.is_done():
                currently_running.remove(job)

        # ===== 3. SCHEDULER DECISION =====
        if use_smart_features:
            new_jobs = scheduler.schedule(solar_available, current_temp, current_hour)
        else:
            new_jobs = scheduler.schedule(0.0, 0.0, current_hour)

        # Add new jobs to running list
        for job in new_jobs:
            if job not in currently_running and not job.is_done():
                currently_running.append(job)

        # ===== 4. POWER CALCULATIONS =====
        compute_power = sum(job.power_kw for job in currently_running)
        solar_used = min(compute_power, solar_available)
        grid_power = compute_power - solar_used
        cooling_power_needed = cooling_power_kw(current_temp, compute_power)

        # ===== 5. THERMAL STATE UPDATE =====
        temp_change = (
            HEAT_ACCUMULATION * compute_power
            - COOLING_EFFICIENCY * cooling_power_needed
            - THERMAL_DISSIPATION * (current_temp - ambient_temp)
        )
        current_temp += temp_change
        current_temp = max(ambient_temp - 5, min(current_temp, 100))

        # ===== 6. METRICS TRACKING =====
        metrics.add_energy(
            load_kw=compute_power,
            solar_kw=solar_used,
            dt_hours=dt_hours
        )
        metrics.add_cooling(cooling_power_needed, dt_hours)

        # ===== 7. CHECK DEADLINES =====
        for job in scheduler.jobs:
            if job.deadline_missed(current_hour):
                metrics.add_deadline_penalty()

        # ===== 8. LOGGING =====
        time_log.append(current_hour)
        grid_log.append(grid_power)
        solar_log.append(solar_used)
        cooling_log.append(cooling_power_needed)
        temp_log.append(current_temp)

        # ===== 9. TIME ADVANCE =====
        current_hour += dt_hours

    return metrics, time_log, grid_log, solar_log, cooling_log, temp_log


def get_job_timeline(scheduler):
    """Extract job execution timeline from scheduler's jobs."""
    timeline = []

    for job in scheduler.jobs:
        if job.start_hour is not None:
            timeline.append({
                'name': job.name,
                'start': job.start_hour,
                'duration': job.duration / 60.0,
                'end': job.start_hour + (job.duration / 60.0),
                'priority': job.priority,
                'power_kw': job.power_kw,
                'completed': job.is_done(),
                'deadline_missed': job.penalized
            })

    return timeline