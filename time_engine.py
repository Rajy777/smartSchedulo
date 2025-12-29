"""
Time step generation for simulation loop.

Generates hourly time points based on simulation configuration.
Used by simulation_runner to iterate through the day.
"""

from config import (
    SIMULATION_START_HOUR,
    SIMULATION_END_HOUR,
    TIME_STEP_MINUTES
)


def generate_time_steps():
    """
    Generate time steps for the simulation based on config settings.

    Returns:
        list[float]: List of time points in hours (e.g., [0.0, 0.167, 0.333, ...])

    Example:
        With TIME_STEP_MINUTES=10, SIMULATION_START_HOUR=0, SIMULATION_END_HOUR=24:
        >>> steps = generate_time_steps()
        >>> len(steps)  # 24 hours * 60 min/hr / 10 min/step = 144 steps
        144
        >>> steps[:3]
        [0.0, 0.16666666666666666, 0.3333333333333333]
    """
    # Calculate total simulation duration in minutes
    total_hours = SIMULATION_END_HOUR - SIMULATION_START_HOUR
    total_minutes = total_hours * 60

    # Generate time points in minutes, then convert to hours
    time_steps = []
    for t_min in range(0, total_minutes, TIME_STEP_MINUTES):
        # Convert minutes to hours and add start offset
        t_hour = SIMULATION_START_HOUR + (t_min / 60.0)
        time_steps.append(t_hour)

    return time_steps


def get_num_steps():
    """
    Calculate total number of simulation steps.

    Returns:
        int: Number of time steps in simulation

    Example:
        >>> get_num_steps()  # 24 hours * 60 / 10 minutes
        144
    """
    total_hours = SIMULATION_END_HOUR - SIMULATION_START_HOUR
    total_minutes = total_hours * 60
    return total_minutes // TIME_STEP_MINUTES


def minutes_to_hours(minutes):
    """
    Convert minutes to hours.

    Args:
        minutes (float): Time in minutes

    Returns:
        float: Time in hours
    """
    return minutes / 60.0


def hours_to_minutes(hours):
    """
    Convert hours to minutes.

    Args:
        hours (float): Time in hours

    Returns:
        float: Time in minutes
    """
    return hours * 60.0


if __name__ == "__main__":
    # Test the function
    steps = generate_time_steps()
    print(f"Generated {len(steps)} time steps")
    print(f"First 5 steps: {steps[:5]}")
    print(f"Last 5 steps: {steps[-5:]}")
    print(f"Time step interval: {steps[1] - steps[0]:.4f} hours ({TIME_STEP_MINUTES} minutes)")