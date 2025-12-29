"""
Experiment runner for comparing baseline vs smart scheduler.

Runs multiple experiments with random job sets to quantify:
- Cost savings
- Energy efficiency (grid, solar, cooling)
- Carbon reduction
- SLA compliance
"""

from scheduler import SmartScheduler
from baseline_scheduler import BaselineScheduler
from simulation_runner import run_simulation
from job import Job
import random
import copy


def random_jobs(num_jobs=5, seed=None):
    """
    Generate random jobs with varied characteristics.

    ✅ FIXED:
    - Lowercase priorities ("low", "medium", "high")
    - 30% of jobs have no deadline (more realistic)
    - Optional seed for reproducibility
    """
    if seed is not None:
        random.seed(seed)

    jobs = []
    for i in range(num_jobs):
        # 70% chance of having a deadline
        deadline = random.randint(10, 23) if random.random() > 0.3 else None

        jobs.append(Job(
            name=f"Job-{i}",
            power_kw=round(random.uniform(0.8, 3.5), 2),
            duration_min=random.randint(30, 180),
            priority=random.choice(["low", "medium", "high"]),  # ✅ lowercase
            deadline_hour=deadline
        ))

    return jobs


def run_experiments(n=10, seed=None):
    """
    Run multiple experiments comparing baseline vs smart scheduler.

    ✅ FIXED:
    - Deep copies jobs to avoid state pollution
    - Correct parameter name: use_smart_features
    - Comprehensive metrics tracking
    - Optional seed for reproducibility
    """
    if seed is not None:
        random.seed(seed)

    results = []

    print(f"Running {n} experiments...\n")

    for i in range(n):
        # Generate unique jobs for this experiment
        exp_seed = (seed + i) if seed is not None else None
        jobs = random_jobs(num_jobs=5, seed=exp_seed)

        # ✅ FIXED: Deep copy jobs so each scheduler gets independent instances
        baseline_jobs = copy.deepcopy(jobs)
        smart_jobs = copy.deepcopy(jobs)

        # Create schedulers
        base = BaselineScheduler()
        smart = SmartScheduler()

        # Add jobs to schedulers
        for j in baseline_jobs:
            base.add_job(j)

        for j in smart_jobs:
            smart.add_job(j)

        # ✅ FIXED: Correct parameter name
        base_m, *_ = run_simulation(base, use_smart_features=False)
        smart_m, *_ = run_simulation(smart, use_smart_features=True)

        # ✅ ENHANCED: Track comprehensive metrics
        results.append({
            "base_cost": base_m.total_cost(),
            "smart_cost": smart_m.total_cost(),
            "base_grid": base_m.total_grid_energy(),
            "smart_grid": smart_m.total_grid_energy(),
            "base_solar": base_m.solar_energy,
            "smart_solar": smart_m.solar_energy,
            "base_carbon": base_m.carbon_kg,
            "smart_carbon": smart_m.carbon_kg,
            "base_violations": base_m.deadline_violations,
            "smart_violations": smart_m.deadline_violations,
        })

        # Progress indicator
        if (i + 1) % 5 == 0 or (i + 1) == n:
            print(f"  Completed {i + 1}/{n} experiments")

    print()
    return results


def summarize(results):
    """
    Calculate and display summary statistics.

    ✅ FIXED:
    - Handles division by zero
    - Shows standard deviation
    - Includes all key metrics
    - Better formatting
    """
    if not results:
        print("No results to summarize!")
        return

    n = len(results)

    # Calculate savings with zero-division protection
    cost_savings = []
    for r in results:
        if r["base_cost"] > 0:  # ✅ FIXED: Avoid division by zero
            saving_pct = (r["base_cost"] - r["smart_cost"]) / r["base_cost"] * 100
            cost_savings.append(saving_pct)
        else:
            cost_savings.append(0)

    # Helper function for statistics
    def calc_stats(values):
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        std = variance ** 0.5
        return mean, std, min(values), max(values)

    # Calculate statistics for key metrics
    avg_saving, std_saving, min_saving, max_saving = calc_stats(cost_savings)

    grid_savings = [r["base_grid"] - r["smart_grid"] for r in results]
    avg_grid, std_grid, min_grid, max_grid = calc_stats(grid_savings)

    carbon_savings = [r["base_carbon"] - r["smart_carbon"] for r in results]
    avg_carbon, std_carbon, min_carbon, max_carbon = calc_stats(carbon_savings)

    solar_used = [r["smart_solar"] for r in results]
    avg_solar, std_solar, min_solar, max_solar = calc_stats(solar_used)

    base_violations = [r["base_violations"] for r in results]
    smart_violations = [r["smart_violations"] for r in results]
    avg_base_viol = sum(base_violations) / n
    avg_smart_viol = sum(smart_violations) / n

    # Print formatted summary
    print("=" * 70)
    print("EXPERIMENT SUMMARY")
    print("=" * 70)
    print(f"Number of experiments: {n}\n")

    print("💰 Cost Savings:")
    print(f"  Average: {avg_saving:.2f}%")
    print(f"  Std Dev: {std_saving:.2f}%")
    print(f"  Range: {min_saving:.2f}% to {max_saving:.2f}%\n")

    print("⚡ Grid Energy Savings:")
    print(f"  Average: {avg_grid:.2f} kWh")
    print(f"  Std Dev: {std_grid:.2f} kWh")
    print(f"  Range: {min_grid:.2f} to {max_grid:.2f} kWh\n")

    print("🌱 Carbon Reduction:")
    print(f"  Average: {avg_carbon:.2f} kg CO2")
    print(f"  Std Dev: {std_carbon:.2f} kg")
    print(f"  Range: {min_carbon:.2f} to {max_carbon:.2f} kg\n")

    print("☀️ Solar Energy Utilization:")
    print(f"  Average: {avg_solar:.2f} kWh")
    print(f"  Std Dev: {std_solar:.2f} kWh")
    print(f"  Range: {min_solar:.2f} to {max_solar:.2f} kWh\n")

    print("⏰ SLA Violations:")
    print(f"  Baseline avg: {avg_base_viol:.1f}")
    print(f"  Smart avg: {avg_smart_viol:.1f}")
    print(f"  Reduction: {avg_base_viol - avg_smart_viol:.1f} violations\n")

    print("=" * 70)


def print_detailed_results(results):
    """
    Print detailed table of all experiment results.
    """
    print("\n" + "=" * 70)
    print("DETAILED EXPERIMENT RESULTS")
    print("=" * 70)
    print(f"{'#':<3} {'Base':>8} {'Smart':>8} {'Save%':>7} {'Grid Δ':>9} {'Violations':>12}")
    print(f"{'':3} {'Cost':>8} {'Cost':>8} {'':>7} {'(kWh)':>9} {'(B→S)':>12}")
    print("-" * 70)

    for i, r in enumerate(results):
        cost_save_pct = ((r["base_cost"] - r["smart_cost"]) / r["base_cost"] * 100) if r["base_cost"] > 0 else 0
        grid_delta = r["base_grid"] - r["smart_grid"]

        print(f"{i:<3} "
              f"₹{r['base_cost']:>7.2f} "
              f"₹{r['smart_cost']:>7.2f} "
              f"{cost_save_pct:>6.1f}% "
              f"{grid_delta:>9.2f} "
              f"{r['base_violations']:>5} → {r['smart_violations']:<4}")

    print("=" * 70)


# ✅ Example usage and testing
if __name__ == "__main__":
    print("Smart Data Hub Energy Scheduler - Experiment Runner\n")

    # Run experiments with reproducible seed
    results = run_experiments(n=10, seed=42)

    # Show summary statistics
    summarize(results)

    # Show detailed results
    print_detailed_results(results)

    # Example: Calculate total savings across all experiments
    total_base_cost = sum(r["base_cost"] for r in results)
    total_smart_cost = sum(r["smart_cost"] for r in results)
    total_savings = total_base_cost - total_smart_cost

    print(f"\n📊 AGGREGATE TOTALS:")
    print(f"  Total Baseline Cost: ₹{total_base_cost:.2f}")
    print(f"  Total Smart Cost: ₹{total_smart_cost:.2f}")
    print(f"  Total Savings: ₹{total_savings:.2f} ({total_savings/total_base_cost*100:.1f}%)")