"""
Tests des fonctions actuarielles pures de M3 (provisionnement).

Aucune dependance a HMD ou au portefeuille synthetique : qx construits a la
main, comme pour test_m2_pricing.py.
"""
import numpy as np

from src.m3_reserving.actuarial_functions import prospective_reserve, reserve_run_off
from src.m2_pricing.actuarial_functions import net_level_premium


def test_reserve_zero_length_qx_returns_zero():
    assert prospective_reserve(np.array([]), capital=100000, annual_premium=500,
                                discount_rate=0.01) == 0.0


def test_reserve_never_negative():
    # Prime tres elevee (largement superieure au risque) -> VAP primes > VAP engagements
    # -> la provision doit etre plafonnee a 0, jamais negative
    qx = np.full(10, 0.001)
    reserve = prospective_reserve(qx, capital=10000, annual_premium=100000,
                                   discount_rate=0.01)
    assert reserve == 0.0


def test_reserve_at_inception_consistent_with_net_premium():
    # A la souscription (duree residuelle = duree totale), si la prime versee
    # EST la prime pure nivelee (equivalence actuarielle exacte), la provision
    # initiale doit etre quasi nulle (par definition de l'equivalence).
    qx = np.linspace(0.005, 0.03, 15)
    capital = 150_000
    discount_rate = 0.015

    pure_premium = net_level_premium(qx, capital, discount_rate)
    reserve_at_t0 = prospective_reserve(qx, capital, pure_premium, discount_rate)

    assert reserve_at_t0 < 1.0  # quasi nul (tolérance d'arrondi numérique)


def test_reserve_increases_when_premium_below_pure_premium():
    qx = np.linspace(0.005, 0.03, 15)
    capital = 150_000
    discount_rate = 0.015
    pure_premium = net_level_premium(qx, capital, discount_rate)

    reserve_underpriced = prospective_reserve(qx, capital, pure_premium * 0.7, discount_rate)
    assert reserve_underpriced > 0


def test_reserve_run_off_shape_and_terminal_value():
    qx = np.full(10, 0.01)
    capital = 100_000
    premium = net_level_premium(qx, capital, discount_rate=0.01)
    run_off = reserve_run_off(qx, capital, premium, discount_rate=0.01)

    assert len(run_off) == 11  # t=0 à t=10 inclus
    # A la toute derniere date (plus aucune couverture restante), la provision doit être nulle
    assert np.isclose(run_off[-1], 0.0, atol=1e-6)
    assert (run_off >= 0).all()


def test_reserve_run_off_term_product_typically_increases_then_decreases():
    # Profil classique d'un temporaire décès avec prime nivelée : la provision
    # (mathematique de temporisation) croît d'abord (les jeunes années sont
    # sur-tarifées par la prime nivelée) puis redescend vers 0 en fin de contrat.
    qx = np.linspace(0.002, 0.04, 20)  # mortalité croissante avec l'âge
    capital = 200_000
    premium = net_level_premium(qx, capital, discount_rate=0.01)
    run_off = reserve_run_off(qx, capital, premium, discount_rate=0.01)

    max_idx = np.argmax(run_off)
    assert 0 < max_idx < len(run_off) - 1  # le maximum n'est ni au tout début ni à la toute fin
    assert run_off[-1] < run_off[max_idx]  # ça redescend bien vers la fin
