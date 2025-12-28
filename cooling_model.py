from config import IDEAL_TEMP, COOLING_COEFFICIENT

def cooling_power_kw(current_temp):
    """
    Returns cooling power (kW) required to bring temperature
    toward IDEAL_TEMP.
    """
    if current_temp <= IDEAL_TEMP:
        return 0.0

    return (current_temp - IDEAL_TEMP) * COOLING_COEFFICIENT
