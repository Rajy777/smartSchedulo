"""
Solar power generation model for data hub.

Models photovoltaic generation with realistic diurnal pattern:
- Zero generation at night
- Sinusoidal increase from sunrise to solar noon
- Peak generation at midday (12:00)
- Gradual decrease toward sunset
"""

import math
from config import MAX_SOLAR_KW, SOLAR_EFFICIENCY


# Solar generation hours (can be adjusted seasonally)
SUNRISE_HOUR = 6
SUNSET_HOUR = 18
SOLAR_NOON_HOUR = 12  # Peak generation


def solar_power(hour):
    """
    Calculate available solar power at given hour.

    Model: Sinusoidal generation between sunrise and sunset.
    - 0 kW at night (before sunrise, after sunset)
    - Peak at solar noon (12:00)
    - Gradual ramp up/down following sun position

    Formula: P = MAX_SOLAR_KW * EFFICIENCY * sin(π * (hour - sunrise) / daylight_hours)

    Args:
        hour (float): Hour of day (0-24, can be fractional)

    Returns:
        float: Available solar power in kW

    Example:
        >>> solar_power(6)   # Sunrise
        0.0
        >>> solar_power(12)  # Solar noon (peak)
        6.8  # (8.0 * 0.85)
        >>> solar_power(18)  # Sunset
        0.0
        >>> solar_power(22)  # Night
        0.0
    """
    # Normalize hour to 0-24 range
    hour = hour % 24

    # No solar power outside daylight hours
    if hour < SUNRISE_HOUR or hour > SUNSET_HOUR:
        return 0.0

    # Calculate solar generation using sinusoidal model
    # Maps hour from [6,18] to [0,π] for sine function
    daylight_hours = SUNSET_HOUR - SUNRISE_HOUR
    solar_angle = math.pi * (hour - SUNRISE_HOUR) / daylight_hours

    # Sine naturally peaks at π/2 (midpoint), giving peak at noon
    generation_factor = math.sin(solar_angle)

    # Apply maximum capacity and panel efficiency
    available_power = MAX_SOLAR_KW * SOLAR_EFFICIENCY * generation_factor

    return available_power


def is_solar_available(hour):
    """
    Check if solar power is available at given hour.

    Args:
        hour (float): Hour of day (0-24)

    Returns:
        bool: True if sun is up and generating power
    """
    hour = hour % 24
    return SUNRISE_HOUR <= hour <= SUNSET_HOUR


def peak_solar_power():
    """
    Calculate peak solar generation (at solar noon).

    Returns:
        float: Peak solar power in kW
    """
    return MAX_SOLAR_KW * SOLAR_EFFICIENCY


def total_daily_solar_energy():
    """
    Calculate total solar energy available per day.

    Integrates sinusoidal generation curve over daylight hours.
    Exact integral: (2 * peak * daylight_hours) / π

    Returns:
        float: Total daily solar energy in kWh
    """
    daylight_hours = SUNSET_HOUR - SUNRISE_HOUR
    peak_power = peak_solar_power()

    # Integral of sine over [0,π] = 2
    # Energy = average_power * hours = (2*peak/π) * daylight_hours
    total_energy = (2 * peak_power * daylight_hours) / math.pi

    return total_energy


def get_daily_solar_profile(step_hours=0.5):
    """
    Generate complete daily solar profile for visualization.

    Args:
        step_hours (float): Time step for sampling (default 0.5 hours)

    Returns:
        tuple: (hours, power_kw) - lists for plotting

    Example:
        >>> hours, power = get_daily_solar_profile()
        >>> import matplotlib.pyplot as plt
        >>> plt.plot(hours, power)
        >>> plt.xlabel('Hour of Day')
        >>> plt.ylabel('Solar Power (kW)')
    """
    hours = []
    power = []

    hour = 0.0
    while hour < 24:
        hours.append(hour)
        power.append(solar_power(hour))
        hour += step_hours

    return hours, power


if __name__ == "__main__":
    # Test the solar model
    print("Solar Power Generation Profile")
    print("=" * 70)
    print(f"Configuration:")
    print(f"  Max Capacity: {MAX_SOLAR_KW} kW")
    print(f"  Panel Efficiency: {SOLAR_EFFICIENCY * 100}%")
    print(f"  Peak Generation: {peak_solar_power():.2f} kW")
    print(f"  Sunrise: {SUNRISE_HOUR}:00")
    print(f"  Sunset: {SUNSET_HOUR}:00")
    print(f"  Total Daily Energy: {total_daily_solar_energy():.2f} kWh")
    print("=" * 70)
    print(f"{'Hour':<8} {'Solar Power (kW)':<20} {'Visual':<20}")
    print("-" * 70)

    for h in range(0, 25, 2):
        power = solar_power(h)
        bar_length = int(power / MAX_SOLAR_KW * 30) if power > 0 else 0
        bar = "█" * bar_length
        print(f"{h:02d}:00    {power:<20.2f} {bar}")

    print("-" * 70)