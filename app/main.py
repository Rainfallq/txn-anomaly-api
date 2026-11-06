"""FastAPI application."""

from __future__ import annotations

import os

from fastapi import FastAPI
from pydantic import BaseModel, Field

from . import __version__
from .data import generate_amounts
from .scoring import fit_baseline, is_suspicious, z_score

BASELINE_SIZE = int(os.environ.get("BASELINE_SIZE", "5000"))
SEED = int(os.environ.get("SEED", "42"))
THRESHOLD = float(os.environ.get("THRESHOLD", "3.0"))

app = FastAPI(title="txn-anomaly-api", version=__version__)

# Fixed seed means the baseline is identical on every machine and every run.
baseline = fit_baseline(generate_amounts(BASELINE_SIZE, SEED))


class ScoreRequest(BaseModel):
    amount: float = Field(gt=0, description="Transaction amount, must be positive")


class ScoreResponse(BaseModel):
    amount: float
    z_score: float
    suspicious: bool


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "version": __version__}


@app.get("/baseline")
def get_baseline() -> dict[str, float | int]:
    return {
        "n": baseline.n,
        "mean_log": round(baseline.mean_log, 4),
        "std_log": round(baseline.std_log, 4),
        "threshold": THRESHOLD,
    }


@app.post("/score", response_model=ScoreResponse)
def score(request: ScoreRequest) -> ScoreResponse:
    z = z_score(request.amount, baseline)
    return ScoreResponse(
        amount=request.amount,
        z_score=round(z, 4),
        suspicious=is_suspicious(request.amount, baseline, THRESHOLD),
    )
