"""
M9 - Optimiseur d'hypotheses actuarielles (Assumption Optimizer).

Aucune donnee brute propre : orchestre M1 (mortalite, via M2), M2 (prime
pure) et M4 (SCR) pour rechercher le chargement commercial qui maximise la
marge technique du portefeuille sous un arbitrage rachat-prix (voir
actuarial_functions.py pour le modele et sa justification).

Reutilisation intentionnelle (aucune duplication de logique actuarielle) :
  - M2/pricing.py::compute_pure_premium pour la prime pure par contrat
  - M2/pricing.py::_get_qx_path_for_policy + M2/actuarial_functions.py pour
    la rente de survie (ax) par contrat
  - M4/scr.py::compute_scr_biometric pour recalculer le SCR sous le nouveau
    chargement optimal (en construisant un portefeuille "ajuste" ou la prime
    commerciale = chargement_optimal * prime_pure, puis en appelant M4 SANS
    LE MODIFIER - un portefeuille est juste un DataFrame, M4 n'a pas besoin
    de savoir qu'il est hypothetique)
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from src.common.config_loader import load_config, get_logger
from src.common.synthetic_portfolio import load_synthetic_portfolio
from src.m2_pricing.pricing import compute_pure_premium, _get_qx_path_for_policy
from src.m2_pricing.actuarial_functions import actuarial_present_value_annuity_due
from src.m4_scr.scr import compute_scr_biometric
from src.m4_scr.scr_functions import solvency_ratio
from src.m9_optimizer.actuarial_functions import (
    margin_per_policy, optimal_loading_closed_form, clip_to_bounds,
)

logger = get_logger(__name__)


def _compute_annuity_values(priced_portfolio: pd.DataFrame, applicable_products: set) -> np.ndarray:
    """Calcule la rente de survie (ax) de chaque contrat tarifé par M2, limité
    aux produits applicables à l'optimisation (voir config.yaml : Vie Entière
    exclue, voir docstring du module).

    Reutilise directement _get_qx_path_for_policy (M2) et
    actuarial_present_value_annuity_due (M2/actuarial_functions) - aucune
    nouvelle formule actuarielle introduite ici.
    """
    cfg = load_config()
    pricing_cfg = cfg["pricing"]
    discount_rate = pricing_cfg["technical_rate"]
    radix = pricing_cfg["radix"]
    term_duration = pricing_cfg["term_product_duration_years"]
    term_max_age = pricing_cfg["term_product_max_age"]

    ax_values = np.full(len(priced_portfolio), np.nan)

    for i, row in priced_portfolio.iterrows():
        if row["produit"] not in applicable_products:
            continue
        if pd.isna(row["prime_pure_eur"]) or row["prime_pure_eur"] == 0:
            continue
        duration = min(term_duration, max(term_max_age - row["age_actuel"], 0))
        if duration <= 0:
            continue

        qx = _get_qx_path_for_policy(row["age_actuel"], row["genre"], duration)
        if len(qx) == 0:
            continue
        ax_values[i] = actuarial_present_value_annuity_due(qx, discount_rate, radix)

    return ax_values


def optimize_portfolio_loading(portfolio: pd.DataFrame | None = None) -> dict:
    """Trouve le chargement commercial optimal du portefeuille et évalue son
    impact sur le SCR (via M4), pour un rapport complet d'aide à la décision.
    """
    cfg = load_config()
    m9_cfg = cfg["m9_optimizer"]
    lapse_elasticity = m9_cfg["lapse_elasticity"]
    bounds = tuple(m9_cfg["loading_bounds"])
    own_funds = m9_cfg["assumed_own_funds_eur"]
    applicable_products = set(m9_cfg["applicable_products"])

    portfolio = portfolio if portfolio is not None else load_synthetic_portfolio()

    priced = compute_pure_premium(portfolio)
    ax_values = _compute_annuity_values(priced, applicable_products)
    priced = priced.assign(ax=ax_values)

    valid = priced.dropna(subset=["prime_pure_eur", "ax"])
    valid = valid[valid["prime_pure_eur"] > 0]

    # Chargement optimal fermé (uniforme sur le périmètre protection pure -
    # voir limite documentée dans actuarial_functions.py : indépendant de
    # prime_pure/ax du fait de l'élasticité uniforme assumée).
    optimal_loading_raw = optimal_loading_closed_form(lapse_elasticity)
    optimal_loading = clip_to_bounds(optimal_loading_raw, bounds)

    total_margin_optimal = float(np.sum(
        margin_per_policy(valid["prime_pure_eur"], valid["ax"], optimal_loading, lapse_elasticity)
    ))
    # Marge à chargement=1.3 (référence commerciale usuelle) pour comparaison
    total_margin_reference = float(np.sum(
        margin_per_policy(valid["prime_pure_eur"], valid["ax"], 1.3, lapse_elasticity)
    ))

    # Impact sur le SCR : portefeuille ajusté avec prime commerciale = chargement
    # optimal * prime pure, UNIQUEMENT pour le périmètre protection pure (voir
    # config.yaml). La Vie Entière et les autres produits gardent leur prime
    # d'origine, inchangée.
    adjusted_portfolio = portfolio.copy()
    mask = (
        priced["prime_pure_eur"].notna() & (priced["prime_pure_eur"] > 0)
        & priced["produit"].isin(applicable_products)
    )
    adjusted_portfolio.loc[mask, "prime_annuelle_eur"] = (
        optimal_loading * priced.loc[mask, "prime_pure_eur"]
    )

    scr_report_baseline = compute_scr_biometric(portfolio)
    scr_report_optimal = compute_scr_biometric(adjusted_portfolio)

    solvency_ratio_baseline = solvency_ratio(own_funds, scr_report_baseline["scr_vie_biometrique"])
    solvency_ratio_optimal = solvency_ratio(own_funds, scr_report_optimal["scr_vie_biometrique"])

    logger.info(
        "Chargement optimal=%.3f | Marge totale=%.0f EUR | SCR vie (baseline->optimal)=%.0f -> %.0f EUR",
        optimal_loading, total_margin_optimal,
        scr_report_baseline["scr_vie_biometrique"], scr_report_optimal["scr_vie_biometrique"],
    )

    return {
        "optimal_loading": optimal_loading,
        "optimal_loading_unclipped": optimal_loading_raw,
        "lapse_elasticity_assumed": lapse_elasticity,
        "total_margin_at_optimal": total_margin_optimal,
        "total_margin_at_reference_1_3": total_margin_reference,
        "n_policies_priced": len(valid),
        "scr_vie_biometrique_baseline": scr_report_baseline["scr_vie_biometrique"],
        "scr_vie_biometrique_optimal": scr_report_optimal["scr_vie_biometrique"],
        "solvency_ratio_baseline": solvency_ratio_baseline,
        "solvency_ratio_optimal": solvency_ratio_optimal,
        "assumed_own_funds_eur": own_funds,
    }


if __name__ == "__main__":
    report = optimize_portfolio_loading()
    for k, v in report.items():
        if isinstance(v, float):
            print(f"{k:35s} : {v:>15,.3f}" if v < 100 else f"{k:35s} : {v:>15,.0f}")
        else:
            print(f"{k:35s} : {v}")
