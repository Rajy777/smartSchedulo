"""
Metrics tracking for data hub simulation.

Tracks all energy consumption, carbon emissions, and SLA penalties.
Used to compare baseline vs smart scheduler performance.
"""

from config import (
    GRID_CARBON_INTENSITY,
    DEADLINE_PENALTY_KWH,
    GRID_PRICE,
    COOLING_PRICE,
    CARBON_PRICE
)


class Metrics:
    """
    Tracks energy, carbon, and cost metrics for simulation.

    Energy accounting:
    - grid_energy: Energy from grid for compute loads (kWh)
    - solar_energy: Energy from solar for compute loads (kWh)
    - cooling_energy: Energy for cooling (always from grid) (kWh)
    - total_grid: grid_energy + cooling_energy (all grid consumption)

    Carbon accounting:
    - carbon_kg: Total CO2 emissions (kg)

    SLA accounting:
    - deadline_violations: Count of missed deadlines
    - deadline_penalty_kwh: Equivalent energy penalty for violations
    """

    def __init__(self):
        # Energy tracking (kWh)
        self.grid_energy = 0.0         # Grid energy for compute loads
        self.solar_energy = 0.0        # Solar energy for compute loads
        self.cooling_energy = 0.0      # Cooling energy (from grid)

        # Carbon tracking (kg CO2)
        self.carbon_kg = 0.0

        # SLA tracking
        self.deadline_violations = 0
        self.deadline_penalty_kwh = 0.0  # Energy-equivalent penalty

    def add_energy(self, load_kw, solar_kw, dt_hours):
        """
        Add energy consumption for compute loads.

        Intelligently splits load between solar and grid:
        - Use solar first (up to available amount)
        - Remainder comes from grid

        Args:
            load_kw (float): Total compute load power in kW
            solar_kw (float): Available solar power in kW
            dt_hours (float): Time step duration in hours
        """
        # How much solar can actually be used
        used_solar = min(load_kw, solar_kw)

        # Remaining load must come from grid
        grid_power = load_kw - used_solar

        # Accumulate energy (power * time)
        self.solar_energy += used_solar * dt_hours
        self.grid_energy += grid_power * dt_hours

        # Grid energy produces carbon emissions
        self.carbon_kg += grid_power * dt_hours * GRID_CARBON_INTENSITY

    def add_cooling(self, cooling_kw, dt_hours):
        """
        Add cooling energy consumption.

        Cooling always comes from grid (not from solar in this model).

        Args:
            cooling_kw (float): Cooling power in kW
            dt_hours (float): Time step duration in hours
        """
        cooling_energy = cooling_kw * dt_hours

        # Track cooling separately for analysis
        self.cooling_energy += cooling_energy

        # Cooling is also grid energy, contributes to carbon
        # Note: This is tracked separately from compute grid_energy
        # Total grid = grid_energy + cooling_energy
        self.carbon_kg += cooling_energy * GRID_CARBON_INTENSITY

    def add_deadline_penalty(self):
        """
        Record a deadline violation (SLA penalty).

        Each violation adds:
        - +1 to violation count
        - Energy-equivalent penalty (for cost calculations)
        """
        self.deadline_violations += 1
        self.deadline_penalty_kwh += DEADLINE_PENALTY_KWH

    def total_grid_energy(self):
        """
        Calculate total grid energy consumption.

        Returns:
            float: Total grid energy (compute + cooling) in kWh
        """
        return self.grid_energy + self.cooling_energy

    def effective_grid_energy(self):
        """
        Calculate effective grid energy including SLA penalties.

        This represents the "cost-equivalent" grid energy when penalties
        are expressed as energy units.

        Returns:
            float: Grid energy + deadline penalties in kWh-equivalent
        """
        return self.total_grid_energy() + self.deadline_penalty_kwh

    def total_energy(self):
        """
        Calculate total energy consumption from all sources.

        Returns:
            float: Total energy (grid + solar + cooling) in kWh
        """
        return self.solar_energy + self.grid_energy + self.cooling_energy

    def solar_percentage(self):
        """
        Calculate percentage of compute load met by solar.

        Returns:
            float: Solar percentage (0-100)
        """
        compute_total = self.solar_energy + self.grid_energy
        if compute_total == 0:
            return 0.0
        return (self.solar_energy / compute_total) * 100

    def grid_cost(self):
        """Calculate cost of grid energy for compute."""
        return self.grid_energy * GRID_PRICE

    def cooling_cost(self):
        """Calculate cost of cooling energy."""
        return self.cooling_energy * COOLING_PRICE

    def carbon_cost(self):
        """Calculate cost of carbon emissions."""
        return self.carbon_kg * CARBON_PRICE

    def penalty_cost(self):
        """Calculate cost of SLA penalties."""
        return self.deadline_penalty_kwh * GRID_PRICE

    def total_cost(self):
        """
        Calculate total operational cost.

        Cost components:
        1. Grid energy for compute (kWh * grid_price)
        2. Cooling energy (kWh * cooling_price)
        3. Carbon emissions (kg * carbon_price)
        4. SLA penalties (kWh-equivalent * grid_price)

        Returns:
            float: Total cost in currency units (₹)
        """
        return (
            self.grid_cost() +
            self.cooling_cost() +
            self.carbon_cost() +
            self.penalty_cost()
        )

    def get_summary(self):
        """
        Get comprehensive metrics summary.

        Returns:
            dict: All metrics organized by category
        """
        return {
            "energy": {
                "solar_kwh": round(self.solar_energy, 2),
                "grid_kwh": round(self.grid_energy, 2),
                "cooling_kwh": round(self.cooling_energy, 2),
                "total_grid_kwh": round(self.total_grid_energy(), 2),
                "total_kwh": round(self.total_energy(), 2),
                "solar_percentage": round(self.solar_percentage(), 1)
            },
            "carbon": {
                "emissions_kg": round(self.carbon_kg, 2)
            },
            "sla": {
                "violations": self.deadline_violations,
                "penalty_kwh": round(self.deadline_penalty_kwh, 2)
            },
            "cost": {
                "grid": round(self.grid_cost(), 2),
                "cooling": round(self.cooling_cost(), 2),
                "carbon": round(self.carbon_cost(), 2),
                "penalties": round(self.penalty_cost(), 2),
                "total": round(self.total_cost(), 2)
            }
        }

    def __repr__(self):
        return (f"Metrics(grid={self.grid_energy:.1f}kWh, "
                f"solar={self.solar_energy:.1f}kWh, "
                f"cooling={self.cooling_energy:.1f}kWh, "
                f"carbon={self.carbon_kg:.1f}kg, "
                f"violations={self.deadline_violations}, "
                f"cost=₹{self.total_cost():.2f})")


if __name__ == "__main__":
    # Test metrics
    print("Testing Metrics...")
    m = Metrics()

    # Simulate some energy usage
    print("\nStep 1: 5 kW load, 3 kW solar available for 0.5 hours")
    m.add_energy(load_kw=5, solar_kw=3, dt_hours=0.5)
    print(f"  Solar used: {3 * 0.5} kWh")
    print(f"  Grid used: {2 * 0.5} kWh")

    print("\nStep 2: 1 kW cooling for 0.5 hours")
    m.add_cooling(cooling_kw=1, dt_hours=0.5)

    print("\nStep 3: 2 deadline violations")
    m.add_deadline_penalty()
    m.add_deadline_penalty()

    print("\n" + "="*60)
    print("METRICS SUMMARY")
    print("="*60)
    summary = m.get_summary()

    print("\nEnergy:")
    for key, val in summary['energy'].items():
        print(f"  {key}: {val}")

    print("\nCarbon:")
    print(f"  emissions_kg: {summary['carbon']['emissions_kg']}")

    print("\nSLA:")
    for key, val in summary['sla'].items():
        print(f"  {key}: {val}")

    print("\nCost Breakdown:")
    for key, val in summary['cost'].items():
        print(f"  {key}: ₹{val}")

    print(f"\n{m}")