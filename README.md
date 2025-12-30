SmartSchedulo ⚡🌱
Thermal-Aware, Cost-Optimized Data Center Scheduling Simulator

SmartSchedulo is a simulation framework that models energy-aware job scheduling in a data-center-like environment.
It compares a baseline scheduler against a smart thermal-aware scheduler to measure improvements in:

Grid energy consumption

Cooling energy usage

Carbon emissions

Total operational cost

SLA (deadline) violations

The system is designed to be extensible, data-driven, and ready for real-world datasets (e.g. Kaggle, CSV, time-series logs).

🔍 Why This Project?
Modern data centers waste energy due to:

Poor thermal awareness

Ignoring solar availability

Rigid scheduling policies

SmartSchedulo explores how intelligent scheduling decisions can reduce:

Energy costs

Carbon footprint

Cooling overhead

— without rewriting core scheduling logic.

🧠 Core Design Philosophy
Schedulers never change.
Only data sources change.

This allows:

Plug-and-play datasets

Realistic experimentation

Reproducible results

🧩 System Architecture
scss
Copy code
Data Sources (Hardcoded / CSV / Kaggle)
        ↓
Simulation Runner
        ↓
Schedulers
(Baseline | Smart Thermal-Aware)
        ↓
Metrics Engine
(Energy, Carbon, Cost, SLA)
        ↓
Dashboard & Experiment Runner
⚙️ Key Components
1️⃣ Schedulers
🔹 BaselineScheduler
Ignores temperature

Ignores solar

Runs jobs greedily

Includes background power load

🔹 SmartScheduler
Thermal-aware (blocks non-critical jobs at high temperature)

Solar-aware (prefers solar availability)

Priority & deadline-aware

Enforces power limits

2️⃣ Thermal & Cooling Model
Ambient temperature varies by time of day

Server temperature evolves using thermal inertia

Cooling power increases with:

Excess temperature

Compute load

This directly affects:

Energy usage

Carbon emissions

Cost

3️⃣ Energy & Carbon Metrics
Tracked during simulation:

Grid energy (kWh)

Solar energy (kWh)

Cooling energy (kWh)

Carbon emissions (kg CO₂)

Deadline violations

Total cost (₹ / unit)

4️⃣ Simulation Engine
The simulation runs in 10-minute time steps over 24 hours:

Job execution

Solar availability

Temperature updates

Cooling decisions

SLA checks

Each run produces:

Time-series logs

Aggregated metrics

5️⃣ Streamlit Dashboard
Interactive UI for:

Adjusting job deadlines

Comparing baseline vs smart scheduler

Visualizing:

Grid energy

Cooling load

Temperature

Carbon emissions

Running batch experiments

6️⃣ Experiment Runner
Runs multiple randomized job scenarios

Compares baseline vs smart scheduler

Reports average cost savings

Designed for statistical evaluation

📊 Example Insights
Smart scheduling can:

Shift workloads to cooler periods

Reduce cooling spikes

Increase solar utilization

Lower total grid dependence

Reduce carbon emissions

📁 Project Structure
bash
Copy code
SmartSchedulo/
│
├── config.py                 # Global constants
├── job.py                    # Job model
├── scheduler.py              # Smart scheduler
├── baseline_scheduler.py     # Baseline scheduler
├── simulation_runner.py      # Core simulation loop
├── metrics.py                # Energy, carbon, cost
│
├── solar_model.py            # Solar generation model
├── temperature_model.py      # Ambient temperature model
├── cooling_model.py          # Cooling power model
│
├── experiment_runner.py      # Batch experiments
├── dashboard.py              # Streamlit dashboard
│
└── README.md
🧪 Current Data Sources
Currently, the simulator uses:

Synthetic solar curves

Rule-based temperature profiles

Randomized or user-defined jobs

This ensures:

Fast experimentation

Full control

No external dependencies

🔌 Planned: Dataset Integration (Kaggle / CSV)
The system is explicitly designed to support external datasets without changing schedulers.

Planned Dataset Types
Users will be able to upload CSVs representing:

Dataset	Example Columns
Solar	time, solar_kw
Temperature	time, ambient_temp
Jobs	job_id, power_kw, duration, deadline, priority
Prices	time, grid_price, carbon_intensity

Planned Integration Flow
sql
Copy code
User Uploads CSV
        ↓
Dataset Loader
        ↓
Time-Indexed Data Provider
        ↓
Simulation Runner
        ↓
Schedulers (UNCHANGED)
Fallback:

If no dataset is provided → use built-in models

Why This Matters
Enables real Kaggle datasets

Supports research & academic evaluation

Allows realistic what-if analysis

Makes the project industry-ready

🚀 Future Roadmap
CSV / Kaggle dataset loader

Dataset validation & schema checks

Multiple scenario comparison

Export results as CSV / JSON

ML-based scheduling (optional)

Real-time pricing models

Paper-ready experiment outputs

🧑‍💻 Tech Stack
Python

Streamlit

Matplotlib

NumPy

Git / GitHub

📌 Status
✅ Core simulation complete
✅ Smart vs baseline comparison working
✅ Dashboard & experiments working
🟡 Dataset integration (next milestone)

📬 Contact / Contributions
This project is under active development.
Dataset ideas, optimization strategies, and scheduling heuristics are welcome.
