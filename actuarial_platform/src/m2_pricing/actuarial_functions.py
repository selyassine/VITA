"""
Fonctions actuarielles pures — calcul de prime pure par équivalence actuarielle.

Séparées volontairement de pricing.py (orchestration) : ces fonctions ne
dépendent d'aucune donnée chargée sur disque, uniquement de tableaux de
probabilités de décès (qx) déjà construits. Elles sont donc testables
unitairement sans HMD, sans portefeuille synthétique, sans rien -
voir tests/test_m2_pricing.py.

Convention actuarielle standard (équivalence des engagements) :
  - Prestations payées en fin d'année de survenance du décès
  - Primes payées en début d'année, tant que l'assuré est en vie (rente immédiate)
  - Prime pure = VAP(prestations) / VAP(primes unitaires) = Ax / äx
"""
from __future__ import annotations

import numpy as np


def survival_curve(qx: np.ndarray, radix: int = 100000) -> np.ndarray:
    """Construit la courbe de survivants l(x) à partir d'une suite de qx.

    qx[t] = probabilité de décès entre l'âge x+t et x+t+1.
    Retourne un array de longueur len(qx)+1 : l[0]=radix, l[t+1]=l[t]*(1-qx[t]).
    """
    if np.any((qx < 0) | (qx > 1)):
        raise ValueError("Toutes les valeurs de qx doivent être comprises entre 0 et 1.")
    lx = np.empty(len(qx) + 1)
    lx[0] = radix
    for t, q in enumerate(qx):
        lx[t + 1] = lx[t] * (1 - q)
    return lx


def actuarial_present_value_benefit(qx: np.ndarray, discount_rate: float,
                                     radix: int = 100000) -> float:
    """VAP unitaire des prestations décès (Ax) : capital de 1 payé en fin d'année de décès."""
    lx = survival_curve(qx, radix)
    v = 1 / (1 + discount_rate)
    deaths = lx[:-1] - lx[1:]                     # nombre de décès pendant l'année t
    discount_factors = v ** np.arange(1, len(qx) + 1)
    return float(np.sum(discount_factors * deaths) / radix)


def actuarial_present_value_annuity_due(qx: np.ndarray, discount_rate: float,
                                         radix: int = 100000) -> float:
    """VAP unitaire d'une rente de 1 versée en début d'année tant que l'assuré est vivant (äx)."""
    lx = survival_curve(qx, radix)
    v = 1 / (1 + discount_rate)
    discount_factors = v ** np.arange(0, len(qx))
    return float(np.sum(discount_factors * lx[:-1]) / radix)


def net_level_premium(qx: np.ndarray, capital: float, discount_rate: float,
                       radix: int = 100000) -> float:
    """Prime pure annuelle nivelée, par équivalence actuarielle : capital * Ax / äx.

    Retourne 0.0 si äx == 0 (ex: qx vide ou survie nulle dès la première période),
    cas limite qui ne devrait pas se produire en pratique mais évite une division
    par zéro silencieuse ailleurs dans le pipeline.
    """
    if len(qx) == 0:
        return 0.0
    ax = actuarial_present_value_annuity_due(qx, discount_rate, radix)
    if ax == 0:
        return 0.0
    Ax = actuarial_present_value_benefit(qx, discount_rate, radix)
    return capital * Ax / ax
