"""
M11 - Intelligence ORSA (Own Risk and Solvency Assessment).

Orchestration pure : aucune donnée brute propre. Projette le Best Estimate
(M3), le SCR biométrique (M4) et le ratio de couverture sur un horizon
pluriannuel, sous hypothèse de run-off (voir actuarial_functions.py).

Réutilise directement, sans duplication :
  - M3/compute_total_best_estimate (Best Estimate, taux technique plat)
  - M4/compute_scr_biometric (SCR mortalité + longévité, agrégé)
  - M4/solvency_ratio (ratio de couverture)
  - M9 (config assumed_own_funds_eur, réutilisé comme hypothèse de fonds
    propres disponibles - cohérence inter-modules plutôt que dupliquer
    une nouvelle hypothèse de fonds propres)
"""
from __future__ import annotations

import pandas as pd

from src.common.config_loader import load_config, get_logger
from src.common.synthetic_portfolio import load_synthetic_portfolio
from src.m3_reserving.reserving import compute_total_best_estimate
from src.m4_scr.scr import compute_scr_biometric
from src.m4_scr.scr_functions import solvency_ratio
from src.m11_orsa.actuarial_functions import project_portfolio_aging

logger = get_logger(__name__)


def orsa_projection(portfolio: pd.DataFrame | None = None,
                     horizon_years: int | None = None) -> pd.DataFrame:
    """Construit la projection ORSA pluriannuelle (run-off) du portefeuille.

    Retourne un DataFrame avec une ligne par année de projection (0 = date
    d'évaluation actuelle), colonnes : best_estimate_eur, scr_mortality_eur,
    scr_longevity_eur, scr_vie_biometrique_eur, own_funds_eur, solvency_ratio.
    """
    cfg = load_config()
    horizon = horizon_years or cfg["m11_orsa"]["projection_horizon_years"]
    own_funds = cfg["m9_optimizer"]["assumed_own_funds_eur"]
    portfolio = portfolio if portfolio is not None else load_synthetic_portfolio()

    rows = []
    for t in range(horizon + 1):
        aged_portfolio = project_portfolio_aging(portfolio, t)

        best_estimate = compute_total_best_estimate(aged_portfolio)
        scr_report = compute_scr_biometric(aged_portfolio)
        ratio = solvency_ratio(own_funds, scr_report["scr_vie_biometrique"])

        rows.append({
            "year": t,
            "best_estimate_eur": best_estimate,
            "scr_mortality_eur": scr_report["scr_mortality"],
            "scr_longevity_eur": scr_report["scr_longevity"],
            "scr_vie_biometrique_eur": scr_report["scr_vie_biometrique"],
            "own_funds_eur": own_funds,
            "solvency_ratio": ratio,
        })
        logger.info(
            "ORSA année %d : BE=%.0f EUR, SCR vie=%.0f EUR, ratio=%.2f",
            t, best_estimate, scr_report["scr_vie_biometrique"], ratio,
        )

    return pd.DataFrame(rows)


if __name__ == "__main__":
    projection = orsa_projection()
    print(projection.round(2).to_string(index=False))
