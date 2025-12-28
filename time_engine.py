def generate_time_steps():
    total_minutes = 24 * 60
    step = 10
    # return time in fractional hours for easier simulation
    return [t / 60 for t in range(0, total_minutes, step)]
