"""
M8 - Gestion Actif-Passif (ALM).

Orchestration : construit un bilan simplifié (actif synthétique vs passif
réel) pour comparer leurs durations et mesurer l'écart de sensibilité aux
taux (duration gap), en réutilisant :
  - M2 (qx projetés, via _get_qx_path_for_policy) pour les flux de passif
  - M4/loader.py (courbes EIOPA réelles, centrale/choc up/down) pour
    l'actualisation des deux côtés du bilan
  - M8/synthetic_assets.py (généré ici) pour le portefeuille obligataire

PÉRIMÈTRE ASSUMÉ (à documenter dans le mémoire) :
  - Seules les obligations ont une duration modélisée finement (flux
    coupons + principal). Actions et immobilier sont traités comme des
    montants de valeur de marché SANS sensibilité aux taux modélisée
    (duration = 0 par simplification) - leur risque relève d'autres
    sous-modules SCR (risque actions, risque immobilier), hors périmètre.
  - La duration du passif est calculée sur le flux NET (prestations moins
    primes), qui peut changer de signe selon les années - interprétation
    Macaulay approximative dans ce cas (limite documentée dans
    actuarial_functions.py).
  - Le bilan actif est calibré pour couvrir le passif à un ratio cible
    (config m8_alm.target_coverage_ratio), pas une vraie contrainte de
    solvabilité complète (qui impliquerait le SCR de marché, hors périmètre).
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from src.common.config_loader import load_config, get_logger
from src.common.synthetic_portfolio import load_synthetic_portfolio
from src.m2_pricing.pricing import _get_qx_path_for_policy
from src.m2_pricing.actuarial_functions import survival_curve
from src.m4_scr.loader import get_shocked_curves
from src.m4_scr.scr import compute_total_best_estimate_with_curve
from src.m8_alm.actuarial_functions import present_value, macaulay_duration, dollar_duration_gap
from src.m8_alm.synthetic_assets import generate_synthetic_bond_portfolio, build_bond_cash_flows

logger = get_logger(__name__)


def compute_liability_cash_flow_schedule(portfolio: pd.DataFrame | None = None) -> dict:
    """Agrège les flux de passif de tout le portefeuille à risque, indexés
    par année 0..max_horizon depuis la date d'évaluation courante. Réutilise
    le même regroupement par profil que M7 pour rester performant.

    Retourne un dict avec 'benefit_cf' (prestations, toujours >= 0) et
    'premium_cf' (primes, toujours >= 0) SÉPARÉMENT, plutôt qu'un flux net
    déjà combiné - voir compute_full_alm_report pour pourquoi cette
    séparation est nécessaire (stabilité du calcul de duration).
    """
    cfg = load_config()
    pricing_cfg = cfg["pricing"]
    alm_cfg = cfg["m8_alm"]
    portfolio = portfolio if portfolio is not None else load_synthetic_portfolio()

    risk_products = set(pricing_cfg["risk_products"])
    radix = pricing_cfg["radix"]
    term_duration = pricing_cfg["term_product_duration_years"]
    term_max_age = pricing_cfg["term_product_max_age"]
    whole_life_max_age = pricing_cfg["whole_life_max_age"]
    max_horizon = alm_cfg["max_horizon_years"]

    subset = portfolio[portfolio["produit"].isin(risk_products)]
    bucketed = subset.groupby(["produit", "genre", "age_actuel"], as_index=False).agg(
        capital_assure_eur=("capital_assure_eur", "sum"),
        prime_annuelle_eur=("prime_annuelle_eur", "sum"),
    )

    benefit_cf = np.zeros(max_horizon + 1)
    premium_cf = np.zeros(max_horizon + 1)

    for _, row in bucketed.iterrows():
        if row["produit"] == "Vie Entière":
            duration = max(whole_life_max_age - row["age_actuel"], 0)
        else:
            duration = min(term_duration, max(term_max_age - row["age_actuel"], 0))
        if duration <= 0:
            continue

        qx = _get_qx_path_for_policy(row["age_actuel"], row["genre"], duration)
        if len(qx) == 0:
            continue

        lx = survival_curve(qx, radix)
        deaths = lx[:-1] - lx[1:]
        n = len(qx)

        # Prestations en fin d'année t (t=1..n) ; primes en début d'année t (t=0..n-1)
        benefit_cf[1:n + 1] += row["capital_assure_eur"] * deaths / radix
        premium_cf[0:n] += row["prime_annuelle_eur"] * lx[:-1] / radix

    logger.info(
        "Flux de passif agrégés sur %d profils, horizon=%d ans",
        len(bucketed), max_horizon,
    )
    return {"benefit_cf": benefit_cf, "premium_cf": premium_cf}


def compute_full_alm_report(portfolio: pd.DataFrame | None = None,
                             country: str = "Euro") -> dict:
    """Rapport ALM complet : duration actif/passif, écart, sensibilité NAV
    aux chocs de taux EIOPA (up/down)."""
    cfg = load_config()
    alm_cfg = cfg["m8_alm"]
    portfolio = portfolio if portfolio is not None else load_synthetic_portfolio()

    curves = get_shocked_curves(country)
    central_curve = curves["spot_central"]

    # --- Passif ---
    # Flux de prestations/primes SÉPARÉS (utilisés uniquement pour le calcul
    # de duration ci-dessous, jamais pour dériver une valeur de passif).
    cash_flows = compute_liability_cash_flow_schedule(portfolio)
    benefit_cf, premium_cf = cash_flows["benefit_cf"], cash_flows["premium_cf"]

    # Valeur de marché du passif : RÉUTILISE la fonction M4 déjà testée et
    # validée, qui applique le plafonnement à 0 PAR CONTRAT (comme M3).
    # Ne JAMAIS calculer cette valeur en agrégeant d'abord benefit_cf et
    # premium_cf du portefeuille entier puis en soustrayant : cela permettrait
    # à l'excès de primes d'un contrat surchargé de compenser artificiellement
    # les prestations d'un autre, produisant un passif total négatif (bug
    # observé et corrigé - voir note méthodologique du README).
    liability_value_central = compute_total_best_estimate_with_curve(central_curve, portfolio)

    # Duration de référence du passif = duration des PRESTATIONS SEULES,
    # toujours bien définie et positive (des décès ne sont jamais négatifs).
    # La duration du flux NET (prestations - primes) peut devenir instable,
    # voire négative, quand les primes commerciales sont très supérieures
    # au risque pur sur une grande partie du portefeuille (observé en
    # pratique sur les produits Temporaire/Prévoyance de ce projet, dont le
    # chargement commercial est volontairement élevé - voir M2) : le flux net
    # est alors fortement négatif pendant la majeure partie de la duree du
    # contrat, ce qui peut faire basculer la moyenne ponderee par le temps en
    # territoire negatif. La duration des prestations seules est la pratique
    # standard en ALM pour l'appariement actif-passif (aligner l'actif sur
    # l'ecoulement attendu des sinistres, pas sur un flux net instable).
    liability_duration = macaulay_duration(benefit_cf, central_curve)
    premium_duration = macaulay_duration(premium_cf, central_curve)

    # --- Actif : obligations calibrées pour couvrir le passif au ratio cible ---
    allocation = alm_cfg["allocation"]
    target_total_assets = liability_value_central * alm_cfg["target_coverage_ratio"]
    target_bond_value = target_total_assets * allocation["bonds"]

    bonds = generate_synthetic_bond_portfolio(target_bond_value, central_curve)
    horizon = int(bonds["maturity_years"].max())
    bond_cf = build_bond_cash_flows(
        bonds["maturity_years"].values, alm_cfg["bond_coupon_rate"],
        bonds["notional_eur"].values, horizon,
    )
    bond_value_central = present_value(bond_cf, central_curve)
    bond_duration = macaulay_duration(bond_cf, central_curve)

    equities_value = target_total_assets * allocation["equities"]
    real_estate_value = target_total_assets * allocation["real_estate"]
    total_asset_value_central = bond_value_central + equities_value + real_estate_value

    # Duration actif "mixte" : actions/immobilier supposées duration=0
    # (simplification assumée, voir docstring du module)
    blended_asset_duration = (
        bond_duration * bond_value_central / total_asset_value_central
        if total_asset_value_central > 0 else 0.0
    )

    gap = dollar_duration_gap(
        total_asset_value_central, blended_asset_duration,
        liability_value_central, liability_duration,
    )

    # --- Sensibilité NAV aux chocs de taux (obligations + passif seulement -
    # actions/immobilier non re-pricées sous choc de taux, hors périmètre) ---
    def nav_under_curve(curve: pd.Series) -> float:
        bond_value = present_value(bond_cf, curve)
        liability_value = compute_total_best_estimate_with_curve(curve, portfolio)
        return (bond_value + equities_value + real_estate_value) - liability_value

    nav_central = total_asset_value_central - liability_value_central
    nav_up = nav_under_curve(curves["spot_shock_up"])
    nav_down = nav_under_curve(curves["spot_shock_down"])

    logger.info(
        "ALM : duration actif=%.1f ans, passif=%.1f ans, gap=%.0f EUR | NAV central=%.0f, up=%.0f, down=%.0f",
        blended_asset_duration, liability_duration, gap, nav_central, nav_up, nav_down,
    )

    return {
        "liability_value_central": liability_value_central,
        "liability_duration": liability_duration,
        "premium_duration": premium_duration,
        "bond_value_central": bond_value_central,
        "bond_duration": bond_duration,
        "equities_value": equities_value,
        "real_estate_value": real_estate_value,
        "total_asset_value_central": total_asset_value_central,
        "blended_asset_duration": blended_asset_duration,
        "dollar_duration_gap": gap,
        "nav_central": nav_central,
        "nav_shock_up": nav_up,
        "nav_shock_down": nav_down,
        "nav_sensitivity_up": nav_up - nav_central,
        "nav_sensitivity_down": nav_down - nav_central,
    }


if __name__ == "__main__":
    report = compute_full_alm_report()
    for k, v in report.items():
        print(f"{k:30s} : {v:>18,.2f}" if isinstance(v, float) else f"{k:30s} : {v}")
