"""
Tests des fonctions SCR pures de M4.

Aucune dependance a EIOPA ou a M1/M3 : ces tests s'executent toujours.
"""
import numpy as np
import pytest

from src.m4_scr.scr_functions import (
    scr_submodule,
    aggregate_scr_life,
    solvency_ratio,
    SCR_LIFE_CORRELATION_MATRIX,
)


def test_scr_submodule_positive_when_shock_increases_reserve():
    assert scr_submodule(best_estimate_central=1000, best_estimate_shocked=1200) == 200


def test_scr_submodule_never_negative():
    # Choc favorable (BE choqué < BE central) -> SCR nul, jamais négatif
    assert scr_submodule(best_estimate_central=1000, best_estimate_shocked=800) == 0.0


def test_correlation_matrix_is_symmetric():
    assert np.allclose(SCR_LIFE_CORRELATION_MATRIX, SCR_LIFE_CORRELATION_MATRIX.T)


def test_correlation_matrix_diagonal_is_one():
    assert np.allclose(np.diag(SCR_LIFE_CORRELATION_MATRIX), 1.0)


def test_aggregate_scr_single_risk_equals_itself():
    # Un seul risque actif -> l'agrégation doit redonner exactement sa valeur
    result = aggregate_scr_life({"mortality": 500})
    assert np.isclose(result, 500)


def test_aggregate_scr_two_uncorrelated_risks_pythagorean():
    # lapse et catastrophe ont une corrélation de 0.25 dans la matrice standard,
    # donc ce n'est PAS un cas Pythagore pur - on vérifie juste la formule brute
    scr_dict = {"lapse": 300, "catastrophe": 400}
    corr = 0.25
    expected = np.sqrt(300**2 + 400**2 + 2 * corr * 300 * 400)
    result = aggregate_scr_life(scr_dict)
    assert np.isclose(result, expected)


def test_aggregate_scr_missing_risks_treated_as_zero():
    result_full = aggregate_scr_life({"mortality": 500, "longevity": 0, "disability": 0,
                                        "lapse": 0, "expense": 0, "revision": 0, "catastrophe": 0})
    result_partial = aggregate_scr_life({"mortality": 500})
    assert np.isclose(result_full, result_partial)


def test_solvency_ratio_basic():
    assert np.isclose(solvency_ratio(own_funds=1_500_000, scr=1_000_000), 1.5)


def test_solvency_ratio_zero_scr_is_infinite():
    assert solvency_ratio(own_funds=1_000_000, scr=0) == float("inf")


# --- Tests du choc de taux avec courbe (indépendants de toute donnée EIOPA) ---

def _flat_curve(rate: float, max_maturity: int = 50):
    import pandas as pd
    return pd.Series(rate, index=pd.RangeIndex(1, max_maturity + 1, name="maturity"))


def test_curve_reserve_matches_flat_rate_reserve_when_curve_is_flat():
    """Test de cohérence critique : une courbe plate à x% doit donner exactement
    le même résultat que M3 avec un taux technique plat à x% - sinon les deux
    moteurs de calcul (M3 flat-rate, M4 courbe) ne seraient pas cohérents entre
    eux, ce qui invaliderait la comparaison SCR de taux vs Best Estimate central.
    """
    from src.m4_scr.scr import prospective_reserve_with_curve
    from src.m3_reserving.actuarial_functions import prospective_reserve

    qx = np.linspace(0.005, 0.03, 15)
    capital = 150_000
    premium = 2000
    rate = 0.015

    reserve_m3 = prospective_reserve(qx, capital, premium, discount_rate=rate)
    reserve_m4 = prospective_reserve_with_curve(qx, capital, premium, _flat_curve(rate))

    assert np.isclose(reserve_m3, reserve_m4, rtol=1e-6)


def test_curve_reserve_higher_rate_gives_lower_reserve():
    from src.m4_scr.scr import prospective_reserve_with_curve

    qx = np.linspace(0.005, 0.03, 15)
    capital = 150_000
    premium = 2000

    reserve_low_rate = prospective_reserve_with_curve(qx, capital, premium, _flat_curve(0.01))
    reserve_high_rate = prospective_reserve_with_curve(qx, capital, premium, _flat_curve(0.05))

    assert reserve_high_rate <= reserve_low_rate


def test_curve_reserve_zero_length_qx_returns_zero():
    from src.m4_scr.scr import prospective_reserve_with_curve
    assert prospective_reserve_with_curve(np.array([]), 100000, 500, _flat_curve(0.02)) == 0.0
