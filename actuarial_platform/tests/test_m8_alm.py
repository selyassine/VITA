"""
Tests des fonctions pures de M8 (valeur actualisée, duration de Macaulay).

Aucune dépendance de données.
"""
import numpy as np
import pandas as pd

from src.m8_alm.actuarial_functions import (
    discount_factors_from_curve, present_value, macaulay_duration, dollar_duration_gap,
)


def _flat_curve(rate: float, max_maturity: int = 50) -> pd.Series:
    return pd.Series(rate, index=pd.RangeIndex(1, max_maturity + 1, name="maturity"))


def test_discount_factors_zero_at_t0_is_one():
    factors = discount_factors_from_curve(_flat_curve(0.03), horizon=10)
    assert factors[0] == 1.0
    assert factors[-1] < 1.0


def test_present_value_flat_curve_matches_manual_calc():
    cash_flows = np.array([0, 100, 100, 100])  # t=0..3
    pv = present_value(cash_flows, _flat_curve(0.05))
    expected = 100 / 1.05 + 100 / 1.05**2 + 100 / 1.05**3
    assert np.isclose(pv, expected)


def test_zero_coupon_bond_duration_equals_maturity():
    # Un zéro-coupon qui paie 1000 à l'année 10 a une duration EXACTEMENT
    # égale à 10 (un seul flux -> moyenne pondérée triviale).
    cash_flows = np.zeros(11)
    cash_flows[10] = 1000
    duration = macaulay_duration(cash_flows, _flat_curve(0.03))
    assert np.isclose(duration, 10.0)


def test_coupon_bond_duration_less_than_maturity():
    # Une obligation couponnée a toujours une duration < sa maturité
    # (les coupons intermédiaires "rapprochent" la moyenne pondérée)
    maturity = 10
    cash_flows = np.zeros(maturity + 1)
    cash_flows[1:] = 30  # coupon annuel
    cash_flows[maturity] += 1000  # remboursement du principal
    duration = macaulay_duration(cash_flows, _flat_curve(0.03))
    assert 0 < duration < maturity


def test_duration_zero_when_total_pv_is_zero():
    cash_flows = np.zeros(5)
    assert macaulay_duration(cash_flows, _flat_curve(0.03)) == 0.0


def test_higher_coupon_reduces_duration():
    maturity = 10
    low_coupon = np.zeros(maturity + 1)
    low_coupon[1:] = 10
    low_coupon[maturity] += 1000

    high_coupon = np.zeros(maturity + 1)
    high_coupon[1:] = 80
    high_coupon[maturity] += 1000

    curve = _flat_curve(0.03)
    assert macaulay_duration(high_coupon, curve) < macaulay_duration(low_coupon, curve)


def test_dollar_duration_gap_zero_when_matched():
    gap = dollar_duration_gap(asset_value=1000, asset_duration=8,
                               liability_value=1000, liability_duration=8)
    assert gap == 0.0


def test_dollar_duration_gap_positive_when_assets_longer():
    gap = dollar_duration_gap(asset_value=1000, asset_duration=10,
                               liability_value=1000, liability_duration=6)
    assert gap > 0


def test_benefit_only_duration_stays_positive_when_net_cash_flow_would_be_negative():
    """Test de non-régression : reproduit le scénario qui causait une duration
    NÉGATIVE avant correction dans M8 - un flux net (prestations - primes)
    dont la valeur actualisée TOTALE est positive, mais dont la duration
    (moyenne pondérée par le temps) devient négative si la composante
    positive est concentrée tôt (poids temporel faible) et la composante
    négative plus tard (poids temporel élevé, qui tire le numérateur vers
    le bas malgré un montant plus petit en valeur absolue).

    C'est exactement ce qui se produisait avec le flux net agrégé du
    portefeuille réel : primes commerciales fortement surchargées sur les
    produits Temporaire/Prévoyance (net négatif sur une grande partie de la
    durée), compensées par un flux positif de la Vie Entière étalé sur
    plusieurs décennies. La duration des PRESTATIONS SEULES, elle, reste
    toujours bien définie et positive (ce que M8 utilise en pratique).
    """
    curve = _flat_curve(0.02, max_maturity=30)
    horizon = 20

    # Flux net construit pour reproduire le problème : PV totale positive,
    # mais duration négative (voir docstring ci-dessus).
    net_cf = np.zeros(horizon + 1)
    net_cf[0] = 500     # poids temporel nul (t=0), n'affecte pas le numérateur
    net_cf[18] = -100   # poids temporel élevé, tire le numérateur vers le négatif

    net_duration = macaulay_duration(net_cf, curve)
    assert net_duration < 0  # confirme que le problème existe bien pour un flux net

    # En revanche, une composante strictement positive (comme les prestations
    # seules, qui ne peuvent jamais être négatives) reste toujours bien définie
    benefit_only_cf = np.abs(net_cf)  # substitut illustratif d'un flux toujours positif
    benefit_duration = macaulay_duration(benefit_only_cf, curve)
    assert benefit_duration > 0
