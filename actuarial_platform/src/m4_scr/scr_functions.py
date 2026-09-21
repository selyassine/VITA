"""
M4 - Fonctions pures de calcul du SCR (Solvency Capital Requirement).

Formule standard Solvabilite II (Reglement delegue (UE) 2015/35).

Separation volontaire (meme principe que M2/M3) :
  - Les chocs de choc BIOMETRIQUES (mortalite, longevite, rachat, frais) sont
    des valeurs fixes REGLEMENTAIRES, codees en dur dans config.yaml, et le
    calcul de leur impact ne depend d'aucun fichier de donnees externe -
    seulement des sorties de M1/M3 (deja fonctionnels).
  - Le choc de TAUX (SCR marche/taux) depend, lui, des courbes EIOPA
    (fichier externe reel) - traite separement dans loader.py une fois la
    structure du fichier confirmee.

Principe general d'un sous-module de risque (ex: SCR mortalite) :
  SCR_risque = BE_choque - BE_central
  ou BE = Best Estimate = somme des provisions mathematiques (M3) du
  portefeuille, recalculees sous le scenario de choc applique aux qx (M1).

Agregation des sous-modules par la matrice de correlation standard
Solvabilite II (formule standard, correlations fixes et publiques - pas de
correlation a estimer soi-meme) :
  SCR_vie = sqrt( sum_i sum_j Corr(i,j) * SCR_i * SCR_j )
"""
from __future__ import annotations

import numpy as np

# Matrice de correlation standard Solvabilite II - module SCR Vie
# (Reglement delegue (UE) 2015/35, Annexe IV)
# Ordre : mortalite, longevite, invalidite, rachat, frais, revision, catastrophe
SCR_LIFE_CORRELATION_ORDER = [
    "mortality", "longevity", "disability", "lapse", "expense", "revision", "catastrophe",
]

SCR_LIFE_CORRELATION_MATRIX = np.array([
    # mort  long  disa  laps  exp   rev   cat
    [1.00, -0.25, 0.25, 0.00, 0.25, 0.00, 0.25],   # mortalite
    [-0.25, 1.00, 0.00, 0.25, 0.25, 0.25, 0.00],   # longevite
    [0.25, 0.00, 1.00, 0.00, 0.50, 0.00, 0.25],    # invalidite
    [0.00, 0.25, 0.00, 1.00, 0.50, 0.00, 0.25],    # rachat
    [0.25, 0.25, 0.50, 0.50, 1.00, 0.00, 0.25],    # frais
    [0.00, 0.25, 0.00, 0.00, 0.00, 1.00, 0.00],    # revision
    [0.25, 0.00, 0.25, 0.25, 0.25, 0.00, 1.00],    # catastrophe
])


def scr_submodule(best_estimate_central: float, best_estimate_shocked: float) -> float:
    """SCR d'un sous-module de risque = écart entre BE choqué et BE central.

    Convention : un SCR est toujours >= 0 (c'est un besoin de capital, jamais
    négatif). Si le choc améliore la position (BE choqué < BE central), le
    SCR de ce sous-module est nul par convention prudente.
    """
    return max(best_estimate_shocked - best_estimate_central, 0.0)


def aggregate_scr_life(scr_by_risk: dict[str, float]) -> float:
    """Agrège les SCR par sous-module via la matrice de corrélation standard.

    scr_by_risk : dict avec au moins certaines des clés de
                  SCR_LIFE_CORRELATION_ORDER (les clés absentes sont traitées
                  comme un SCR nul pour ce sous-module, ex: pas de risque
                  d'invalidité modélisé dans ce projet).
    """
    vector = np.array([scr_by_risk.get(risk, 0.0) for risk in SCR_LIFE_CORRELATION_ORDER])
    variance = vector @ SCR_LIFE_CORRELATION_MATRIX @ vector
    return float(np.sqrt(max(variance, 0.0)))


def solvency_ratio(own_funds: float, scr: float) -> float:
    """Ratio de couverture du SCR = fonds propres éligibles / SCR.

    >= 100% = compagnie solvable au sens Solvabilité II (>= 1 SCR de fonds propres).
    """
    if scr == 0:
        return float("inf")
    return own_funds / scr
