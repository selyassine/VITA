"""
M9 - Fonctions pures : marge technique en fonction du chargement commercial.

Meme principe que M2/M3/M4/M7 : testable sans aucune donnee chargee.

MODELE (hypothese assumee, a documenter dans le memoire) :
Un chargement commercial plus eleve (prime_commerciale = loading * prime_pure,
loading > 1) augmente la marge unitaire par contrat, MAIS augmente aussi le
risque de rachat (l'assure trouve la police moins competitive et resilie plus
tot) - un arbitrage classique en tarification actuarielle. On modelise cet
arbitrage par une fonction de marge unimodale :

    marge(loading) = (loading - 1) * prime_pure * ax * exp(-k * (loading - 1))

ou :
  - (loading - 1) * prime_pure = marge commerciale unitaire annuelle
  - ax = rente de survie actuarielle (VAP d'une rente de 1/an tant que vivant)
    -> convertit une marge annuelle en valeur actualisee sur la duree du contrat
  - exp(-k * (loading-1)) = facteur de persistance : penalise la marge quand
    le chargement s'eloigne de 1 (rachat accru), k = "elasticite rachat-prix"

Cette forme a un OPTIMUM ANALYTIQUE simple (derivee nulle) :
    loading* = 1 + 1/k
independant de prime_pure et ax (consequence du choix d'une elasticite
UNIFORME sur tout le portefeuille - simplification a documenter : une version
plus fine ferait varier k par segment/produit).
"""
from __future__ import annotations

import numpy as np


def margin_per_policy(pure_premium: float, ax: float, loading: float,
                       lapse_elasticity: float) -> float:
    """Marge technique actualisee d'un contrat pour un chargement donne."""
    return (loading - 1) * pure_premium * ax * np.exp(-lapse_elasticity * (loading - 1))


def optimal_loading_closed_form(lapse_elasticity: float) -> float:
    """Chargement optimal analytique (maximise margin_per_policy) : 1 + 1/k."""
    if lapse_elasticity <= 0:
        raise ValueError("lapse_elasticity doit être strictement positif.")
    return 1 + 1 / lapse_elasticity


def clip_to_bounds(value: float, bounds: tuple[float, float]) -> float:
    """Borne une valeur optimale à un intervalle réaliste (config.yaml)."""
    return float(np.clip(value, bounds[0], bounds[1]))
