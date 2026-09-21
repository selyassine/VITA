"""
M4 - Orchestration du calcul de SCR (Solvency Capital Requirement) - formule standard.

Combine :
  - M1 (mortalite projetee) + M3 (provisionnement) pour les chocs BIOMETRIQUES
    (mortalite +15%, longevite -20%), sans dependre de fichier externe.
  - M4/loader.py (courbes EIOPA reelles) pour le choc de TAUX, en recalculant
    le Best Estimate sous courbe choquee (voir prospective_reserve_with_curve
    ci-dessous, qui actualise chaque flux avec le taux spot de sa propre
    maturite plutot qu'un taux technique plat).

PERIMETRE ASSUME (a documenter dans le memoire) :
  - SCR vie (mortalite + longevite) agrege via la matrice de correlation
    standard Solvabilite II (voir scr_functions.py) -> "SCR_vie_biometrique"
  - SCR de taux calcule separement -> "SCR_taux"
  - L'agregation finale SCR_vie x SCR_taux necessiterait la matrice de
    correlation BSCR complete (marche, defaut, vie, sante, non-vie), qui
    implique aussi le risque de spread/actions/immobilier (hors perimetre
    de ce projet, qui ne modelise pas l'actif - voir futur M8/ALM). Ce module
    presente donc les deux SCR cote a cote plutot que de les agreger
    formellement, ce qui est un choix de perimetre assume, pas un oubli.
  - Le risque de rachat (lapse) necessite M5, non implemente a ce stade -
    absent de l'agregation SCR_vie pour l'instant.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from src.common.config_loader import load_config, get_logger
from src.common.synthetic_portfolio import load_synthetic_portfolio
from src.m2_pricing.pricing import _get_qx_path_for_policy
from src.m2_pricing.actuarial_functions import survival_curve
from src.m3_reserving.reserving import compute_total_best_estimate
from src.m4_scr.loader import get_shocked_curves
from src.m4_scr.scr_functions import scr_submodule, aggregate_scr_life, solvency_ratio

logger = get_logger(__name__)


def prospective_reserve_with_curve(qx_remaining: np.ndarray, capital: float,
                                    annual_premium: float, spot_curve: pd.Series,
                                    radix: int = 100000) -> float:
    """Provision mathematique prospective, mais actualisee avec une courbe de
    taux par maturite (EIOPA) plutot qu'un taux technique plat.

    Meme convention que M3 (prestations fin d'annee, primes debut d'annee),
    mais chaque flux a la date t est actualise avec le taux spot de maturite t
    (interpolation absente : on utilise le taux de la maturite entiere la plus
    proche, les courbes EIOPA couvrant 1 a 150 ans, largement suffisant pour
    des durees de contrat <= 100 ans).
    """
    if len(qx_remaining) == 0:
        return 0.0

    lx = survival_curve(qx_remaining, radix)
    n = len(qx_remaining)
    max_maturity = spot_curve.index.max()

    # Facteurs d'actualisation par maturite (bornes a la maturite max disponible)
    maturities = np.clip(np.arange(1, n + 1), 1, max_maturity)
    rates = spot_curve.loc[maturities].values
    discount_factors = (1 + rates) ** (-np.arange(1, n + 1))

    deaths = lx[:-1] - lx[1:]
    vap_engagements = capital * np.sum(discount_factors * deaths) / radix

    maturities_annuity = np.clip(np.arange(0, n), 1, max_maturity)
    rates_annuity = spot_curve.loc[maturities_annuity].values
    discount_factors_annuity = np.concatenate(
        [[1.0], (1 + rates_annuity[1:]) ** (-np.arange(1, n))]
    )
    vap_primes = annual_premium * np.sum(discount_factors_annuity * lx[:-1]) / radix

    return max(vap_engagements - vap_primes, 0.0)


def compute_total_best_estimate_with_curve(spot_curve: pd.Series,
                                            portfolio: pd.DataFrame | None = None) -> float:
    """Best Estimate total du portefeuille, actualise avec une courbe de taux
    donnee (au lieu du taux technique plat de M3). Reutilise les memes regles
    de duree/perimetre que M3 (memes produits a risque, memes durees)."""
    cfg = load_config()
    pricing_cfg = cfg["pricing"]
    portfolio = portfolio if portfolio is not None else load_synthetic_portfolio()

    risk_products = set(pricing_cfg["risk_products"])
    radix = pricing_cfg["radix"]
    term_duration = pricing_cfg["term_product_duration_years"]
    term_max_age = pricing_cfg["term_product_max_age"]
    whole_life_max_age = pricing_cfg["whole_life_max_age"]

    total = 0.0
    for _, row in portfolio.iterrows():
        if row["produit"] not in risk_products:
            continue
        if row["produit"] == "Vie Entière":
            duration = max(whole_life_max_age - row["age_actuel"], 0)
        else:
            duration = min(term_duration, max(term_max_age - row["age_actuel"], 0))
        if duration <= 0:
            continue

        qx = _get_qx_path_for_policy(row["age_actuel"], row["genre"], duration)
        total += prospective_reserve_with_curve(
            qx, row["capital_assure_eur"], row["prime_annuelle_eur"], spot_curve, radix
        )
    return total


def compute_scr_biometric(portfolio: pd.DataFrame | None = None) -> dict:
    """SCR mortalite + longevite (formule standard, chocs reglementaires config.yaml)."""
    cfg = load_config()
    shocks = cfg["scr_standard_formula"]
    portfolio = portfolio if portfolio is not None else load_synthetic_portfolio()

    be_central = compute_total_best_estimate(portfolio, mortality_shock=0.0)
    be_mortality_shocked = compute_total_best_estimate(
        portfolio, mortality_shock=shocks["mortality_shock"]
    )
    be_longevity_shocked = compute_total_best_estimate(
        portfolio, mortality_shock=shocks["longevity_shock"]
    )

    scr_mortality = scr_submodule(be_central, be_mortality_shocked)
    scr_longevity = scr_submodule(be_central, be_longevity_shocked)

    logger.info(
        "BE central=%.0f EUR | SCR mortalite=%.0f EUR | SCR longevite=%.0f EUR",
        be_central, scr_mortality, scr_longevity,
    )

    return {
        "best_estimate_central": be_central,
        "scr_mortality": scr_mortality,
        "scr_longevity": scr_longevity,
        "scr_vie_biometrique": aggregate_scr_life(
            {"mortality": scr_mortality, "longevity": scr_longevity}
        ),
    }


def compute_scr_interest_rate(portfolio: pd.DataFrame | None = None,
                               country: str = "Euro") -> dict:
    """SCR de taux, a partir des vraies courbes EIOPA (choc up/down)."""
    portfolio = portfolio if portfolio is not None else load_synthetic_portfolio()
    curves = get_shocked_curves(country)

    be_central = compute_total_best_estimate_with_curve(curves["spot_central"], portfolio)
    be_shock_up = compute_total_best_estimate_with_curve(curves["spot_shock_up"], portfolio)
    be_shock_down = compute_total_best_estimate_with_curve(curves["spot_shock_down"], portfolio)

    scr_up = scr_submodule(be_central, be_shock_up)
    scr_down = scr_submodule(be_central, be_shock_down)
    scr_interest = max(scr_up, scr_down)

    logger.info(
        "BE central (courbe)=%.0f EUR | SCR taux hausse=%.0f | SCR taux baisse=%.0f | retenu=%.0f",
        be_central, scr_up, scr_down, scr_interest,
    )

    return {
        "best_estimate_central_curve": be_central,
        "scr_interest_up": scr_up,
        "scr_interest_down": scr_down,
        "scr_taux": scr_interest,
    }


def compute_full_scr_report(portfolio: pd.DataFrame | None = None) -> dict:
    """Rapport complet SCR : biometrique + taux, presentes cote a cote (voir
    limite d'agregation documentee en tete de fichier)."""
    portfolio = portfolio if portfolio is not None else load_synthetic_portfolio()

    biometric = compute_scr_biometric(portfolio)
    interest = compute_scr_interest_rate(portfolio)

    report = {**biometric, **interest}
    logger.info(
        "SCR vie biometrique=%.0f EUR | SCR taux=%.0f EUR (non agreges - voir limite de perimetre)",
        report["scr_vie_biometrique"], report["scr_taux"],
    )
    return report


if __name__ == "__main__":
    report = compute_full_scr_report()
    for k, v in report.items():
        print(f"{k:35s} : {v:>15,.0f}" if isinstance(v, (int, float)) else f"{k}: {v}")
