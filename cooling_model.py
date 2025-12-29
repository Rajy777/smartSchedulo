"""
Cooling power calculation for data hub thermal management.

The cooling system activates when hub temperature exceeds threshold.
Cooling power required depends on:
1. Excess temperature above threshold
2. Current computational load (which generates heat)

COP (Coefficient of Performance) represents cooling efficiency:
- Higher COP = more efficient cooling (less energy per kW of cooling)
- COP of 3.0 means 1 kW of electrical power provides 3 kW of cooling
"""

from config import COOLING_FACTOR, TEMP_THRESHOLD, COOLING_COP

# Load-dependent cooling factor (how much cooling scales with compute load)
LOAD_COOLING_FACTOR = 0.05


def cooling_power_kw(hub_temp, compute_load_kw):
    """
    Calculate cooling power required based on temperature and load.

    Physics model:
    - Below threshold: No cooling needed
    - Above threshold: Cooling = (temp_excess * factor + load * factor) / COP

    Args:
        hub_temp (float): Current data hub temperature in °C
        compute_load_kw (float): Current computational power load in kW

    Returns:
        float: Cooling power consumption in kW (electrical power, not cooling capacity)

    Example:
        >>> cooling_power_kw(hub_temp=30, compute_load_kw=8)
        >>> # Hub is 5°C above threshold (30-25)
        >>> # Cooling needed = (0.5 * 5 + 0.05 * 8) / 3.0 = 0.967 kW
    """
    # Input validation
    if hub_temp < 0:
        raise ValueError(f"Invalid hub temperature: {hub_temp}°C")
    if compute_load_kw < 0:
        raise ValueError(f"Invalid compute load: {compute_load_kw} kW")

    # No cooling needed below threshold
    if hub_temp <= TEMP_THRESHOLD:
        return 0.0

    # Calculate excess temperature
    excess_temp = hub_temp - TEMP_THRESHOLD

    # Cooling requirement (before COP adjustment)
    # - Temperature component: proportional to how hot it is
    # - Load component: higher loads need more cooling
    cooling_requirement = (COOLING_FACTOR * excess_temp +
                          LOAD_COOLING_FACTOR * compute_load_kw)

    # Convert to electrical power using COP
    # COP = 3.0 means 1 kW electrical gives 3 kW cooling capacity
    electrical_power = cooling_requirement / COOLING_COP

    return max(0.0, electrical_power)  # Ensure non-negative


def cooling_capacity_kw(electrical_power_kw):
    """
    Calculate cooling capacity from electrical power input.

    Args:
        electrical_power_kw (float): Electrical power to cooling system

    Returns:
        float: Cooling capacity in kW (thermal energy removed)

    Example:
        >>> cooling_capacity_kw(1.0)
        >>> # 1 kW electrical * COP 3.0 = 3.0 kW cooling capacity
    """
    return electrical_power_kw * COOLING_COP