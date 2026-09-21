"""
M8 - Fonctions pures : valeur actualisee et duration de Macaulay a partir
d'une courbe de taux par maturite.

Meme principe que M2/M3/M4/M7/M9 : testable sans donnee chargee.

Duration de Macaulay : moyenne ponderee des dates de flux, ponderee par la
valeur actualisee de chaque flux. Mesure la sensibilite temporelle d'un actif
ou d'un passif aux mouvements de taux - utilisee ici pour comparer l'actif
et le passif d'un bilan simplifie (voir alm.py pour l'orchestration).

LIMITE ASSUMEE : la duration de Macaulay est definie proprement pour des
flux de signe constant (ex: obligations, flux tous positifs). Appliquee a
un flux NET passif (prestations - primes, qui peut changer de signe selon
les annees), l'interpretation devient approximative - pratique courante en
ALM simplifiee, mais a documenter comme limite methodologique.
"""
from __future__ import annotations

import numpy as np
import pandas as pd


def discount_factors_from_curve(spot_curve: pd.Series, horizon: int) -> np.ndarray:
    """Facteurs d'actualisation DF(0..horizon) à partir d'une courbe de taux
    par maturité (ex: courbe EIOPA). DF(0) = 1 (valeur actuelle immédiate).
    Les maturités au-delà de la courbe disponible sont bornées au dernier
    taux connu (extrapolation plate, hypothèse simplificatrice standard).
    """
    max_maturity = spot_curve.index.max()
    factors = np.empty(horizon + 1)
    factors[0] = 1.0
    for t in range(1, horizon + 1):
        maturity = min(t, max_maturity)
        rate = spot_curve.loc[maturity]
        factors[t] = (1 + rate) ** (-t)
    return factors


def present_value(cash_flows: np.ndarray, spot_curve: pd.Series) -> float:
    """VAP d'un vecteur de flux (indexé par année 0..len-1) via une courbe de taux."""
    discount_factors = discount_factors_from_curve(spot_curve, len(cash_flows) - 1)
    return float(np.sum(cash_flows * discount_factors))


def macaulay_duration(cash_flows: np.ndarray, spot_curve: pd.Series) -> float:
    """Duration de Macaulay d'un vecteur de flux (indexé par année 0..len-1).

    Retourne 0.0 si la valeur actualisée totale est nulle (évite une division
    par zéro ; cas limite qui ne devrait pas se produire en pratique).
    """
    discount_factors = discount_factors_from_curve(spot_curve, len(cash_flows) - 1)
    pv_flows = cash_flows * discount_factors
    total_pv = np.sum(pv_flows)
    if total_pv == 0:
        return 0.0
    years = np.arange(len(cash_flows))
    return float(np.sum(years * pv_flows) / total_pv)


def dollar_duration_gap(asset_value: float, asset_duration: float,
                         liability_value: float, liability_duration: float) -> float:
    """Écart de duration en valeur ("dollar duration gap") : plus pertinent
    qu'un simple écart de duration quand actif et passif ont des montants
    différents. Positif = l'actif est plus sensible aux taux que le passif
    en valeur absolue (risque de perte de surplus si les taux baissent)."""
    return asset_value * asset_duration - liability_value * liability_duration
