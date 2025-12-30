"""
Data Adapter Layer - Abstraction between data sources and simulation.

Provides unified .get(time) interface for:
- CSV datasets (user-uploaded)
- Hardcoded models (fallback)

CRITICAL: This layer ensures simulation code never changes.
"""

import pandas as pd
import numpy as np
from abc import ABC, abstractmethod
from solar_model import solar_power as solar_model_func
from temperature_model import ambient_temperature as temp_model_func


class DataSource(ABC):
    """Abstract base class for all data sources."""

    @abstractmethod
    def get(self, time):
        """
        Get value at given time.

        Args:
            time (float): Hour of day (0-24)

        Returns:
            float: Value at that time
        """
        pass

    @abstractmethod
    def is_loaded(self):
        """Check if data source has actual data."""
        pass


class CSVDataSource(DataSource):
    """
    Data source from CSV file with interpolation.

    Supports:
    - Linear interpolation between data points
    - Cyclic wrapping (hour 24 = hour 0)
    - Fallback to default value if data missing
    """

    def __init__(self, csv_path=None, time_col='hour', value_col='value',
                 fallback_func=None, default_value=0.0):
        """
        Initialize CSV data source.

        Args:
            csv_path (str): Path to CSV file
            time_col (str): Name of time column (e.g., 'hour')
            value_col (str): Name of value column (e.g., 'solar_kw', 'temp_c')
            fallback_func (callable): Function to call if data missing
            default_value (float): Default if no data and no fallback
        """
        self.csv_path = csv_path
        self.time_col = time_col
        self.value_col = value_col
        self.fallback_func = fallback_func
        self.default_value = default_value

        self.data = None
        self.loaded = False

        if csv_path:
            self._load_csv()

    def _load_csv(self):
        """Load and validate CSV data."""
        try:
            df = pd.read_csv(self.csv_path)

            # Validate columns exist
            if self.time_col not in df.columns or self.value_col not in df.columns:
                raise ValueError(f"CSV must contain '{self.time_col}' and '{self.value_col}' columns")

            # Sort by time
            df = df.sort_values(self.time_col)

            # Store as dict for fast lookup
            self.data = dict(zip(df[self.time_col], df[self.value_col]))
            self.times = np.array(sorted(self.data.keys()))
            self.values = np.array([self.data[t] for t in self.times])

            self.loaded = True

        except Exception as e:
            print(f"Warning: Failed to load CSV {self.csv_path}: {e}")
            self.loaded = False

    def get(self, time):
        """
        Get value at given time with interpolation.

        Args:
            time (float): Hour of day (0-24)

        Returns:
            float: Interpolated value
        """
        # Normalize time to 0-24 range
        time = time % 24

        # If no data loaded, use fallback
        if not self.loaded:
            if self.fallback_func:
                return self.fallback_func(time)
            return self.default_value

        # If exact time exists, return it
        if time in self.data:
            return float(self.data[time])

        # Interpolate between nearest points
        return float(np.interp(time, self.times, self.values, period=24))

    def is_loaded(self):
        """Check if CSV data was successfully loaded."""
        return self.loaded


class ModelDataSource(DataSource):
    """
    Data source from hardcoded model function.
    Always available as fallback.
    """

    def __init__(self, model_func):
        """
        Initialize model-based data source.

        Args:
            model_func (callable): Function that takes time and returns value
        """
        self.model_func = model_func

    def get(self, time):
        """Get value from model function."""
        return self.model_func(time)

    def is_loaded(self):
        """Models are always available."""
        return True


class HybridDataSource(DataSource):
    """
    Hybrid source: tries CSV first, falls back to model.
    This is the recommended data source type.
    """

    def __init__(self, csv_source, model_source):
        """
        Initialize hybrid source.

        Args:
            csv_source (CSVDataSource): CSV data source (may be None)
            model_source (ModelDataSource): Model fallback
        """
        self.csv_source = csv_source
        self.model_source = model_source

    def get(self, time):
        """Get value, preferring CSV over model."""
        if self.csv_source and self.csv_source.is_loaded():
            return self.csv_source.get(time)
        return self.model_source.get(time)

    def is_loaded(self):
        """Check if CSV is loaded."""
        return self.csv_source and self.csv_source.is_loaded()


# ==============================================================================
# FACTORY FUNCTIONS - Create data sources for simulation
# ==============================================================================

def create_solar_source(csv_path=None):
    """
    Create solar power data source.

    Args:
        csv_path (str): Path to solar CSV (columns: hour, solar_kw)

    Returns:
        HybridDataSource: Solar power source with fallback
    """
    csv_source = CSVDataSource(
        csv_path=csv_path,
        time_col='hour',
        value_col='solar_kw',
        fallback_func=solar_model_func,
        default_value=0.0
    ) if csv_path else None

    model_source = ModelDataSource(solar_model_func)

    return HybridDataSource(csv_source, model_source)


def create_temperature_source(csv_path=None):
    """
    Create temperature data source.

    Args:
        csv_path (str): Path to temperature CSV (columns: hour, temp_c)

    Returns:
        HybridDataSource: Temperature source with fallback
    """
    csv_source = CSVDataSource(
        csv_path=csv_path,
        time_col='hour',
        value_col='temp_c',
        fallback_func=temp_model_func,
        default_value=25.0
    ) if csv_path else None

    model_source = ModelDataSource(temp_model_func)

    return HybridDataSource(csv_source, model_source)


def create_price_source(csv_path=None, default_price=6.0):
    """
    Create electricity price data source.

    Args:
        csv_path (str): Path to price CSV (columns: hour, price)
        default_price (float): Default price per kWh

    Returns:
        HybridDataSource: Price source with fallback
    """
    csv_source = CSVDataSource(
        csv_path=csv_path,
        time_col='hour',
        value_col='price',
        fallback_func=lambda t: default_price,
        default_value=default_price
    ) if csv_path else None

    model_source = ModelDataSource(lambda t: default_price)

    return HybridDataSource(csv_source, model_source)


def create_carbon_source(csv_path=None, default_intensity=0.7):
    """
    Create carbon intensity data source.

    Args:
        csv_path (str): Path to carbon CSV (columns: hour, carbon_intensity)
        default_intensity (float): Default kg CO2 per kWh

    Returns:
        HybridDataSource: Carbon source with fallback
    """
    csv_source = CSVDataSource(
        csv_path=csv_path,
        time_col='hour',
        value_col='carbon_intensity',
        fallback_func=lambda t: default_intensity,
        default_value=default_intensity
    ) if csv_path else None

    model_source = ModelDataSource(lambda t: default_intensity)

    return HybridDataSource(csv_source, model_source)


# ==============================================================================
# JOB DATASET LOADER
# ==============================================================================

def load_jobs_from_csv(csv_path):
    """
    Load jobs from CSV file.

    Expected columns:
    - name: Job name (string)
    - power_kw: Power consumption (float)
    - duration_min: Duration in minutes (int)
    - priority: Priority level (string: 'high', 'medium', 'low')
    - deadline_hour: Deadline hour (int, optional)

    Args:
        csv_path (str): Path to jobs CSV

    Returns:
        list[Job]: List of Job objects

    Raises:
        ValueError: If CSV format is invalid
    """
    from job import Job

    try:
        df = pd.read_csv(csv_path)

        # Validate required columns
        required_cols = ['name', 'power_kw', 'duration_min', 'priority']
        for col in required_cols:
            if col not in df.columns:
                raise ValueError(f"CSV must contain '{col}' column")

        jobs = []
        for _, row in df.iterrows():
            # Handle optional deadline
            deadline = row.get('deadline_hour', None)
            if pd.isna(deadline):
                deadline = None
            else:
                deadline = int(deadline)

            # Normalize priority to lowercase
            priority = str(row['priority']).lower()

            job = Job(
                name=str(row['name']),
                power_kw=float(row['power_kw']),
                duration_min=int(row['duration_min']),
                priority=priority,
                deadline_hour=deadline
            )
            jobs.append(job)

        return jobs

    except Exception as e:
        raise ValueError(f"Failed to load jobs from {csv_path}: {e}")


# ==============================================================================
# TESTING & VALIDATION
# ==============================================================================

if __name__ == "__main__":
    print("Testing Data Adapter Layer\n")
    print("=" * 70)

    # Test 1: Model-only source
    print("\n1. Testing Model-Only Source")
    solar_model = create_solar_source(csv_path=None)
    print(f"   Hour 12 solar: {solar_model.get(12):.2f} kW")
    print(f"   Is loaded: {solar_model.is_loaded()} (False = using model)")

    # Test 2: Temperature model
    print("\n2. Testing Temperature Model")
    temp_model = create_temperature_source(csv_path=None)
    for hour in [0, 6, 12, 18]:
        print(f"   Hour {hour:02d} temp: {temp_model.get(hour):.1f}°C")

    # Test 3: Create sample CSV and load
    print("\n3. Testing CSV Loading")
    import tempfile
    import os

    # Create temporary CSV
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as f:
        f.write("hour,solar_kw\n")
        f.write("0,0\n")
        f.write("6,1.5\n")
        f.write("12,8.0\n")
        f.write("18,2.0\n")
        temp_csv = f.name

    solar_csv = create_solar_source(csv_path=temp_csv)
    print(f"   CSV loaded: {solar_csv.is_loaded()}")
    print(f"   Hour 12 solar: {solar_csv.get(12):.2f} kW")
    print(f"   Hour 9 solar (interpolated): {solar_csv.get(9):.2f} kW")

    # Cleanup
    os.unlink(temp_csv)

    print("\n" + "=" * 70)
    print("✅ Data Adapter Layer working correctly!")