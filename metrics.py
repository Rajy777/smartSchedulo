# metrics.py
from config import CARBON_INTENSITY

class Metrics:
    def __init__(self):
        self.grid_energy = 0.0
        self.solar_energy = 0.0
        self.cooling_energy = 0.0

    def add_energy(self, total_power_kw, solar_kw, time_hours):
        if solar_kw >= total_power_kw:
            self.solar_energy += total_power_kw * time_hours
        else:
            self.solar_energy += solar_kw * time_hours
            self.grid_energy += (total_power_kw - solar_kw) * time_hours

    def add_cooling_energy(self, cooling_kw, time_hours):
        self.cooling_energy += cooling_kw * time_hours
        self.grid_energy += cooling_kw * time_hours  # cooling always grid

    def total_grid_energy(self):
        return self.grid_energy

    def total_energy(self):
        return self.grid_energy + self.solar_energy

    # 🔥 NEW: Carbon-aware metric
    def total_carbon_emissions(self):
        return self.grid_energy * CARBON_INTENSITY
