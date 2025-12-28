# ==============================
# Simulation Time Configuration
# ==============================
SIMULATION_START_HOUR = 0
SIMULATION_END_HOUR = 24
TIME_STEP_MINUTES = 10   # 10-minute resolution


# ==============================
# Data Hub & Thermal Parameters
# ==============================
IDEAL_TEMP = 25          # °C
MAX_DATA_HUB_POWER = 10  # kW

COOLING_COEFFICIENT = 0.08  # kW cooling per °C above ideal


# ==============================
# Solar Configuration
# ==============================
MAX_SOLAR_CAPACITY_KW = 8.0   # Rooftop solar capacity (kW)
SOLAR_EFFICIENCY = 0.85       # Panel + inverter efficiency


# ==============================
# Thermal Inertia Model
# ==============================
HEAT_ACCUMULATION = 0.02      # °C increase per kW per timestep
COOLING_EFFICIENCY = 0.6      # °C removed per kW cooling
THERMAL_DISSIPATION = 0.05    # Passive heat loss factor


# ==============================
# Carbon & SLA Model
# ==============================
GRID_CARBON_INTENSITY = 0.7   # kg CO₂ per kWh (India avg)
DEADLINE_PENALTY_KWH = 0.5    # Virtual energy penalty per violation
