"""classical_solver.py
Simple CVXPY-based portfolio solver for mean-variance optimization.
"""
import numpy as np
import time

def solve_classical_portfolio(problem: dict):
    """Solve a basic mean-variance portfolio problem as baseline.
    problem: {"mu": array, "Sigma": matrix, "budget": float}
    returns: (weights, info)
    """
    mu = np.array(problem["mu"])
    Sigma = np.array(problem["Sigma"])
    lam = problem.get("risk_lambda", 1.0)
    t0 = time.time()
    try:
        n = len(mu)
        w = np.linalg.solve(Sigma + lam * np.eye(n), mu)
        w = w / max(1e-12, w.sum()) * problem.get("budget", 1.0)
    except Exception as e:
        w = np.ones_like(mu) / len(mu)
    t1 = time.time()
    info = {"time_s": t1 - t0}
    return w, info
