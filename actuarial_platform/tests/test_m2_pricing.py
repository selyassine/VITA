"""
Tests des fonctions actuarielles pures de M2.

Aucune dépendance à HMD, EIOPA ou au portefeuille synthétique : ces tests
s'exécutent toujours, avec des qx construits à la main, pour valider la
mathématique actuarielle indépendamment de toute donnée réelle.
"""
import numpy as np
import pytest

from src.m2_pricing.actuarial_functions import (
    survival_curve,
    actuarial_present_value_benefit,
    actuarial_present_value_annuity_due,
    net_level_premium,
)


def test_survival_curve_basic():
    qx = np.array([0.1, 0.1, 0.1])
    lx = survival_curve(qx, radix=1000)
    assert lx[0] == 1000
    assert np.isclose(lx[1], 900)
    assert np.isclose(lx[2], 810)
    assert np.isclose(lx[3], 729)


def test_survival_curve_rejects_invalid_qx():
    with pytest.raises(ValueError):
        survival_curve(np.array([0.1, 1.5, 0.1]))
    with pytest.raises(ValueError):
        survival_curve(np.array([-0.1, 0.1]))


def test_survival_curve_zero_mortality_stays_constant():
    qx = np.zeros(5)
    lx = survival_curve(qx, radix=1000)
    assert np.allclose(lx, 1000)


def test_annuity_due_with_zero_discount_and_zero_mortality_equals_duration():
    # Sans actualisation et sans mortalité, äx = durée (chaque versement vaut 1)
    qx = np.zeros(10)
    ax = actuarial_present_value_annuity_due(qx, discount_rate=0.0)
    assert np.isclose(ax, 10.0)


def test_benefit_value_with_certain_death_first_year():
    # Décès certain en fin de première année (qx[0]=1) -> Ax = v^1 * 1 = v
    qx = np.array([1.0])
    discount_rate = 0.05
    Ax = actuarial_present_value_benefit(qx, discount_rate)
    assert np.isclose(Ax, 1 / 1.05)


def test_net_level_premium_zero_length_qx_returns_zero():
    assert net_level_premium(np.array([]), capital=100000, discount_rate=0.01) == 0.0


def test_net_level_premium_scales_linearly_with_capital():
    qx = np.array([0.01, 0.012, 0.015, 0.02])
    p1 = net_level_premium(qx, capital=100000, discount_rate=0.02)
    p2 = net_level_premium(qx, capital=200000, discount_rate=0.02)
    assert np.isclose(p2, 2 * p1)


def test_net_level_premium_increases_with_mortality():
    qx_low = np.full(10, 0.005)
    qx_high = np.full(10, 0.05)
    p_low = net_level_premium(qx_low, capital=100000, discount_rate=0.01)
    p_high = net_level_premium(qx_high, capital=100000, discount_rate=0.01)
    assert p_high > p_low


def test_net_level_premium_positive_and_reasonable():
    # Cas réaliste : homme de 50 ans, qx croissant doucement sur 20 ans, capital 200k€
    qx = np.linspace(0.003, 0.02, 20)
    premium = net_level_premium(qx, capital=200_000, discount_rate=0.01)
    assert premium > 0
    # La prime pure annuelle ne doit pas dépasser le capital assuré (garde-fou grossier)
    assert premium < 200_000
