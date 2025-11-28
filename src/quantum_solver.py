"""quantum_solver.py
Classiq SDK integration example for the orchestrator.

This module shows two modes:
1. **Live Classiq path** — uses the `classiq` Python SDK to create a Qmod model, synthesize it and query resource estimates / execution. Replace placeholders (API keys, preferences) with real values.
2. **Fallback path** — when the Classiq SDK or credentials are unavailable, we fall back to a lightweight estimator that returns conservative resource estimates.
"""
import os
import logging
from typing import Dict

try:
    # The Classiq SDK package name is `classiq` per Classiq docs
    from classiq import *  # noqa: F401,F403
    CLASSIQ_AVAILABLE = True
except Exception:
    CLASSIQ_AVAILABLE = False

def _fallback_estimate(problem: dict) -> Dict:
    n = len(problem["mu"])
    qubits = min(2 * n, 60)
    depth = max(10, n * 8)
    fidelity = max(0.2, 0.95 - depth * 0.005)
    estimated_cost = depth * 0.6 + qubits * 0.12
    return {
        "qubits": int(qubits),
        "depth": int(depth),
        "fidelity": float(fidelity),
        "estimated_cost": float(estimated_cost),
        "source": "fallback",
    }

def compile_and_estimate_quantum(problem: dict) -> Dict:
    if not CLASSIQ_AVAILABLE:
        logging.warning("Classiq SDK not available — using fallback estimator")
        return _fallback_estimate(problem)

    try:
        @qfunc
        def demo(q: QBit) -> None:
            X(q)
            H(q)

        @qfunc
        def main(q: Output[QBit]) -> None:
            allocate(q)
            demo(q)

        model = create_model(main)
        write_qmod(model, name="portfolio_demo", directory=None)

        synth_opts = {
            "hardware_target": os.environ.get("CLASSIQ_HW_TARGET", "generic"),
            "max_qubits": int(os.environ.get("CLASSIQ_MAX_QUBITS", "80")),
        }

        synthesis = synthesize(model, preferences=synth_opts)

        qubits = getattr(synthesis, "qubits", None) or synthesis.get("qubits", None) or 0
        depth = getattr(synthesis, "depth", None) or synthesis.get("depth", None) or 0

        base_error = float(os.environ.get("CLASSIQ_BASE_ERROR", 0.01))
        fidelity = max(0.0, 1.0 - base_error * max(1, depth))
        estimated_cost = float(os.environ.get("CLASSIQ_COST_PER_DEPTH", 0.5)) * depth + 0.1 * qubits

        return {
            "qubits": int(qubits),
            "depth": int(depth),
            "fidelity": float(fidelity),
            "estimated_cost": float(estimated_cost),
            "source": "classiq_synthesis",
        }

    except Exception as e:
        logging.exception("Classiq synthesis failed — falling back to estimator: %s", e)
        return _fallback_estimate(problem)
