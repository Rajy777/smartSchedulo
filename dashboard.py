"""
Enhanced Dashboard with Dataset Upload Support.

✅ Allows CSV uploads for solar, temperature, jobs
✅ Falls back to hardcoded models if no upload
✅ Shows dataset status clearly
"""

import streamlit as st
import matplotlib.pyplot as plt
import copy
import tempfile
import os
from job import Job
from scheduler import SmartScheduler
from baseline_scheduler import BaselineScheduler
from simulation_runner import run_simulation
from data_adapter import (
    create_solar_source,
    create_temperature_source,
    load_jobs_from_csv
)

# Page configuration
st.set_page_config(
    page_title="Smart Scheduler with Datasets",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🔋 Smart Data Hub Energy Scheduler")
st.markdown("**Enhanced Edition**: Upload real datasets or use built-in models")

# ========================================
# SIDEBAR - DATASET UPLOADS
# ========================================
st.sidebar.header("📁 Dataset Upload")

with st.sidebar.expander("🌞 Solar Power Dataset", expanded=False):
    st.markdown("""
    **Format**: CSV with columns:
    - `hour` (0-24)
    - `solar_kw` (power in kW)

    **Example**:
    ```
    hour,solar_kw
    0,0
    6,1.5
    12,8.0
    18,2.0
    ```
    """)
    solar_file = st.file_uploader("Upload Solar CSV", type=['csv'], key='solar')

with st.sidebar.expander("🌡️ Temperature Dataset", expanded=False):
    st.markdown("""
    **Format**: CSV with columns:
    - `hour` (0-24)
    - `temp_c` (temperature in °C)

    **Example**:
    ```
    hour,temp_c
    0,26
    12,42
    18,35
    ```
    """)
    temp_file = st.file_uploader("Upload Temperature CSV", type=['csv'], key='temp')

with st.sidebar.expander("🧠 Jobs/Workload Dataset", expanded=False):
    st.markdown("""
    **Format**: CSV with columns:
    - `name` (job name)
    - `power_kw` (power consumption)
    - `duration_min` (duration in minutes)
    - `priority` (high/medium/low)
    - `deadline_hour` (optional, 0-24)

    **Example**:
    ```
    name,power_kw,duration_min,priority,deadline_hour
    AI Training,3.5,120,high,18
    Backup,1.2,90,low,23
    ```
    """)
    jobs_file = st.file_uploader("Upload Jobs CSV", type=['csv'], key='jobs')

st.sidebar.markdown("---")

# ========================================
# DATASET STATUS DISPLAY
# ========================================
st.sidebar.subheader("📊 Dataset Status")

solar_status = "✅ CSV Loaded" if solar_file else "🔄 Using Model"
temp_status = "✅ CSV Loaded" if temp_file else "🔄 Using Model"
jobs_status = "✅ CSV Loaded" if jobs_file else "🔄 Using Default"

st.sidebar.markdown(f"""
- **Solar**: {solar_status}
- **Temperature**: {temp_status}
- **Jobs**: {jobs_status}
""")

st.sidebar.markdown("---")

# ========================================
# MANUAL JOB CONFIGURATION (if no CSV)
# ========================================
if not jobs_file:
    st.sidebar.subheader("📋 Manual Job Configuration")
    st.sidebar.info("💡 Set deadlines during solar hours (6-18) for best results!")

    # Job 1
    with st.sidebar.expander("Job 1 Settings", expanded=False):
        job1_power = st.slider("Power (kW)", 1.0, 5.0, 3.5, 0.5, key='j1p')
        job1_duration = st.slider("Duration (min)", 30, 240, 120, 30, key='j1d')
        job1_deadline = st.slider("Deadline (hour)", 0, 24, 14, key='j1dl')
        job1_priority = st.selectbox("Priority", ["high", "medium", "low"], 0, key='j1pr')

    # Job 2
    with st.sidebar.expander("Job 2 Settings", expanded=False):
        job2_power = st.slider("Power (kW)", 1.0, 5.0, 2.5, 0.5, key='j2p')
        job2_duration = st.slider("Duration (min)", 30, 240, 150, 30, key='j2d')
        job2_deadline = st.slider("Deadline (hour)", 0, 24, 16, key='j2dl')
        job2_priority = st.selectbox("Priority", ["high", "medium", "low"], 1, key='j2pr')

    # Job 3
    with st.sidebar.expander("Job 3 Settings", expanded=False):
        job3_power = st.slider("Power (kW)", 1.0, 5.0, 1.5, 0.5, key='j3p')
        job3_duration = st.slider("Duration (min)", 30, 240, 90, 30, key='j3d')
        job3_deadline = st.slider("Deadline (hour)", 0, 24, 20, key='j3dl')
        job3_priority = st.selectbox("Priority", ["high", "medium", "low"], 2, key='j3pr')

# ========================================
# PROCESS UPLOADED DATASETS
# ========================================

# Solar data source
solar_source = None
if solar_file:
    with tempfile.NamedTemporaryFile(delete=False, suffix='.csv', mode='wb') as f:
        f.write(solar_file.getvalue())
        solar_csv_path = f.name
    solar_source = create_solar_source(csv_path=solar_csv_path)
    if not solar_source.is_loaded():
        st.error("❌ Failed to load solar CSV. Using model fallback.")
        solar_source = None
else:
    solar_source = create_solar_source(csv_path=None)

# Temperature data source
temp_source = None
if temp_file:
    with tempfile.NamedTemporaryFile(delete=False, suffix='.csv', mode='wb') as f:
        f.write(temp_file.getvalue())
        temp_csv_path = f.name
    temp_source = create_temperature_source(csv_path=temp_csv_path)
    if not temp_source.is_loaded():
        st.error("❌ Failed to load temperature CSV. Using model fallback.")
        temp_source = None
else:
    temp_source = create_temperature_source(csv_path=None)

# Jobs
jobs = []
if jobs_file:
    with tempfile.NamedTemporaryFile(delete=False, suffix='.csv', mode='wb') as f:
        f.write(jobs_file.getvalue())
        jobs_csv_path = f.name
    try:
        jobs = load_jobs_from_csv(jobs_csv_path)
        st.success(f"✅ Loaded {len(jobs)} jobs from CSV")
    except Exception as e:
        st.error(f"❌ Failed to load jobs CSV: {e}")
        jobs = []
else:
    # Use manual configuration
    jobs = [
        Job("Job 1", job1_power, job1_duration, job1_priority, job1_deadline),
        Job("Job 2", job2_power, job2_duration, job2_priority, job2_deadline),
        Job("Job 3", job3_power, job3_duration, job3_priority, job3_deadline),
    ]

# ========================================
# RUN SIMULATIONS
# ========================================

@st.cache_data(ttl=5)
def run_comparison_with_datasets(_solar_src, _temp_src, _jobs_list):
    """Run simulations with provided data sources."""

    # Deep copy jobs for independent simulations
    baseline_jobs = copy.deepcopy(_jobs_list)
    smart_jobs = copy.deepcopy(_jobs_list)

    # Run Baseline
    baseline = BaselineScheduler()
    for job in baseline_jobs:
        baseline.add_job(job)

    base_metrics, time_b, grid_b, solar_b, cooling_b, temp_b = run_simulation(
        baseline,
        use_smart_features=False,
        solar_source=_solar_src,
        temperature_source=_temp_src
    )

    # Run Smart
    smart = SmartScheduler()
    for job in smart_jobs:
        smart.add_job(job)

    smart_metrics, time_s, grid_s, solar_s, cooling_s, temp_s = run_simulation(
        smart,
        use_smart_features=True,
        solar_source=_solar_src,
        temperature_source=_temp_src
    )

    return (base_metrics, time_b, grid_b, solar_b, cooling_b, temp_b,
            smart_metrics, time_s, grid_s, solar_s, cooling_s, temp_s,
            baseline_jobs, smart_jobs)

# Run simulation
if len(jobs) == 0:
    st.error("❌ No jobs defined! Upload jobs CSV or configure manually.")
    st.stop()

sim_results = run_comparison_with_datasets(solar_source, temp_source, jobs)

(base_metrics, time_b, grid_b, solar_b, cooling_b, temp_b,
 smart_metrics, time_s, grid_s, solar_s, cooling_s, temp_s,
 baseline_jobs, smart_jobs) = sim_results

# ========================================
# METRICS DISPLAY
# ========================================
st.header("📊 Performance Metrics")

col1, col2, col3, col4 = st.columns(4)

with col1:
    cost_diff = base_metrics.total_cost() - smart_metrics.total_cost()
    cost_pct = (cost_diff / base_metrics.total_cost() * 100) if base_metrics.total_cost() > 0 else 0
    st.metric("💰 Cost Savings", f"₹{cost_diff:.2f}", f"{cost_pct:.1f}%")

with col2:
    grid_diff = base_metrics.total_grid_energy() - smart_metrics.total_grid_energy()
    grid_pct = (grid_diff / base_metrics.total_grid_energy() * 100) if base_metrics.total_grid_energy() > 0 else 0
    st.metric("⚡ Grid Saved", f"{grid_diff:.2f} kWh", f"{grid_pct:.1f}%")

with col3:
    carbon_diff = base_metrics.carbon_kg - smart_metrics.carbon_kg
    carbon_pct = (carbon_diff / base_metrics.carbon_kg * 100) if base_metrics.carbon_kg > 0 else 0
    st.metric("🌱 Carbon Reduced", f"{carbon_diff:.2f} kg", f"{carbon_pct:.1f}%")

with col4:
    st.metric("☀️ Solar Used", f"{smart_metrics.solar_energy:.2f} kWh",
              f"{smart_metrics.solar_percentage():.1f}%")

# ========================================
# DETAILED COMPARISON
# ========================================
st.subheader("📋 Detailed Comparison")

col1, col2 = st.columns(2)

with col1:
    st.markdown("**Baseline Scheduler**")
    st.write(f"Total Cost: ₹{base_metrics.total_cost():.2f}")
    st.write(f"Grid Energy: {base_metrics.grid_energy:.2f} kWh")
    st.write(f"Solar Energy: {base_metrics.solar_energy:.2f} kWh")
    st.write(f"Cooling: {base_metrics.cooling_energy:.2f} kWh")
    st.write(f"Carbon: {base_metrics.carbon_kg:.2f} kg CO₂")
    st.write(f"Violations: {base_metrics.deadline_violations}")

with col2:
    st.markdown("**Smart Scheduler**")
    st.write(f"Total Cost: ₹{smart_metrics.total_cost():.2f}")
    st.write(f"Grid Energy: {smart_metrics.grid_energy:.2f} kWh")
    st.write(f"Solar Energy: {smart_metrics.solar_energy:.2f} kWh")
    st.write(f"Cooling: {smart_metrics.cooling_energy:.2f} kWh")
    st.write(f"Carbon: {smart_metrics.carbon_kg:.2f} kg CO₂")
    st.write(f"Violations: {smart_metrics.deadline_violations}")

# ========================================
# VISUALIZATIONS
# ========================================
st.header("⚡ Energy Analysis")

fig, ax = plt.subplots(figsize=(14, 6))
ax.plot(time_b, grid_b, label="Baseline Grid", color='red', linewidth=2, alpha=0.7)
ax.plot(time_s, grid_s, label="Smart Grid", color='green', linewidth=2, alpha=0.7)
ax.plot(time_s, solar_s, label="Solar Used", color='gold', linestyle='--', linewidth=2)
ax.fill_between(time_s, solar_s, alpha=0.2, color='gold')
ax.set_xlabel("Time (Hours)")
ax.set_ylabel("Power (kW)")
ax.set_title("Grid vs Solar - Baseline vs Smart")
ax.legend()
ax.grid(True, alpha=0.3)
st.pyplot(fig)

# Temperature
st.header("🌡️ Temperature Profile")
fig, ax = plt.subplots(figsize=(14, 5))
ax.plot(time_b, temp_b, label="Baseline", color='red', linewidth=2)
ax.plot(time_s, temp_s, label="Smart", color='green', linewidth=2)
ax.set_xlabel("Time (Hours)")
ax.set_ylabel("Temperature (°C)")
ax.set_title("Hub Temperature Over Time")
ax.legend()
ax.grid(True, alpha=0.3)
st.pyplot(fig)

# ========================================
# JOB TIMELINE
# ========================================
st.header("📅 Job Execution Timeline")

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 6), sharex=True)

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

for i, job in enumerate(smart_jobs):
    if job.start_hour is not None:
        duration_hr = job.duration / 60
        color = {'high': 'darkgreen', 'medium': 'orange', 'low': 'lightblue'}[job.priority]
        ax2.barh(i, duration_hr, left=job.start_hour, height=0.8,
                color=color, alpha=0.7, edgecolor='black')
        ax2.text(job.start_hour + duration_hr/2, i, job.name,
                ha='center', va='center', fontweight='bold', fontsize=9)
        if job.deadline is not None:
            ax2.axvline(x=job.deadline, color='red', linestyle='--', alpha=0.5, linewidth=1)

ax2.set_yticks(range(len(smart_jobs)))
ax2.set_yticklabels([job.name for job in smart_jobs])
ax2.set_xlabel("Time (Hours)")
ax2.set_title("Smart Scheduler (color = priority)", fontweight='bold')
ax2.set_xlim(0, 24)
ax2.grid(True, alpha=0.3, axis='x')

plt.tight_layout()
st.pyplot(fig)

# ========================================
# FOOTER
# ========================================
st.markdown("---")
st.markdown("""
**Smart Data Hub Scheduler - Dataset Edition** |
Upload real-world data or use built-in models |
Powered by intelligent scheduling
""")