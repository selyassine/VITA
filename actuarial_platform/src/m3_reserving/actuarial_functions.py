"""
Fonctions actuarielles pures — provisions mathematiques par methode prospective.

Meme principe que M2/actuarial_functions.py : ces fonctions ne dependent
d'aucune donnee chargee sur disque, uniquement de tableaux qx deja construits.
Testables unitairement sans HMD, sans portefeuille - voir tests/test_m3_reserving.py.

Methode prospective (la plus standard en provisionnement vie) :
  Provision mathematique a la date t = VAP(engagements futurs de l'assureur)
                                       - VAP(primes futures de l'assure)

Avec la meme convention que M2 : prestations en fin d'annee de deces,
primes en debut d'annee tant que l'assure est vivant.
"""
from __future__ import annotations

import numpy as np

from src.m2_pricing.actuarial_functions import (
    survival_curve,
    actuarial_present_value_benefit,
    actuarial_present_value_annuity_due,
)


def prospective_reserve(qx_remaining: np.ndarray, capital: float, annual_premium: float,
                         discount_rate: float, radix: int = 100000) -> float:
    """Provision mathematique prospective a un instant donne.

    qx_remaining : qx futurs restants a courir a PARTIR de la date de calcul
                   (pas depuis la souscription - c'est la duree residuelle qui compte).
    capital : capital sous risque restant.
    annual_premium : prime annuelle encore payee par l'assure sur la duree residuelle
                      (prime commerciale reelle, pas la prime pure).
    discount_rate : taux d'actualisation (peut differer du taux de tarification
                    d'origine si on veut mesurer un ecart de rendement).

    Retourne la provision mathematique unitaire (VAP engagements - VAP primes).
    Peut etre negative en theorie (prime future > engagement futur), auquel cas
    on la plafonne a 0 par convention prudente (une compagnie ne peut pas afficher
    une provision negative pour un contrat isole, cela reviendrait a anticiper un
    profit futur comme un actif certain).
    """
    if len(qx_remaining) == 0:
        return 0.0

    Ax = actuarial_present_value_benefit(qx_remaining, discount_rate, radix)
    ax = actuarial_present_value_annuity_due(qx_remaining, discount_rate, radix)

    vap_engagements = capital * Ax
    vap_primes = annual_premium * ax

    reserve = vap_engagements - vap_primes
    return max(reserve, 0.0)


def reserve_run_off(qx_full_path: np.ndarray, capital: float, annual_premium: float,
                     discount_rate: float, radix: int = 100000) -> np.ndarray:
    """Calcule la provision mathematique a CHAQUE annee future d'un contrat
    (run-off complet), en reappliquant prospective_reserve sur la duree
    residuelle a chaque pas de temps. Utile pour visualiser l'evolution de
    la provision dans le temps (typiquement croissante puis decroissante
    pour un temporaire, croissante puis stable pour une vie entiere).

    Retourne un array de longueur len(qx_full_path)+1 (provision a t=0,1,...,n).
    """
    n = len(qx_full_path)
    reserves = np.empty(n + 1)
    for t in range(n + 1):
        reserves[t] = prospective_reserve(
            qx_full_path[t:], capital, annual_premium, discount_rate, radix
        )
    return reserves
