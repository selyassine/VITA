"""
Tests des fonctions pures de M7 (VaR sur distribution simulée).

Aucune dépendance à HMD ou au portefeuille : distributions construites à la main.
"""
import numpy as np
import pytest

from src.m7_longevity.actuarial_functions import value_at_risk, distribution_summary


def test_value_at_risk_basic():
    # Distribution uniforme 0..1000 (1001 points) -> percentile 99.5% ≈ 995
    distribution = np.arange(0, 1001)
    var = value_at_risk(distribution, central=500, confidence=0.995)
    assert np.isclose(var, 495, atol=2)


def test_value_at_risk_floored_at_zero():
    # Si le quantile est en dessous du central (distribution très favorable),
    # la VaR doit être plafonnée à 0, jamais négative.
    distribution = np.full(100, 10.0)  # constante, quantile == central
    var = value_at_risk(distribution, central=50.0, confidence=0.995)
    assert var == 0.0


def test_value_at_risk_empty_distribution_raises():
    with pytest.raises(ValueError):
        value_at_risk(np.array([]), central=100.0)


def test_value_at_risk_increases_with_confidence():
    rng = np.random.default_rng(0)
    distribution = rng.normal(1000, 200, size=5000)
    var_95 = value_at_risk(distribution, central=1000, confidence=0.95)
    var_995 = value_at_risk(distribution, central=1000, confidence=0.995)
    assert var_995 >= var_95


def test_distribution_summary_keys_and_ordering():
    distribution = np.arange(1, 101)  # 1..100
    summary = distribution_summary(distribution)
    assert summary["min"] <= summary["p50"] <= summary["p95"] <= summary["p99_5"] <= summary["max"]
    assert np.isclose(summary["mean"], 50.5)
