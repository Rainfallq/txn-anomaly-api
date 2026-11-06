import math

import pytest

from app.data import generate_amounts
from app.scoring import Baseline, fit_baseline, is_suspicious, z_score


@pytest.fixture
def baseline():
    return fit_baseline(generate_amounts(5000, seed=42))


def test_fit_baseline_counts_samples(baseline):
    assert baseline.n == 5000


def test_fit_baseline_matches_generator_parameters(baseline):
    # data was generated with mu=3.5 and sigma=1.0
    assert baseline.mean_log == pytest.approx(3.5, abs=0.1)
    assert baseline.std_log == pytest.approx(1.0, abs=0.1)


def test_typical_amount_has_small_z(baseline):
    assert abs(z_score(math.exp(3.5), baseline)) < 0.2


def test_huge_amount_is_suspicious(baseline):
    assert is_suspicious(1_000_000, baseline)


def test_normal_amount_is_not_suspicious(baseline):
    assert not is_suspicious(33.0, baseline)


def test_tiny_amount_is_also_suspicious(baseline):
    assert is_suspicious(0.0001, baseline)


def test_zero_spread_returns_zero():
    assert z_score(10, Baseline(2.0, 0.0, 5)) == 0.0


def test_fit_needs_two_values():
    with pytest.raises(ValueError):
        fit_baseline([5.0])


def test_fit_rejects_non_positive():
    with pytest.raises(ValueError):
        fit_baseline([5.0, -1.0])


def test_z_score_rejects_non_positive(baseline):
    with pytest.raises(ValueError):
        z_score(0, baseline)


def test_threshold_must_be_positive(baseline):
    with pytest.raises(ValueError):
        is_suspicious(10, baseline, threshold=0)
