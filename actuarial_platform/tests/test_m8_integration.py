"""
Tests d'intégration M8 - cohérence comptable du bilan ALM.

Nécessite HMD + EIOPA (les deux sources réelles utilisées par M8).
"""
import numpy as np
import pytest

from src.m1_mortality.loader import load_mortality_rates
from src.m4_scr.loader import load_base_spot_curve

DATA_AVAILABLE = True
try:
    load_mortality_rates()
    load_base_spot_curve()
except FileNotFoundError:
    DATA_AVAILABLE = False

pytestmark = pytest.mark.skipif(
    not DATA_AVAILABLE, reason="HMD et/ou EIOPA non présents"
)


def test_nav_equals_assets_minus_liabilities():
    from src.m8_alm.alm import compute_full_alm_report
    report = compute_full_alm_report()
    expected_nav = report["total_asset_value_central"] - report["liability_value_central"]
    assert np.isclose(report["nav_central"], expected_nav, rtol=1e-6)


def test_total_assets_equals_sum_of_components():
    from src.m8_alm.alm import compute_full_alm_report
    report = compute_full_alm_report()
    expected_total = (
        report["bond_value_central"] + report["equities_value"] + report["real_estate_value"]
    )
    assert np.isclose(report["total_asset_value_central"], expected_total, rtol=1e-6)


def test_bond_portfolio_matches_target_coverage():
    from src.common.config_loader import load_config
    from src.m8_alm.alm import compute_full_alm_report
    cfg = load_config()
    allocation = cfg["m8_alm"]["allocation"]
    report = compute_full_alm_report()
    target_bond_value = (
        report["liability_value_central"] * cfg["m8_alm"]["target_coverage_ratio"] * allocation["bonds"]
    )
    # La calibration du notional est exacte (mise à l'échelle linéaire), donc
    # la VAP obligataire doit correspondre de très près à la cible
    assert np.isclose(report["bond_value_central"], target_bond_value, rtol=1e-4)


def test_all_durations_are_positive():
    from src.m8_alm.alm import compute_full_alm_report
    report = compute_full_alm_report()
    # La duration du passif est désormais basée sur les prestations seules
    # (toujours positive par construction) - voir docstring de alm.py pour
    # la justification (la duration du flux net pouvait devenir instable).
    assert report["liability_duration"] > 0
    assert report["premium_duration"] > 0
    assert report["bond_duration"] > 0


def test_all_balance_sheet_values_are_positive():
    """Régression : la valeur du passif (et donc, en cascade, celle des
    actifs calibrés dessus) est devenue négative avant correction, quand le
    passif était calculé en agrégeant les flux bruts plutôt qu'en réutilisant
    le plafonnement par contrat de M4 (voir README, note méthodologique M8).
    """
    from src.m8_alm.alm import compute_full_alm_report
    report = compute_full_alm_report()
    assert report["liability_value_central"] > 0
    assert report["bond_value_central"] > 0
    assert report["equities_value"] > 0
    assert report["real_estate_value"] > 0
    assert report["total_asset_value_central"] > 0
