"""
Diagnostic test to identify why metrics are frozen.

Run this standalone to see exactly what's happening.
"""

import copy
from job import Job
from scheduler import SmartScheduler
from baseline_scheduler import BaselineScheduler
from simulation_runner import run_simulation

print("=" * 70)
print("DIAGNOSTIC TEST - Finding Frozen Metrics Issue")
print("=" * 70)

# Create test jobs
print("\n1. Creating jobs...")
jobs = [
    Job("AI Training", 3.5, 120, "high", deadline_hour=18),
    Job("Video Processing", 2.0, 60, "medium", deadline_hour=20),
    Job("Data Backup", 1.2, 90, "low", deadline_hour=23),
]

for job in jobs:
    print(f"   {job.name}: {job.power_kw} kW, {job.duration} min, {job.priority}")

# Deep copy jobs
baseline_jobs = copy.deepcopy(jobs)
smart_jobs = copy.deepcopy(jobs)

print(f"\n2. Job IDs check:")
print(f"   Original job 0: {id(jobs[0])}")
print(f"   Baseline job 0: {id(baseline_jobs[0])}")
print(f"   Smart job 0: {id(smart_jobs[0])}")
print(f"   ✅ All different IDs = deep copy working!" if id(jobs[0]) != id(baseline_jobs[0]) != id(smart_jobs[0]) else "   ❌ SAME IDs = NOT COPYING!")

# Create schedulers
print("\n3. Creating schedulers...")
baseline = BaselineScheduler()
smart = SmartScheduler()

for job in baseline_jobs:
    baseline.add_job(job)

for job in smart_jobs:
    smart.add_job(job)

print(f"   Baseline has {len(baseline.jobs)} jobs")
print(f"   Smart has {len(smart.jobs)} jobs")

# Run baseline simulation
print("\n4. Running BASELINE simulation...")
base_metrics, time_b, grid_b, solar_b, cooling_b, temp_b = run_simulation(
    baseline,
    use_smart_features=False
)

print(f"   ✅ Baseline completed")
print(f"   Grid energy: {base_metrics.grid_energy:.2f} kWh")
print(f"   Solar energy: {base_metrics.solar_energy:.2f} kWh")
print(f"   Cooling energy: {base_metrics.cooling_energy:.2f} kWh")
print(f"   Carbon: {base_metrics.carbon_kg:.2f} kg")
print(f"   Violations: {base_metrics.deadline_violations}")
print(f"   Total cost: ₹{base_metrics.total_cost():.2f}")

# Check job states after baseline
print("\n5. Baseline job states:")
for job in baseline_jobs:
    print(f"   {job.name}: {job.status}, remaining={job.remaining}min")

# Check if smart jobs are still pristine
print("\n6. Smart job states (should still be WAITING):")
for job in smart_jobs:
    print(f"   {job.name}: {job.status}, remaining={job.remaining}min")
    if job.status != "WAITING":
        print(f"   ❌ ERROR: Job already modified before smart simulation!")

# Run smart simulation
print("\n7. Running SMART simulation...")
smart_metrics, time_s, grid_s, solar_s, cooling_s, temp_s = run_simulation(
    smart,
    use_smart_features=True
)

print(f"   ✅ Smart completed")
print(f"   Grid energy: {smart_metrics.grid_energy:.2f} kWh")
print(f"   Solar energy: {smart_metrics.solar_energy:.2f} kWh")
print(f"   Cooling energy: {smart_metrics.cooling_energy:.2f} kWh")
print(f"   Carbon: {smart_metrics.carbon_kg:.2f} kg")
print(f"   Violations: {smart_metrics.deadline_violations}")
print(f"   Total cost: ₹{smart_metrics.total_cost():.2f}")

# Check grid/solar logs
print("\n8. Checking power logs...")
print(f"   Baseline grid log sample (first 10): {grid_b[:10]}")
print(f"   Baseline solar log sample (first 10): {solar_b[:10]}")
print(f"   Smart grid log sample (first 10): {grid_s[:10]}")
print(f"   Smart solar log sample (first 10): {solar_s[:10]}")

# Sum of logs should match metrics
baseline_grid_sum = sum(grid_b) * (10/60)  # 10 min timesteps
baseline_solar_sum = sum(solar_b) * (10/60)
smart_grid_sum = sum(grid_s) * (10/60)
smart_solar_sum = sum(solar_s) * (10/60)

print(f"\n9. Log sum vs Metrics:")
print(f"   Baseline grid: log_sum={baseline_grid_sum:.2f}, metrics={base_metrics.grid_energy:.2f}")
print(f"   Baseline solar: log_sum={baseline_solar_sum:.2f}, metrics={base_metrics.solar_energy:.2f}")
print(f"   Smart grid: log_sum={smart_grid_sum:.2f}, metrics={smart_metrics.grid_energy:.2f}")
print(f"   Smart solar: log_sum={smart_solar_sum:.2f}, metrics={smart_metrics.solar_energy:.2f}")

# Compare results
print("\n" + "=" * 70)
print("COMPARISON")
print("=" * 70)

grid_diff = base_metrics.grid_energy - smart_metrics.grid_energy
solar_diff = smart_metrics.solar_energy - base_metrics.solar_energy
carbon_diff = base_metrics.carbon_kg - smart_metrics.carbon_kg
cost_diff = base_metrics.total_cost() - smart_metrics.total_cost()

print(f"Grid energy difference: {grid_diff:.2f} kWh")
print(f"Solar energy difference: {solar_diff:.2f} kWh")
print(f"Carbon difference: {carbon_diff:.2f} kg")
print(f"Cost difference: ₹{cost_diff:.2f}")

if abs(grid_diff) < 0.1 and abs(solar_diff) < 0.1:
    print("\n❌ PROBLEM DETECTED: Results are nearly identical!")
    print("   Possible causes:")
    print("   1. simulation_runner.py still has grid_log bug")
    print("   2. Smart scheduler not actually using solar")
    print("   3. Jobs not running at all")
else:
    print("\n✅ Results show meaningful differences!")

# Check if solar was actually available
print(f"\n10. Solar availability check:")
print(f"    Hours with solar > 0: {sum(1 for s in solar_s if s > 0)} timesteps")
print(f"    Max solar available: {max(solar_s):.2f} kW")
print(f"    Smart solar usage: {smart_metrics.solar_energy:.2f} kWh")

if smart_metrics.solar_energy < 0.5:
    print("    ❌ Smart scheduler barely using solar!")
    print("    Check: scheduler.py priorities and solar thresholds")

print("\n" + "=" * 70)