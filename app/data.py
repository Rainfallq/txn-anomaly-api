"""Data helpers: synthetic transactions and CSV loading."""

from __future__ import annotations

import csv
import random
from pathlib import Path


def generate_amounts(n: int, seed: int = 42) -> list[float]:
    """Make n fake transaction amounts. Same seed gives the same list.

    Real payment amounts are skewed (many small ones, a few huge ones), so a
    log normal distribution is a reasonable simple choice.
    """
    if n <= 0:
        raise ValueError("n must be positive")
    rng = random.Random(seed)
    return [round(rng.lognormvariate(mu=3.5, sigma=1.0), 2) for _ in range(n)]


def load_amounts_from_csv(path: str | Path, column: str = "amount") -> list[float]:
    """Read one numeric column from a CSV file. Bad rows are skipped."""
    amounts: list[float] = []
    with open(path, newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None or column not in reader.fieldnames:
            raise ValueError(f"column '{column}' not found in {path}")
        for row in reader:
            try:
                value = float(row[column])
            except (TypeError, ValueError):
                continue
            if value > 0:
                amounts.append(value)
    if not amounts:
        raise ValueError("no valid amounts found")
    return amounts
