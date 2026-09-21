"""
Fonctions pures - Value-at-Risk sur une distribution simulee de Best Estimate.

Meme principe que M2/M3/M4 : aucune dependance de donnees, testable seule.
"""
from __future__ import annotations

import numpy as np


def value_at_risk(distribution: np.ndarray, central: float, confidence: float = 0.995) -> float:
    """VaR a un niveau de confiance donne, definie comme l'ecart entre le
    quantile de la distribution simulee et la valeur centrale (best estimate
    de reference), plafonnee a 0 (une VaR de capital ne peut pas etre negative
    par convention prudente - un scenario favorable ne genere pas de "capital
    negatif", juste une VaR nulle pour ce sous-risque).
    """
    if len(distribution) == 0:
        raise ValueError("La distribution simulee est vide.")
    quantile = np.percentile(distribution, confidence * 100)
    return max(quantile - central, 0.0)


def distribution_summary(distribution: np.ndarray) -> dict:
    """Resume statistique simple d'une distribution simulee de Best Estimate."""
    return {
        "mean": float(np.mean(distribution)),
        "std": float(np.std(distribution)),
        "min": float(np.min(distribution)),
        "p50": float(np.percentile(distribution, 50)),
        "p95": float(np.percentile(distribution, 95)),
        "p99_5": float(np.percentile(distribution, 99.5)),
        "max": float(np.max(distribution)),
    }
