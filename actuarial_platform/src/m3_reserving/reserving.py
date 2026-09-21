"""
M3 - Moteur de provisionnement (Reserve Engine).

Orchestration : reutilise les projections de mortalite de M1 (via les memes
fonctions d'extraction de qx que M2) et les primes commerciales du
portefeuille synthetique pour calculer la provision mathematique de chaque
contrat a risque, a la date d'evaluation courante (config["pricing"]["current_year"]).

Perimetre : memes produits que M2 (Temporaire Deces, Vie Entiere, Prevoyance).
Les produits d'epargne restent hors perimetre (provisionnement epargne =
logique financiere, pas actuarielle pure - futur M8/ALM).

Reutilise intentionnellement _get_qx_path_for_policy de M2 plutot que de la
dupliquer : un seul point de verite pour "quelle duree de couverture et quel
qx pour quel contrat", partage entre pricing et provisionnement.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from src.common.config_loader import load_config, get_logger
from src.common.synthetic_portfolio import load_synthetic_portfolio
from src.m2_pricing.pricing import _get_qx_path_for_policy
from src.m3_reserving.actuarial_functions import prospective_reserve

logger = get_logger(__name__)


def compute_mathematical_reserves(portfolio: pd.DataFrame | None = None,
                                   mortality_shock: float = 0.0) -> pd.DataFrame:
    """Calcule la provision mathematique de chaque contrat a risque du portefeuille.

    mortality_shock : choc multiplicatif optionnel sur les qx (voir
    M2/pricing.py::_get_qx_path_for_policy). 0.0 par defaut (aucun choc).
    Utilise par M4 pour recalculer le Best Estimate sous choc mortalite (+15%)
    ou longevite (-20%).

    Retourne le portefeuille enrichi de la colonne provision_mathematique_eur.
    Les produits hors perimetre (epargne) ont cette colonne a NaN, comme pour
    prime_pure_eur dans M2.
    """
    cfg = load_config()
    pricing_cfg = cfg["pricing"]
    portfolio = portfolio if portfolio is not None else load_synthetic_portfolio()

    risk_products = set(pricing_cfg["risk_products"])
    discount_rate = pricing_cfg["technical_rate"]
    radix = pricing_cfg["radix"]
    term_duration = pricing_cfg["term_product_duration_years"]
    term_max_age = pricing_cfg["term_product_max_age"]
    whole_life_max_age = pricing_cfg["whole_life_max_age"]

    provisions = np.full(len(portfolio), np.nan)

    for i, row in portfolio.iterrows():
        if row["produit"] not in risk_products:
            continue

        if row["produit"] == "Vie Entière":
            duration = max(whole_life_max_age - row["age_actuel"], 0)
        else:
            duration = min(term_duration, max(term_max_age - row["age_actuel"], 0))

        if duration <= 0:
            provisions[i] = 0.0
            continue

        qx = _get_qx_path_for_policy(row["age_actuel"], row["genre"], duration,
                                      mortality_shock=mortality_shock)
        provisions[i] = prospective_reserve(
            qx_remaining=qx,
            capital=row["capital_assure_eur"],
            annual_premium=row["prime_annuelle_eur"],
            discount_rate=discount_rate,
            radix=radix,
        )

    result = portfolio.copy()
    result["provision_mathematique_eur"] = np.round(provisions, 2)

    n_provisioned = result["provision_mathematique_eur"].notna().sum()
    total_reserve = result["provision_mathematique_eur"].sum()
    logger.info(
        "Provisions mathematiques calculees pour %d/%d contrats (choc=%.0f%%). Total : %.0f EUR",
        n_provisioned, len(result), mortality_shock * 100, total_reserve,
    )
    return result


def compute_total_best_estimate(portfolio: pd.DataFrame | None = None,
                                 mortality_shock: float = 0.0) -> float:
    """Raccourci : retourne uniquement le Best Estimate total du portefeuille
    (somme des provisions mathematiques), sans le detail contrat par contrat.
    Utilise par M4 pour les calculs de SCR (biometrique), ou seul le total
    importe, pas le detail par police.
    """
    result = compute_mathematical_reserves(portfolio, mortality_shock=mortality_shock)
    return float(result["provision_mathematique_eur"].sum())


if __name__ == "__main__":
    reserved = compute_mathematical_reserves()
    print(reserved[["policy_id", "produit", "age_actuel", "capital_assure_eur",
                     "prime_annuelle_eur", "provision_mathematique_eur"]].head(15))
    print("\nProvision mathematique totale par produit (contrats provisionnes uniquement):")
    print(reserved.dropna(subset=["provision_mathematique_eur"])
          .groupby("produit")["provision_mathematique_eur"].agg(["count", "sum", "mean"]))
