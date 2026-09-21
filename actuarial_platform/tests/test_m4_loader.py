"""
Tests du loader EIOPA (M4).

Nécessite les fichiers EIOPA dans data/raw/eiopa/EIOPA_RFR_20260531/.
"""
import pytest

from src.m4_scr.loader import load_base_spot_curve, load_shock_factors, get_shocked_curves

EIOPA_AVAILABLE = True
try:
    load_base_spot_curve()
except FileNotFoundError:
    EIOPA_AVAILABLE = False

pytestmark = pytest.mark.skipif(
    not EIOPA_AVAILABLE, reason="Fichiers EIOPA non présents dans data/raw/eiopa/"
)


def test_base_curve_loaded_for_euro():
    curve = load_base_spot_curve("Euro")
    assert not curve.empty
    assert curve.index.min() == 1
    # Les taux doivent rester dans une fourchette plausible (pas de valeur aberrante)
    assert curve.between(-0.05, 0.15).all()


def test_shock_factors_loaded_and_decreasing_with_maturity():
    shocks = load_shock_factors()
    assert not shocks.empty
    assert {"shock_up", "shock_down"}.issubset(shocks.columns)
    # Les chocs réglementaires sont plus forts à court terme qu'à long terme
    assert shocks["shock_up"].iloc[0] > shocks["shock_up"].iloc[20]
    assert shocks["shock_down"].iloc[0] > shocks["shock_down"].iloc[20]


def test_shocked_curves_consistent_direction():
    curves = get_shocked_curves("Euro")
    # Le choc à la hausse doit toujours donner un taux >= courbe centrale
    assert (curves["spot_shock_up"] >= curves["spot_central"]).all()
    # Le choc à la baisse doit toujours donner un taux <= courbe centrale
    assert (curves["spot_shock_down"] <= curves["spot_central"]).all()


def test_unknown_country_raises_clear_error():
    with pytest.raises(ValueError, match="introuvable"):
        load_base_spot_curve("Atlantis")
