from config import GRID_CARBON_INTENSITY, DEADLINE_PENALTY_KWH

class Metrics:
    def __init__(self):
        self.grid_energy = 0.0
        self.solar_energy = 0.0
        self.cooling_energy = 0.0
        self.carbon = 0.0
        self.deadline_penalty = 0.0
        self.deadline_violations = 0

    def add_energy(self, load_kw, solar_kw, dt):
        used_solar = min(load_kw, solar_kw)
        grid = load_kw - used_solar

        self.solar_energy += used_solar * dt
        self.grid_energy += grid * dt
        self.carbon += grid * dt * GRID_CARBON_INTENSITY

    def add_cooling(self, cooling_kw, dt):
        self.cooling_energy += cooling_kw * dt
        self.grid_energy += cooling_kw * dt
        self.carbon += cooling_kw * dt * GRID_CARBON_INTENSITY

    def add_deadline_penalty(self):
        self.deadline_violations += 1
        self.deadline_penalty += DEADLINE_PENALTY_KWH

    def effective_grid_energy(self):
        return self.grid_energy + self.deadline_penalty
