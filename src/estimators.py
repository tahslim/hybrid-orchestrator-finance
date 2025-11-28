"""estimators.py
Lightweight cost/fidelity estimator utilities.
"""

class ResourceEstimator:
    def __init__(self, hw_profile: dict = None):
        self.hw = hw_profile or {"qubit_limit": 60, "base_error_rate": 0.01}

    def estimate(self, qubits: int, depth: int):
        base = self.hw["base_error_rate"]
        logical_fidelity = max(0.0, 1.0 - base * depth)
        estimated_cost = 0.2 * qubits + 0.5 * depth
        return {"fidelity": logical_fidelity, "estimated_cost": estimated_cost}
