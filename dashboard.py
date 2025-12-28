# full_dashboard.py

import streamlit as st
import matplotlib.pyplot as plt
from job import Job
from scheduler import SmartScheduler
from baseline_scheduler import BaselineScheduler
from simulation_runner import run_simulation

st.set_page_config(page_title="Smart Scheduler Dashboard", layout="wide")
st.title("Smart Scheduler Energy, Carbon & Cooling Dashboard")

# Sidebar: Job deadlines
st.sidebar.header("Job Settings")
ai_training_deadline = st.sidebar.slider("AI Training Deadline (Hour)", 0, 24, 18)
video_deadline = st.sidebar.slider("Video Processing Deadline (Hour)", 0, 24, 20)
backup_deadline = st.sidebar.slider("Data Backup Deadline (Hour)", 0, 24, 23)

# Sidebar: Cooling control
st.sidebar.header("Cooling Settings")
ideal_temp = st.sidebar.slider("Ideal Hub Temperature (°C)", 20, 30, 25)

# Job creation
def create_jobs():
    return [
        Job("AI Training", 3.5, 120, "HIGH", deadline=ai_training_deadline),
        Job("Video Processing", 2.0, 60, "MEDIUM", deadline=video_deadline),
        Job("Data Backup", 1.2, 90, "LOW", deadline=backup_deadline),
    ]

# Run Baseline
baseline = BaselineScheduler()
for job in create_jobs():
    baseline.add_job(job)
base_metrics, time_b, grid_b, solar_b, cooling_b, temp_b = run_simulation(baseline, smart=False)

# Run Smart Scheduler
smart = SmartScheduler()
for job in create_jobs():
    smart.add_job(job)
smart_metrics, time_s, grid_s, solar_s, cooling_s, temp_s = run_simulation(smart, smart=True)

# Display Metrics
st.subheader("Energy & Carbon Comparison")
st.write(f"**Baseline Grid Energy:** {base_metrics.total_grid_energy():.2f} kWh")
st.write(f"**Smart Grid Energy:** {smart_metrics.total_grid_energy():.2f} kWh")
st.write(f"**Grid Energy Savings:** {(base_metrics.total_grid_energy() - smart_metrics.total_grid_energy()) / base_metrics.total_grid_energy() * 100:.2f} %")
st.write(f"**Baseline Carbon Emissions:** {base_metrics.total_carbon_emissions():.2f} kg CO2")
st.write(f"**Smart Carbon Emissions:** {smart_metrics.total_carbon_emissions():.2f} kg CO2")
st.write(f"**Carbon Saved:** {base_metrics.total_carbon_emissions() - smart_metrics.total_carbon_emissions():.2f} kg CO2")
st.write(f"**Baseline Cooling Energy:** {sum(cooling_b):.2f} kWh")
st.write(f"**Smart Cooling Energy:** {sum(cooling_s):.2f} kWh")

# Energy Plots
st.subheader("Energy & Temperature Over Time")
fig, ax = plt.subplots(figsize=(12,6))
ax.plot(time_b, grid_b, label="Baseline Grid Energy")
ax.plot(time_s, grid_s, label="Smart Grid Energy")
ax.plot(time_b, solar_b, label="Solar Power", linestyle='--')
ax.plot(time_b, cooling_b, label="Baseline Cooling", linestyle=':')
ax.plot(time_s, cooling_s, label="Smart Cooling", linestyle='-.')
ax.set_xlabel("Time (Hours)")
ax.set_ylabel("Power (kW)")
ax.set_title("Energy & Cooling Over Time")
ax.legend()
st.pyplot(fig)

# Temperature Plot
st.subheader("Hub Temperature Over Time")
fig2, ax2 = plt.subplots(figsize=(12,4))
ax2.plot(time_b, temp_b, label="Baseline Temp")
ax2.plot(time_s, temp_s, label="Smart Temp")
ax2.axhline(y=ideal_temp, color='r', linestyle='--', label='Ideal Temp')
ax2.set_xlabel("Time (Hours)")
ax2.set_ylabel("Temperature (°C)")
ax2.set_title("Data Hub Temperature")
ax2.legend()
st.pyplot(fig2)

# Job Timeline
st.subheader("Job Execution Timeline")
def plot_job_timeline(jobs):
    fig, ax = plt.subplots(figsize=(12,4))
    for i, job in enumerate(jobs):
        start = 0
        duration = job.total_time / 60  # minutes to hours
        ax.broken_barh([(start, duration)], (i*10, 9), facecolors=('tab:blue'))
        ax.text(start + duration/2, i*10 + 4, job.name, ha='center', va='center', color='white')
    ax.set_yticks([i*10 + 4.5 for i in range(len(jobs))])
    ax.set_yticklabels([job.name for job in jobs])
    ax.set_xlabel("Time (Hours)")
    ax.set_title("Job Execution Timeline (Simplified)")
    st.pyplot(fig)

plot_job_timeline(create_jobs())
