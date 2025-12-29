"""
Streamlit Dashboard for Smart Data Hub Energy Scheduler.

Provides interactive visualization of:
- Energy consumption (grid, solar, cooling)
- Temperature management
- Carbon emissions
- Job execution timeline
- Multi-experiment comparison
"""

import streamlit as st
import matplotlib.pyplot as plt
import copy
from job import Job
from scheduler import SmartScheduler
from baseline_scheduler import BaselineScheduler
from simulation_runner import run_simulation
from experiment_runner import run_experiments, summarize, print_detailed_results
from config import TIME_STEP_MINUTES

# Page configuration
st.set_page_config(
    page_title="Smart Scheduler Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🔋 Smart Data Hub Energy Scheduler Dashboard")
st.markdown("Compare **Baseline** vs **Smart** scheduling for energy, carbon, and cost optimization")

# ========================================
# SIDEBAR CONTROLS
# ========================================
st.sidebar.header("⚙️ Configuration")

st.sidebar.subheader("📋 Job Deadlines")
ai_training_deadline = st.sidebar.slider("AI Training Deadline (Hour)", 0, 24, 18)
video_deadline = st.sidebar.slider("Video Processing Deadline (Hour)", 0, 24, 20)
backup_deadline = st.sidebar.slider("Data Backup Deadline (Hour)", 0, 24, 23)

st.sidebar.subheader("🌡️ Temperature Settings")
ideal_temp = st.sidebar.slider("Ideal Hub Temperature (°C)", 20, 30, 25)
thermal_threshold = st.sidebar.slider("Thermal Threshold (°C)", 28, 36, 32)

st.sidebar.subheader("🧪 Experiment Settings")
num_experiments = st.sidebar.slider("Number of Experiments", 1, 20, 10)
random_seed = st.sidebar.number_input("Random Seed (for reproducibility)", value=42, step=1)

# ========================================
# JOB CREATION
# ========================================
def create_jobs():
    """
    Create sample jobs with user-configured deadlines.
    ✅ FIXED: Uses lowercase priorities
    """
    return [
        Job("AI Training", 3.5, 120, "high", deadline_hour=ai_training_deadline),
        Job("Video Processing", 2.0, 60, "medium", deadline_hour=video_deadline),
        Job("Data Backup", 1.2, 90, "low", deadline_hour=backup_deadline),
    ]

# ========================================
# RUN SIMULATIONS
# ========================================
@st.cache_data
def run_comparison_simulation(ai_dl, video_dl, backup_dl):
    """
    Run baseline vs smart simulation with caching.
    ✅ FIXED: Deep copies jobs, correct parameter names
    """
    try:
        # Create jobs
        jobs = [
            Job("AI Training", 3.5, 120, "high", deadline_hour=ai_dl),
            Job("Video Processing", 2.0, 60, "medium", deadline_hour=video_dl),
            Job("Data Backup", 1.2, 90, "low", deadline_hour=backup_dl),
        ]

        # ✅ FIXED: Deep copy jobs for independent simulations
        baseline_jobs = copy.deepcopy(jobs)
        smart_jobs = copy.deepcopy(jobs)

        # Run Baseline
        baseline = BaselineScheduler()
        for job in baseline_jobs:
            baseline.add_job(job)
        base_metrics, time_b, grid_b, solar_b, cooling_b, temp_b = run_simulation(
            baseline,
            use_smart_features=False  # ✅ FIXED: correct parameter name
        )

        # Run Smart
        smart = SmartScheduler()
        for job in smart_jobs:
            smart.add_job(job)
        smart_metrics, time_s, grid_s, solar_s, cooling_s, temp_s = run_simulation(
            smart,
            use_smart_features=True  # ✅ FIXED: correct parameter name
        )

        return (base_metrics, time_b, grid_b, solar_b, cooling_b, temp_b,
                smart_metrics, time_s, grid_s, solar_s, cooling_s, temp_s,
                baseline_jobs, smart_jobs)

    except Exception as e:
        st.error(f"Simulation failed: {str(e)}")
        return None

# Run simulation
sim_results = run_comparison_simulation(ai_training_deadline, video_deadline, backup_deadline)

if sim_results is None:
    st.stop()

(base_metrics, time_b, grid_b, solar_b, cooling_b, temp_b,
 smart_metrics, time_s, grid_s, solar_s, cooling_s, temp_s,
 baseline_jobs, smart_jobs) = sim_results

# ========================================
# METRICS COMPARISON
# ========================================
st.header("📊 Performance Metrics")

# Create 4 columns for key metrics
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "💰 Cost Savings",
        f"₹{base_metrics.total_cost() - smart_metrics.total_cost():.2f}",
        f"{(base_metrics.total_cost() - smart_metrics.total_cost()) / base_metrics.total_cost() * 100:.1f}%"
    )

with col2:
    st.metric(
        "⚡ Grid Energy Saved",
        f"{base_metrics.total_grid_energy() - smart_metrics.total_grid_energy():.2f} kWh",
        f"{(base_metrics.total_grid_energy() - smart_metrics.total_grid_energy()) / base_metrics.total_grid_energy() * 100:.1f}%"
    )

with col3:
    st.metric(
        "🌱 Carbon Reduced",
        f"{base_metrics.carbon_kg - smart_metrics.carbon_kg:.2f} kg CO₂",
        f"{(base_metrics.carbon_kg - smart_metrics.carbon_kg) / base_metrics.carbon_kg * 100:.1f}%"
    )

with col4:
    st.metric(
        "❄️ Cooling Energy Saved",
        f"{base_metrics.cooling_energy - smart_metrics.cooling_energy:.2f} kWh",
        f"{(base_metrics.cooling_energy - smart_metrics.cooling_energy) / base_metrics.cooling_energy * 100:.1f}%" if base_metrics.cooling_energy > 0 else "N/A"
    )

# Detailed metrics table
st.subheader("📋 Detailed Comparison")

col1, col2 = st.columns(2)

with col1:
    st.markdown("**Baseline Scheduler**")
    st.write(f"Total Cost: ₹{base_metrics.total_cost():.2f}")
    st.write(f"Grid Energy: {base_metrics.grid_energy:.2f} kWh")
    st.write(f"Solar Energy: {base_metrics.solar_energy:.2f} kWh")
    st.write(f"Cooling Energy: {base_metrics.cooling_energy:.2f} kWh")
    st.write(f"Total Grid (incl. cooling): {base_metrics.total_grid_energy():.2f} kWh")
    st.write(f"Carbon Emissions: {base_metrics.carbon_kg:.2f} kg CO₂")
    st.write(f"Deadline Violations: {base_metrics.deadline_violations}")

with col2:
    st.markdown("**Smart Scheduler**")
    st.write(f"Total Cost: ₹{smart_metrics.total_cost():.2f}")
    st.write(f"Grid Energy: {smart_metrics.grid_energy:.2f} kWh")
    st.write(f"Solar Energy: {smart_metrics.solar_energy:.2f} kWh")
    st.write(f"Cooling Energy: {smart_metrics.cooling_energy:.2f} kWh")
    st.write(f"Total Grid (incl. cooling): {smart_metrics.total_grid_energy():.2f} kWh")
    st.write(f"Carbon Emissions: {smart_metrics.carbon_kg:.2f} kg CO₂")
    st.write(f"Deadline Violations: {smart_metrics.deadline_violations}")

# ========================================
# ENERGY & POWER VISUALIZATION
# ========================================
st.header("⚡ Energy & Power Analysis")

tab1, tab2, tab3 = st.tabs(["Combined View", "Baseline Only", "Smart Only"])

with tab1:
    fig, ax = plt.subplots(figsize=(14, 6))

    # Baseline
    ax.plot(time_b, grid_b, label="Baseline Grid", color='red', linewidth=2, alpha=0.7)
    ax.plot(time_b, cooling_b, label="Baseline Cooling", color='orange', linestyle=':', linewidth=2, alpha=0.7)

    # Smart
    ax.plot(time_s, grid_s, label="Smart Grid", color='green', linewidth=2, alpha=0.7)
    ax.plot(time_s, cooling_s, label="Smart Cooling", color='blue', linestyle=':', linewidth=2, alpha=0.7)

    # Solar
    ax.plot(time_s, solar_s, label="Solar Available", color='gold', linestyle='--', linewidth=2, alpha=0.9)

    ax.fill_between(time_s, solar_s, alpha=0.2, color='gold', label='Solar Generation')

    ax.set_xlabel("Time (Hours)", fontsize=12)
    ax.set_ylabel("Power (kW)", fontsize=12)
    ax.set_title("Energy & Cooling Over Time - Baseline vs Smart", fontsize=14, fontweight='bold')
    ax.legend(loc='upper right')
    ax.grid(True, alpha=0.3)
    st.pyplot(fig)

with tab2:
    fig, ax = plt.subplots(figsize=(14, 6))
    ax.plot(time_b, grid_b, label="Grid Power", color='red', linewidth=2)
    ax.plot(time_b, cooling_b, label="Cooling Power", color='orange', linewidth=2)
    ax.plot(time_b, solar_b, label="Solar Available", color='gold', linestyle='--', linewidth=2)
    ax.set_xlabel("Time (Hours)", fontsize=12)
    ax.set_ylabel("Power (kW)", fontsize=12)
    ax.set_title("Baseline Scheduler - Power Consumption", fontsize=14, fontweight='bold')
    ax.legend()
    ax.grid(True, alpha=0.3)
    st.pyplot(fig)

with tab3:
    fig, ax = plt.subplots(figsize=(14, 6))
    ax.plot(time_s, grid_s, label="Grid Power", color='green', linewidth=2)
    ax.plot(time_s, cooling_s, label="Cooling Power", color='blue', linewidth=2)
    ax.plot(time_s, solar_s, label="Solar Available", color='gold', linestyle='--', linewidth=2)
    ax.fill_between(time_s, solar_s, alpha=0.2, color='gold')
    ax.set_xlabel("Time (Hours)", fontsize=12)
    ax.set_ylabel("Power (kW)", fontsize=12)
    ax.set_title("Smart Scheduler - Power Consumption", fontsize=14, fontweight='bold')
    ax.legend()
    ax.grid(True, alpha=0.3)
    st.pyplot(fig)

# ========================================
# TEMPERATURE VISUALIZATION
# ========================================
st.header("🌡️ Temperature Management")

fig, ax = plt.subplots(figsize=(14, 5))
ax.plot(time_b, temp_b, label="Baseline Temperature", color='red', linewidth=2)
ax.plot(time_s, temp_s, label="Smart Temperature", color='green', linewidth=2)
ax.axhline(y=ideal_temp, color='blue', linestyle='--', linewidth=2, label=f'Ideal Temp ({ideal_temp}°C)')
ax.axhline(y=thermal_threshold, color='orange', linestyle='--', linewidth=2, label=f'Thermal Threshold ({thermal_threshold}°C)')

ax.fill_between(time_b, ideal_temp, thermal_threshold, alpha=0.2, color='yellow', label='Safe Zone')
ax.fill_between(time_b, thermal_threshold, max(max(temp_b), max(temp_s)) + 2, alpha=0.2, color='red', label='Danger Zone')

ax.set_xlabel("Time (Hours)", fontsize=12)
ax.set_ylabel("Temperature (°C)", fontsize=12)
ax.set_title("Hub Temperature - Baseline vs Smart", fontsize=14, fontweight='bold')
ax.legend(loc='upper right')
ax.grid(True, alpha=0.3)
st.pyplot(fig)

# Temperature statistics
col1, col2 = st.columns(2)
with col1:
    st.markdown("**Baseline Temperature Stats**")
    st.write(f"Average: {sum(temp_b)/len(temp_b):.1f}°C")
    st.write(f"Max: {max(temp_b):.1f}°C")
    st.write(f"Min: {min(temp_b):.1f}°C")

with col2:
    st.markdown("**Smart Temperature Stats**")
    st.write(f"Average: {sum(temp_s)/len(temp_s):.1f}°C")
    st.write(f"Max: {max(temp_s):.1f}°C")
    st.write(f"Min: {min(temp_s):.1f}°C")

# ========================================
# JOB EXECUTION TIMELINE
# ========================================
st.header("📅 Job Execution Timeline")

def plot_job_timeline(baseline_jobs, smart_jobs):
    """
    ✅ FIXED: Shows actual execution timeline based on start_hour
    """
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 6), sharex=True)

    # Baseline timeline
    for i, job in enumerate(baseline_jobs):
        if job.start_hour is not None:
            duration_hr = job.duration / 60
            ax1.barh(i, duration_hr, left=job.start_hour, height=0.8,
                    color='red', alpha=0.7, edgecolor='black')
            ax1.text(job.start_hour + duration_hr/2, i, job.name,
                    ha='center', va='center', fontweight='bold', fontsize=9)

    ax1.set_yticks(range(len(baseline_jobs)))
    ax1.set_yticklabels([job.name for job in baseline_jobs])
    ax1.set_title("Baseline Scheduler", fontweight='bold')
    ax1.set_xlim(0, 24)
    ax1.grid(True, alpha=0.3, axis='x')

    # Smart timeline
    for i, job in enumerate(smart_jobs):
        if job.start_hour is not None:
            duration_hr = job.duration / 60
            color = {'high': 'darkgreen', 'medium': 'orange', 'low': 'lightblue'}[job.priority]
            ax2.barh(i, duration_hr, left=job.start_hour, height=0.8,
                    color=color, alpha=0.7, edgecolor='black')
            ax2.text(job.start_hour + duration_hr/2, i, job.name,
                    ha='center', va='center', fontweight='bold', fontsize=9)

            # Show deadline
            if job.deadline is not None:
                ax2.axvline(x=job.deadline, color='red', linestyle='--', alpha=0.5, linewidth=1)

    ax2.set_yticks(range(len(smart_jobs)))
    ax2.set_yticklabels([job.name for job in smart_jobs])
    ax2.set_xlabel("Time (Hours)", fontsize=12)
    ax2.set_title("Smart Scheduler (color = priority)", fontweight='bold')
    ax2.set_xlim(0, 24)
    ax2.grid(True, alpha=0.3, axis='x')

    plt.tight_layout()
    st.pyplot(fig)

plot_job_timeline(baseline_jobs, smart_jobs)

# ========================================
# MULTI-EXPERIMENT ANALYSIS
# ========================================
st.header("🧪 Multi-Experiment Analysis")

st.markdown(f"""
Run **{num_experiments}** experiments with random job configurations to validate
the smart scheduler's performance across diverse scenarios.
""")

if st.button("🚀 Run Experiments", type="primary"):
    with st.spinner(f"Running {num_experiments} experiments..."):
        # ✅ FIXED: Uses corrected run_experiments with seed
        results = run_experiments(n=num_experiments, seed=int(random_seed))

        # Calculate summary statistics
        cost_savings = [(r["base_cost"] - r["smart_cost"]) / r["base_cost"] * 100
                       for r in results if r["base_cost"] > 0]
        grid_savings = [r["base_grid"] - r["smart_grid"] for r in results]
        carbon_savings = [r["base_carbon"] - r["smart_carbon"] for r in results]

        avg_cost_saving = sum(cost_savings) / len(cost_savings)
        avg_grid_saving = sum(grid_savings) / len(grid_savings)
        avg_carbon_saving = sum(carbon_savings) / len(carbon_savings)

        # Display results
        st.success(f"✅ Completed {num_experiments} experiments!")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Average Cost Savings", f"{avg_cost_saving:.2f}%")
        with col2:
            st.metric("Average Grid Savings", f"{avg_grid_saving:.2f} kWh")
        with col3:
            st.metric("Average Carbon Savings", f"{avg_carbon_saving:.2f} kg CO₂")

        # Plot distribution
        fig, axes = plt.subplots(1, 3, figsize=(15, 4))

        axes[0].hist(cost_savings, bins=10, color='green', alpha=0.7, edgecolor='black')
        axes[0].set_xlabel("Cost Savings (%)")
        axes[0].set_ylabel("Frequency")
        axes[0].set_title("Distribution of Cost Savings")
        axes[0].axvline(avg_cost_saving, color='red', linestyle='--', linewidth=2, label=f'Mean: {avg_cost_saving:.1f}%')
        axes[0].legend()

        axes[1].hist(grid_savings, bins=10, color='blue', alpha=0.7, edgecolor='black')
        axes[1].set_xlabel("Grid Energy Savings (kWh)")
        axes[1].set_ylabel("Frequency")
        axes[1].set_title("Distribution of Grid Savings")
        axes[1].axvline(avg_grid_saving, color='red', linestyle='--', linewidth=2, label=f'Mean: {avg_grid_saving:.1f} kWh')
        axes[1].legend()

        axes[2].hist(carbon_savings, bins=10, color='orange', alpha=0.7, edgecolor='black')
        axes[2].set_xlabel("Carbon Savings (kg CO₂)")
        axes[2].set_ylabel("Frequency")
        axes[2].set_title("Distribution of Carbon Savings")
        axes[2].axvline(avg_carbon_saving, color='red', linestyle='--', linewidth=2, label=f'Mean: {avg_carbon_saving:.1f} kg')
        axes[2].legend()

        plt.tight_layout()
        st.pyplot(fig)

        # Show detailed results table
        with st.expander("📊 View Detailed Results"):
            st.dataframe(results, use_container_width=True)

# ========================================
# FOOTER
# ========================================
st.markdown("---")
st.markdown("""
**Smart Data Hub Energy Scheduler** | Optimizing energy, reducing carbon, managing temperature
""")