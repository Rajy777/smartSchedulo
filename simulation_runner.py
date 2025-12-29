"""
Simulation runner for data hub scheduling comparison.

Executes the core simulation loop:
1. Generate environmental conditions (solar, temperature)
2. Scheduler decides which jobs to run
3. Calculate power consumption and cooling needs
4. Update thermal state
5. Track metrics (energy, carbon, penalties)
6. Advance time and repeat
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
from solar_model import solar_power
from temperature_model import ambient_temperature
from cooling_model import cooling_power_kw


def run_simulation(scheduler, use_smart_features=True):
    """
    Run scheduling simulation for one day.

    ✅ CRITICAL FIX: Jobs continue running across timesteps until complete.

    Args:
        scheduler: Scheduler instance (BaselineScheduler or SmartScheduler)
        use_smart_features (bool): If True, scheduler receives solar/temp info.
                                    If False, scheduler gets dummy values (baseline mode)

    Returns:
        tuple: (metrics, time_log, grid_log, solar_log, cooling_log, temp_log)
    """
    # Initialize metrics tracker
    metrics = Metrics()

    # Initialize time series logs for plotting
    time_log = []
    grid_log = []
    solar_log = []
    cooling_log = []
    temp_log = []

    # Initialize hub temperature at ambient starting temp
    current_temp = ambient_temperature(SIMULATION_START_HOUR)
    current_hour = SIMULATION_START_HOUR

    # Time step in hours
    dt_hours = TIME_STEP_MINUTES / 60.0

    # ✅ NEW: Track currently running jobs across timesteps
    currently_running = []

    # Main simulation loop
    while current_hour < SIMULATION_END_HOUR:
        # ===== 1. ENVIRONMENTAL CONDITIONS =====
        ambient_temp = ambient_temperature(current_hour)
        solar_available = solar_power(current_hour)

        # ===== 2. EXECUTE RUNNING JOBS =====
        # First, continue running jobs that are already in progress
        for job in currently_running[:]:  # Use slice to safely modify during iteration
            job.run_step(TIME_STEP_MINUTES, current_hour)
            if job.is_done():
                currently_running.remove(job)

        # ===== 3. SCHEDULER DECISION =====
        # Only ask scheduler if we have capacity for new jobs
        # Scheduler now sees what's already running
        if use_smart_features:
            new_jobs = scheduler.schedule(solar_available, current_temp, current_hour)
        else:
            # Baseline: scheduler doesn't see solar/temp
            new_jobs = scheduler.schedule(0.0, 0.0, current_hour)

        # ✅ CRITICAL: Only add jobs that aren't already running
        for job in new_jobs:
            if job not in currently_running and not job.is_done():
                currently_running.append(job)

        # ===== 4. POWER CALCULATIONS =====
        # Total compute power from ALL currently running jobs
        compute_power = sum(job.power_kw for job in currently_running)

        # How much solar can actually be used (limited by available solar)
        solar_used = min(compute_power, solar_available)

        # Grid power = what solar doesn't cover
        grid_power = compute_power - solar_used

        # Cooling power needed based on current temperature
        cooling_power_needed = cooling_power_kw(current_temp, compute_power)

        # ===== 5. THERMAL STATE UPDATE =====
        temp_change = (
            HEAT_ACCUMULATION * compute_power              # Heat added by computation
            - COOLING_EFFICIENCY * cooling_power_needed    # Heat removed by cooling
            - THERMAL_DISSIPATION * (current_temp - ambient_temp)  # Natural dissipation
        )
        current_temp += temp_change

        # Sanity check: temperature shouldn't go below ambient or exceed extreme values
        current_temp = max(ambient_temp - 5, min(current_temp, 100))

        # ===== 6. METRICS TRACKING =====
        # Track energy consumption and carbon
        metrics.add_energy(
            load_kw=compute_power,
            solar_kw=solar_used,
            dt_hours=dt_hours
        )

        # Track cooling energy (all from grid)
        metrics.add_cooling(cooling_power_needed, dt_hours)

        # ===== 7. CHECK DEADLINES =====
        # Check all jobs for deadline violations
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
    """
    Extract job execution timeline from scheduler's jobs.

    Args:
        scheduler: Scheduler instance after simulation

    Returns:
        list: List of dicts with job execution info
    """
    timeline = []

    for job in scheduler.jobs:
        if job.start_hour is not None:  # Job actually ran
            timeline.append({
                'name': job.name,
                'start': job.start_hour,
                'duration': job.duration / 60.0,  # Convert minutes to hours
                'end': job.start_hour + (job.duration / 60.0),
                'priority': job.priority,
                'power_kw': job.power_kw,
                'completed': job.is_done(),
                'deadline_missed': job.penalized
            })

    return timeline


def validate_simulation_results(metrics, time_log, grid_log, solar_log, cooling_log, temp_log):
    """
    Validate simulation results for debugging.

    Returns:
        dict: Validation report with warnings/errors
    """
    report = {
        'valid': True,
        'warnings': [],
        'errors': []
    }

    # Check for zero/empty logs
    if sum(grid_log) == 0 and sum(solar_log) == 0:
        report['errors'].append("No energy consumption recorded - check scheduler")
        report['valid'] = False

    # Check for extreme temperatures
    if max(temp_log) > 80:
        report['warnings'].append(f"Very high temperature: {max(temp_log):.1f}°C")

    # Check cooling activated
    if sum(cooling_log) == 0:
        report['warnings'].append("No cooling activated - check temperature thresholds")

    # Check power persistence
    non_zero_steps = sum(1 for g in grid_log if g > 0)
    if non_zero_steps < 5:
        report['warnings'].append(f"Power only in {non_zero_steps} timesteps - jobs finishing too quickly?")

    return report


if __name__ == "__main__":
    # Test simulation with dummy scheduler
    from baseline_scheduler import BaselineScheduler
    from job import Job

    print("Testing simulation_runner.py...")

    # Create test scheduler with sample jobs
    scheduler = BaselineScheduler()
    scheduler.add_job(Job("TestJob1", power_kw=3, duration_min=120, priority="high"))
    scheduler.add_job(Job("TestJob2", power_kw=2, duration_min=60, priority="medium"))

    # Run simulation
    metrics, time_log, grid_log, solar_log, cooling_log, temp_log = run_simulation(
        scheduler, use_smart_features=False
    )

    # Validate
    report = validate_simulation_results(
        metrics, time_log, grid_log, solar_log, cooling_log, temp_log
    )

    print(f"\nSimulation completed:")
    print(f"  Total grid energy: {metrics.grid_energy:.2f} kWh")
    print(f"  Total solar energy: {metrics.solar_energy:.2f} kWh")
    print(f"  Total cooling: {metrics.cooling_energy:.2f} kWh")
    print(f"  Carbon emissions: {metrics.carbon_kg:.2f} kg CO2")
    print(f"  Max temperature: {max(temp_log):.1f}°C")
    print(f"  Power in {sum(1 for g in grid_log if g > 0)} timesteps")
    print(f"\nValidation: {'✅ PASS' if report['valid'] else '❌ FAIL'}")
    if report['warnings']:
        print("Warnings:", report['warnings'])
    if report['errors']:
        print("Errors:", report['errors'])