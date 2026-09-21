"""
Test d'intégration M11 - vérifie que la projection ORSA s'exécute et produit
une trajectoire cohérente.
"""
import pytest

from src.m1_mortality.loader import load_mortality_rates

HMD_AVAILABLE = True
try:
    load_mortality_rates()
except FileNotFoundError:
    HMD_AVAILABLE = False

pytestmark = pytest.mark.skipif(not HMD_AVAILABLE, reason="HMD non présent")


def test_orsa_projection_has_expected_shape():
    from src.m11_orsa.orsa import orsa_projection
    projection = orsa_projection(horizon_years=3)
    assert len(projection) == 4  # années 0 à 3 inclus
    assert list(projection["year"]) == [0, 1, 2, 3]


def test_orsa_projection_values_are_non_negative():
    from src.m11_orsa.orsa import orsa_projection
    projection = orsa_projection(horizon_years=3)
    assert (projection["best_estimate_eur"] >= 0).all()
    assert (projection["scr_vie_biometrique_eur"] >= 0).all()
    assert (projection["solvency_ratio"] > 0).all()
