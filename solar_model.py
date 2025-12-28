from config import MAX_SOLAR_KW, SOLAR_EFFICIENCY
import math

def solar_power(hour):
    if 6 <= hour <= 18:
        return MAX_SOLAR_KW * SOLAR_EFFICIENCY * math.sin(
            math.pi * (hour - 6) / 12
        )
    return 0.0
