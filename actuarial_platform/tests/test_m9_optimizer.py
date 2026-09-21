"""
Tests des fonctions pures de M9 (optimisation du chargement).

Aucune dépendance de données.
"""
import numpy as np
import pytest

from src.m9_optimizer.actuarial_functions import (
    margin_per_policy, optimal_loading_closed_form, clip_to_bounds,
)


def test_margin_zero_at_loading_one():
    # Sans chargement (loading=1, prime = prime pure), la marge doit être nulle
    assert margin_per_policy(pure_premium=1000, ax=10, loading=1.0, lapse_elasticity=0.5) == 0.0


def test_margin_positive_for_loading_above_one():
    m = margin_per_policy(pure_premium=1000, ax=10, loading=1.5, lapse_elasticity=0.5)
    assert m > 0


def test_closed_form_matches_numeric_grid_search():
    for elasticity in [0.2, 0.5, 1.0, 2.0]:
        closed_form_optimum = optimal_loading_closed_form(elasticity)
        upper_bound = closed_form_optimum + 2.0  # marge pour bien encadrer l'optimum
        loadings = np.linspace(1.0001, upper_bound, 200_000)
        margins = margin_per_policy(pure_premium=1000, ax=10, loading=loadings,
                                     lapse_elasticity=elasticity)
        numeric_optimum = loadings[np.argmax(margins)]
        assert np.isclose(numeric_optimum, closed_form_optimum, atol=1e-3)


def test_higher_elasticity_gives_lower_optimal_loading():
    # Plus le rachat est sensible au prix (k élevé), plus le chargement optimal est bas
    low_elasticity_loading = optimal_loading_closed_form(0.3)
    high_elasticity_loading = optimal_loading_closed_form(1.5)
    assert high_elasticity_loading < low_elasticity_loading


def test_optimal_loading_rejects_non_positive_elasticity():
    with pytest.raises(ValueError):
        optimal_loading_closed_form(0.0)
    with pytest.raises(ValueError):
        optimal_loading_closed_form(-0.5)


def test_clip_to_bounds():
    assert clip_to_bounds(5.0, (1.0, 3.0)) == 3.0
    assert clip_to_bounds(0.5, (1.0, 3.0)) == 1.0
    assert clip_to_bounds(2.0, (1.0, 3.0)) == 2.0


def test_margin_scales_linearly_with_pure_premium_and_ax():
    m1 = margin_per_policy(pure_premium=1000, ax=10, loading=1.5, lapse_elasticity=0.5)
    m2 = margin_per_policy(pure_premium=2000, ax=10, loading=1.5, lapse_elasticity=0.5)
    m3 = margin_per_policy(pure_premium=1000, ax=20, loading=1.5, lapse_elasticity=0.5)
    assert np.isclose(m2, 2 * m1)
    assert np.isclose(m3, 2 * m1)
