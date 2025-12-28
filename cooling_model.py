from config import IDEAL_TEMP , COOLING_COEFFICIENT

def cooling_power_kw(ambient_temp, compute_power_kw):
    if ambient_temp <= IDEAL_TEMP:
        return 0.0

    delta = ambient_temp - IDEAL_TEMP
    return COOLING_COEFFICIENT*delta*compute_power_kw