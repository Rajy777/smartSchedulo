# time_engine.py

def generate_time_steps():
    time_steps = []
    total_minutes = 24 * 60
    step = 10

    for t in range(0, total_minutes, step):
        hour = t // 60
        minute = t % 60
        time_steps.append((hour, minute))

    return time_steps
