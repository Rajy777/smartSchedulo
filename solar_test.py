"""
Test with jobs scheduled during solar hours to see maximum benefit.
"""

import copy
from job import Job
from scheduler import SmartScheduler
from baseline_scheduler import BaselineScheduler
from simulation_runner import run_simulation

print("=" * 70)
print("SOLAR-OPTIMIZED TEST")
print("=" * 70)

# Create jobs with deadlines during/after solar hours
# Solar available: 6 AM - 6 PM (hours 6-18)
jobs = [
    Job("Morning Batch", 2.5, 180, "medium", deadline_hour=14),  # Should use solar
    Job("Midday Analysis", 3.0, 120, "medium", deadline_hour=16),  # Should use solar
    Job("Afternoon Report", 1.5, 90, "low", deadline_hour=20),  # Can use solar
    Job("Critical Task", 2.0, 60, "high", deadline_hour=12),  # High priority
]

print("\nJobs configured for solar hours (6 AM - 6 PM):")
for job in jobs:
    print(f"  {job.name}: {job.power_kw} kW, {job.duration} min, "
          f"{job.priority}, deadline={job.deadline}h")

# Deep copy
baseline_jobs = copy.deepcopy(jobs)
smart_jobs = copy.deepcopy(jobs)

# Create schedulers
baseline = BaselineScheduler()
smart = SmartScheduler()

for job in baseline_jobs:
    baseline.add_job(job)

for job in smart_jobs:
    smart.add_job(job)

# Run simulations
print("\n" + "=" * 70)
print("BASELINE SIMULATION")
print("=" * 70)

base_metrics, time_b, grid_b, solar_b, cooling_b, temp_b = run_simulation(
    baseline,
    use_smart_features=False
)

print(f"Grid energy: {base_metrics.grid_energy:.2f} kWh")
print(f"Solar energy: {base_metrics.solar_energy:.2f} kWh")
print(f"Cooling: {base_metrics.cooling_energy:.2f} kWh")
print(f"Carbon: {base_metrics.carbon_kg:.2f} kg")
print(f"Cost: ₹{base_metrics.total_cost():.2f}")
print(f"Violations: {base_metrics.deadline_violations}")

print("\n" + "=" * 70)
print("SMART SIMULATION")
print("=" * 70)

smart_metrics, time_s, grid_s, solar_s, cooling_s, temp_s = run_simulation(
    smart,
    use_smart_features=True
)

print(f"Grid energy: {smart_metrics.grid_energy:.2f} kWh")
print(f"Solar energy: {smart_metrics.solar_energy:.2f} kWh")
print(f"Cooling: {smart_metrics.cooling_energy:.2f} kWh")
print(f"Carbon: {smart_metrics.carbon_kg:.2f} kg")
print(f"Cost: ₹{smart_metrics.total_cost():.2f}")
print(f"Violations: {smart_metrics.deadline_violations}")

# Calculate savings
print("\n" + "=" * 70)
print("SAVINGS ANALYSIS")
print("=" * 70)

grid_saved = base_metrics.grid_energy - smart_metrics.grid_energy
solar_increase = smart_metrics.solar_energy - base_metrics.solar_energy
carbon_saved = base_metrics.carbon_kg - smart_metrics.carbon_kg
cost_saved = base_metrics.total_cost() - smart_metrics.total_cost()

print(f"Grid energy saved: {grid_saved:.2f} kWh ({grid_saved/base_metrics.grid_energy*100:.1f}%)")
print(f"Solar energy used: {solar_increase:.2f} kWh more")
print(f"Carbon reduced: {carbon_saved:.2f} kg ({carbon_saved/base_metrics.carbon_kg*100:.1f}%)")
print(f"Cost saved: ₹{cost_saved:.2f} ({cost_saved/base_metrics.total_cost()*100:.1f}%)")

# Analyze power distribution
print("\n" + "=" * 70)
print("POWER DISTRIBUTION ANALYSIS")
print("=" * 70)

baseline_power_hours = sum(1 for g in grid_b if g > 0) / 6  # Convert timesteps to hours
smart_power_hours = sum(1 for g in grid_s if g > 0) / 6
solar_hours = sum(1 for s in solar_s if s > 0) / 6

print(f"Baseline power active for: {baseline_power_hours:.1f} hours")
print(f"Smart power active for: {smart_power_hours:.1f} hours")
print(f"Solar utilized for: {solar_hours:.1f} hours")
print(f"Max solar available: {max(solar_s):.2f} kW")

# Show hourly breakdown
print("\n" + "=" * 70)
print("HOURLY POWER BREAKDOWN (kW)")
print("=" * 70)
print(f"{'Hour':<6} {'Base Grid':<12} {'Smart Grid':<12} {'Smart Solar':<12} {'Solar Avail':<12}")
print("-" * 70)

for i in range(0, len(time_s), 6):  # Show every hour
    hour = int(time_s[i])
    if hour < 24:
        print(f"{hour:02d}:00  "
              f"{grid_b[i]:<12.2f} "
              f"{grid_s[i]:<12.2f} "
              f"{solar_s[i]:<12.2f} "
              f"{solar_b[i]:<12.2f}")

print("=" * 70)

# Check if smart is actually better
if cost_saved > 0:
    print("\n✅ SUCCESS: Smart scheduler is saving money!")
    print(f"   Total savings: ₹{cost_saved:.2f} ({cost_saved/base_metrics.total_cost()*100:.1f}%)")
else:
    print("\n❌ PROBLEM: Smart scheduler NOT saving money!")
    print("   Check: scheduler priorities, solar thresholds, job timing")