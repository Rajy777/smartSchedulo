# ========================================
# SIMULATION PARAMETERS
# ========================================
SIMULATION_START_HOUR = 0
SIMULATION_END_HOUR = 24
TIME_STEP_MINUTES = 10

# ========================================
# DATA HUB SPECIFICATIONS
# ========================================
MAX_DATA_HUB_POWER = 10  # kW - Maximum compute power capacity
BASELINE_BACKGROUND_LOAD = 3.0  # kW - Baseline scheduler background load

# ========================================
# TEMPERATURE & THERMAL MODEL
# ========================================
IDEAL_TEMP = 25  # °C - Target operating temperature
THERMAL_THRESHOLD = 32  # °C - Temperature above which low-priority jobs are skipped

# Thermal dynamics (used in temperature_model updates)
HEAT_ACCUMULATION = 0.15  # How much compute power heats the hub
THERMAL_DISSIPATION = 0.05  # Natural cooling rate to ambient
COOLING_EFFICIENCY = 0.6  # How effectively cooling reduces temperature

# ========================================
# COOLING MODEL
# ========================================
TEMP_THRESHOLD = 25  # °C - Temperature above which cooling activates
COOLING_FACTOR = 0.5  # Proportionality constant for cooling calculation
COOLING_COP = 3.0  # Coefficient of Performance (efficiency of cooling system)

# ========================================
# SOLAR ENERGY
# ========================================
MAX_SOLAR_KW = 8.0  # kW - Peak solar generation capacity
SOLAR_EFFICIENCY = 0.85  # Solar panel efficiency factor

# ========================================
# CARBON EMISSIONS
# ========================================
GRID_CARBON_INTENSITY = 0.7  # kg CO2 per kWh from grid

# ========================================
# SLA & PENALTIES
# ========================================
DEADLINE_PENALTY_KWH = 2.0  # kWh - Energy penalty per deadline violation

# ========================================
# COST MODEL (₹ per unit)
# ========================================
GRID_PRICE = 6  # ₹ per kWh
COOLING_PRICE = 6  # ₹ per kWh
CARBON_PRICE = 2  # ₹ per kg CO2