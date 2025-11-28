"""orchestrator.py
Decision engine and scheduler for hybrid execution.
"""
from dataclasses import dataclass
from typing import Dict, Any
import time

from src.estimators import ResourceEstimator
from src.classical_solver import solve_classical_portfolio
from src.quantum_solver import compile_and_estimate_quantum


@dataclass
class DecisionResult:
    path: str
    reason: str
    metrics: Dict[str, Any]


class Orchestrator:
    def __init__(self, estimator: ResourceEstimator, config: Dict[str, Any] = None):
        self.estimator = estimator
        self.config = config or {}
        # thresholds
        self.min_fidelity = self.config.get("min_fidelity", 0.6)
        self.max_cost = self.config.get("max_cost", 100.0)
        self.max_qubits = self.config.get("max_qubits", 50)

    def decide(self, problem: Dict[str, Any]) -> DecisionResult:
        # Estimate classical baseline
        t0 = time.time()
        classical_sol, classical_info = solve_classical_portfolio(problem)
        classical_time = classical_info.get("time_s", 0.0)

        # Estimate quantum resources
        q_resources = compile_and_estimate_quantum(problem)

        # Decision rule (simple): choose quantum if estimated fidelity and cost are acceptable
        reason = "default to classical"
        if q_resources["qubits"] <= self.max_qubits and q_resources["fidelity"] >= self.min_fidelity and q_resources["estimated_cost"] <= self.max_cost:
            path = "quantum"
            reason = "resource/fidelity/cost within thresholds"
        else:
            path = "classical"
            # optional hybrid detection
            if q_resources["qubits"] <= self.max_qubits and q_resources["fidelity"] >= (self.min_fidelity * 0.8):
                path = "hybrid"
                reason = "quantum useful for subproblem; using hybrid"

        metrics = {
            "classical_time": classical_time,
            "quantum_estimate": q_resources,
        }
        return DecisionResult(path=path, reason=reason, metrics=metrics)
