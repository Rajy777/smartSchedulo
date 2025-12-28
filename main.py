from job import Job
from scheduler import SmartScheduler
from baseline_scheduler import BaselineScheduler
from simulation_runner import run_simulation
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use("TkAgg")


def create_jobs():
    return [
                        Job("AI Training", 3.5, 120, "HIGH", deadline=18),
                        Job("Video Processing", 2.0, 60, "MEDIUM", deadline=20),
                        Job("Data Backup", 1.2, 90, "LOW", deadline=23),
 # must finish by 11 PM

    ]


def main():
    # Baseline
    baseline = BaselineScheduler()
    for job in create_jobs():
        baseline.add_job(job)

    base_metrics, time_b, energy_b = run_simulation(baseline, smart=False)

    # Smart
    smart = SmartScheduler()
    for job in create_jobs():
        smart.add_job(job)

    smart_metrics, time_s, energy_s = run_simulation(smart, smart=True)

    print("\n=== COMPARISON REPORT ===")
    print("Baseline Grid Energy:", round(base_metrics.total_grid_energy(), 2), "kWh")
    print("Smart Grid Energy:", round(smart_metrics.total_grid_energy(), 2), "kWh")

    savings = (
        (base_metrics.total_grid_energy() - smart_metrics.total_grid_energy())
        / base_metrics.total_grid_energy()
    ) * 100

    print("Grid Energy Savings:", round(savings, 2), "%")
    print("Baseline Carbon Emissions:",
          round(base_metrics.total_carbon_emissions(), 2), "kg CO2")

    print("Smart Carbon Emissions:",
          round(smart_metrics.total_carbon_emissions(), 2), "kg CO2")

    carbon_saved = (
        base_metrics.total_carbon_emissions()
        - smart_metrics.total_carbon_emissions()
    )

    print("Carbon Saved:", round(carbon_saved, 2), "kg CO2")


    plt.figure()
    plt.plot(time_b, energy_b, label="Baseline")
    plt.plot(time_s, energy_s, label="Smart Scheduler")
    plt.xlabel("Time (Hours)")
    plt.ylabel("Grid Energy (kWh)")
    plt.title("Grid Energy Usage Comparison")
    plt.legend()
    plt.show()


if __name__ == "__main__":
    main()
