"""
M11 - Fonctions pures : vieillissement du portefeuille pour projection ORSA.

Hypothèse RUN-OFF (à documenter dans le mémoire) : aucune nouvelle affaire
n'est souscrite sur l'horizon de projection - le portefeuille existant
vieillit simplement d'année en année. C'est l'hypothèse la plus simple et
la plus prudente pour un premier ORSA prospectif (une hypothèse de nouvelle
production nécessiterait un plan d'affaires commercial, hors périmètre).

Cette fonction est pure (transforme un DataFrame en un autre DataFrame sans
dépendance externe) et donc testable avec un petit portefeuille fabriqué à
la main, sans avoir besoin de charger HMD/EIOPA.
"""
from __future__ import annotations

import pandas as pd


def project_portfolio_aging(portfolio: pd.DataFrame, years_forward: int) -> pd.DataFrame:
    """Vieillit le portefeuille de `years_forward` années (run-off, sans
    nouvelle affaire). Les contrats dont la couverture serait déjà terminée
    à cet horizon ne sont PAS retirés explicitement ici : c'est M2/M3/M4 qui
    les traitent naturellement comme des contrats à durée résiduelle nulle
    (contribution nulle), pas besoin de dupliquer cette logique ici.
    """
    if years_forward < 0:
        raise ValueError("years_forward doit être positif ou nul.")
    aged = portfolio.copy()
    aged["age_actuel"] = aged["age_actuel"] + years_forward
    aged["anciennete_annees"] = aged["anciennete_annees"] + years_forward
    return aged
