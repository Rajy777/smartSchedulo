# temperature_model.py

def ambient_temperature(hour):
    if 0 <= hour < 6:
        return 26
    elif 6 <= hour < 12:
        return 32
    elif 12 <= hour < 16:
        return 42
    elif 16 <= hour < 20:
        return 35
    else:
        return 28
