def ambient_temperature(hour):
    if 0 <= hour < 6:
        return 26.0
    elif 6 <= hour < 12:
        return 32.0
    elif 12 <= hour < 16:
        return 42.0
    elif 16 <= hour < 20:
        return 35.0
    else:
        return 28.0
