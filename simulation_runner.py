# simulation_runner.py

from config import SIMULATION_START_HOUR, SIMULATION_END_HOUR, TIME_STEP_MINUTES, IDEAL_TEMP, COOLING_COEFFICIENT
from metrics import Metrics

# Simple ambient temperature model
def ambient_temperature(hour):
    if 6 <= hour <= 18:
        # hot during day, peak at noon
        return 30 + 5 * ((hour - 12)**2)/36
    else:
        return 25

# Simple solar generation model (kW)
def solar_power(hour):
    if 6 <= hour <= 18:
        return max(0, 5 * (1 - abs(hour-12)/6))  # peak 5 kW at noon
    else:
        return 0

# Cooling power (kW)
def cooling_power_kw(temp):
    if temp <= IDEAL_TEMP:
        return 0
    else:
        return (temp - IDEAL_TEMP) * COOLING_COEFFICIENT

def run_simulation(scheduler, smart=True):
    metrics = Metrics()
    time_log = []
    grid_log = []
    solar_log = []
    cooling_log = []
    temp_log = []

    # Build time steps in hours
    current_hour = SIMULATION_START_HOUR
    while current_hour < SIMULATION_END_HOUR:
        # Temperature and solar
        temp = ambient_temperature(current_hour)
        solar = solar_power(current_hour) if smart else 0

        # Schedule jobs
        if smart:
            running_jobs = scheduler.schedule(solar, temp, current_hour)
        else:
            running_jobs = scheduler.schedule(0, temp)

        # Compute power
        grid_power = sum(job.power_kw for job in running_jobs)
        cooling_power = cooling_power_kw(temp)

        # Update metrics
        dt_hours = TIME_STEP_MINUTES / 60
        metrics.add_energy(grid_power, solar, dt_hours)
        metrics.add_cooling_energy(cooling_power, dt_hours)

        # Advance jobs
        for job in running_jobs:
            job.run_step(TIME_STEP_MINUTES)

        # Append logs
        time_log.append(current_hour)
        grid_log.append(grid_power)
        solar_log.append(solar)
        cooling_log.append(cooling_power)
        temp_log.append(temp)

        # Next time step
        current_hour += TIME_STEP_MINUTES / 60

    return metrics, time_log, grid_log, solar_log, cooling_log, temp_log
