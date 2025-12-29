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

    Args:
        scheduler: Scheduler instance (BaselineScheduler or SmartScheduler)
        use_smart_features (bool): If True, scheduler receives solar/temp info.
                                    If False, scheduler gets dummy values (baseline mode)

    Returns:
        tuple: (metrics, time_log, grid_log, solar_log, cooling_log, temp_log)
            - metrics: Metrics object with cumulative energy/carbon/penalties
            - time_log: List of hour timestamps
            - grid_log: List of grid power usage (kW) at each step
            - solar_log: List of solar power usage (kW) at each step
            - cooling_log: List of cooling power (kW) at each step
            - temp_log: List of hub temperatures (°C) at each step
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

    # Main simulation loop
    while current_hour < SIMULATION_END_HOUR:
        # ===== 1. ENVIRONMENTAL CONDITIONS =====
        ambient_temp = ambient_temperature(current_hour)
        solar_available = solar_power(current_hour)

        # ===== 2. SCHEDULER DECISION =====
        # Smart schedulers get real solar/temp data
        # Baseline schedulers get dummy values (0, 0) so they ignore these factors
        if use_smart_features:
            running_jobs = scheduler.schedule(solar_available, current_temp, current_hour)
        else:
            # Baseline: scheduler doesn't see solar/temp
            running_jobs = scheduler.schedule(0.0, 0.0, current_hour)

        # ===== 3. POWER CALCULATIONS =====
        # Total compute power from running jobs
        compute_power = sum(job.power_kw for job in running_jobs)

        # How much solar can actually be used (limited by available solar)
        solar_used = min(compute_power, solar_available)

        # Grid power = what solar doesn't cover
        grid_power = compute_power - solar_used

        # Cooling power needed based on current temperature
        cooling_power = cooling_power_kw(current_temp, compute_power)

        # ===== 4. THERMAL STATE UPDATE =====
        # Temperature dynamics with correct signs:
        # + heat from compute load
        # - cooling from cooling system (removes heat)
        # - natural dissipation to ambient
        temp_change = (
            HEAT_ACCUMULATION * compute_power          # Heat added by computation
            - COOLING_EFFICIENCY * cooling_power       # Heat removed by cooling
            - THERMAL_DISSIPATION * (current_temp - ambient_temp)  # Natural dissipation
        )
        current_temp += temp_change

        # Sanity check: temperature shouldn't go below ambient or exceed extreme values
        current_temp = max(ambient_temp - 5, min(current_temp, 100))

        # ===== 5. METRICS TRACKING =====
        # Track energy consumption and carbon
        metrics.add_energy(
            load_kw=compute_power,
            solar_kw=solar_used,
            dt_hours=dt_hours
        )

        # Track cooling energy (all from grid)
        metrics.add_cooling(cooling_power, dt_hours)

        # ===== 6. JOB EXECUTION =====
        # Execute one time step for each running job
        for job in running_jobs:
            job.run_step(TIME_STEP_MINUTES, current_hour)

        # Check all jobs for deadline violations
        for job in scheduler.jobs:
            if job.deadline_missed(current_hour):
                metrics.add_deadline_penalty()
                # Note: job.penalized flag is already set inside deadline_missed()

        # ===== 7. LOGGING =====
        time_log.append(current_hour)
        grid_log.append(grid_power)  # FIXED: Log actual grid usage, not total compute
        solar_log.append(solar_used)  # FIXED: Log actual solar usage
        cooling_log.append(cooling_power)
        temp_log.append(current_temp)

        # ===== 8. TIME ADVANCE =====
        current_hour += dt_hours

    return metrics, time_log, grid_log, solar_log, cooling_log, temp_log


def get_job_timeline(scheduler):
    """
    Extract job execution timeline from scheduler's jobs.

    Args:
        scheduler: Scheduler instance after simulation

    Returns:
        list: List of dicts with job execution info:
            [{'name': str, 'start': float, 'duration': float, 'priority': str}, ...]
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

    Args:
        All simulation outputs

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

    # Check metrics consistency
    total_grid_energy = sum(grid_log) * (TIME_STEP_MINUTES / 60.0)
    if abs(metrics.grid_energy - total_grid_energy - metrics.cooling_energy) > 0.1:
        report['warnings'].append("Metrics grid energy doesn't match logs")

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
    print(f"\nValidation: {'✅ PASS' if report['valid'] else '❌ FAIL'}")
    if report['warnings']:
        print("Warnings:", report['warnings'])
    if report['errors']:
        print("Errors:", report['errors'])