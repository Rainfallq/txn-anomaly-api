"""Scoring logic: how unusual is an amount compared with a baseline?"""

from __future__ import annotations

import math
import statistics
from dataclasses import dataclass


@dataclass(frozen=True)
class Baseline:
    mean_log: float
    std_log: float
    n: int


def fit_baseline(amounts: list[float]) -> Baseline:
    """Learn mean and spread of log amounts from historical data."""
    if len(amounts) < 2:
        raise ValueError("need at least 2 amounts to fit a baseline")
    if any(a <= 0 for a in amounts):
        raise ValueError("amounts must be positive")
    logs = [math.log(a) for a in amounts]
    return Baseline(statistics.fmean(logs), statistics.stdev(logs), len(logs))


def z_score(amount: float, baseline: Baseline) -> float:
    """Distance from the typical amount, measured in standard deviations."""
    if amount <= 0:
        raise ValueError("amount must be positive")
    if baseline.std_log == 0:
        return 0.0
    return (math.log(amount) - baseline.mean_log) / baseline.std_log


def is_suspicious(amount: float, baseline: Baseline, threshold: float = 3.0) -> bool:
    """True when the amount is far from normal, in either direction."""
    if threshold <= 0:
        raise ValueError("threshold must be positive")
    return abs(z_score(amount, baseline)) > threshold
