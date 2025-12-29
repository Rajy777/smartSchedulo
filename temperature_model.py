"""
Ambient temperature model for data hub environment.

Provides realistic diurnal (daily) temperature variation.
Temperature follows a sinusoidal pattern peaking in early afternoon.
"""

import math


# Temperature profile configuration (°C)
MIN_AMBIENT_TEMP = 26.0  # Night/early morning minimum
MAX_AMBIENT_TEMP = 42.0  # Afternoon maximum
PEAK_TEMP_HOUR = 14.0    # Hour when temperature peaks (2 PM)


def ambient_temperature(hour):
    """
    Calculate ambient temperature at given hour using sinusoidal model.

    Models realistic diurnal temperature variation:
    - Minimum around 6 AM (sunrise)
    - Maximum around 2 PM (early afternoon)
    - Smooth transitions throughout the day

    Args:
        hour (float): Hour of day (0-24, can be fractional)

    Returns:
        float: Ambient temperature in °C

    Example:
        >>> ambient_temperature(6)   # Early morning
        26.5
        >>> ambient_temperature(14)  # Peak afternoon
        42.0
        >>> ambient_temperature(20)  # Evening
        33.2
    """
    # Normalize hour to 0-24 range (handle wrapping)
    hour = hour % 24

    # Sinusoidal model: temp peaks at PEAK_TEMP_HOUR
    # Phase shift so minimum is ~12 hours before peak
    avg_temp = (MIN_AMBIENT_TEMP + MAX_AMBIENT_TEMP) / 2
    amplitude = (MAX_AMBIENT_TEMP - MIN_AMBIENT_TEMP) / 2

    # Convert to radians, phase-shifted so peak is at PEAK_TEMP_HOUR
    phase = (hour - PEAK_TEMP_HOUR) * (2 * math.pi / 24)

    # Sinusoidal temperature
    temp = avg_temp + amplitude * math.cos(phase)

    return temp


def ambient_temperature_stepped(hour):
    """
    Calculate ambient temperature using stepped approximation.
    Less realistic but simpler, matches your original implementation.

    Args:
        hour (float): Hour of day (0-24)

    Returns:
        float: Ambient temperature in °C
    """
    hour = hour % 24

    if 0 <= hour < 6:
        return 26.0  # Night
    elif 6 <= hour < 12:
        return 32.0  # Morning
    elif 12 <= hour < 16:
        return 42.0  # Hot afternoon
    elif 16 <= hour < 20:
        return 35.0  # Evening
    else:
        return 28.0  # Late evening


def get_daily_temperature_profile(step_hours=0.5):
    """
    Generate complete daily temperature profile for visualization.

    Args:
        step_hours (float): Time step for sampling (default 0.5 hours = 30 min)

    Returns:
        tuple: (hours, temperatures) - lists for plotting

    Example:
        >>> hours, temps = get_daily_temperature_profile()
        >>> import matplotlib.pyplot as plt
        >>> plt.plot(hours, temps)
    """
    hours = []
    temps = []

    hour = 0.0
    while hour < 24:
        hours.append(hour)
        temps.append(ambient_temperature(hour))
        hour += step_hours

    return hours, temps


if __name__ == "__main__":
    # Test and compare models
    print("Temperature Profile Comparison:")
    print("-" * 60)
    print(f"{'Hour':<8} {'Smooth Model':<15} {'Stepped Model':<15}")
    print("-" * 60)

    test_hours = [0, 3, 6, 9, 12, 14, 16, 18, 20, 23]
    for h in test_hours:
        smooth = ambient_temperature(h)
        stepped = ambient_temperature_stepped(h)
        print(f"{h:<8} {smooth:<15.1f} {stepped:<15.1f}")

    print("-" * 60)
    print(f"\nMin temp: {MIN_AMBIENT_TEMP}°C")
    print(f"Max temp: {MAX_AMBIENT_TEMP}°C")
    print(f"Peak hour: {PEAK_TEMP_HOUR}:00")