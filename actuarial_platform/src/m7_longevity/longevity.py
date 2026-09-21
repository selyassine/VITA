"""
M7 - Simulateur de risque de longevite (approche stochastique, Monte-Carlo).

Complementaire de M4 (qui applique un choc DETERMINISTE unique -20% sur les
qx) : ici, on reutilise directement les trajectoires simulees par Lee-Carter
dans M1 (project_mortality, deja base sur une marche aleatoire avec derive
et innovations gaussiennes sur k(t)) pour obtenir une vraie DISTRIBUTION du
Best Estimate du portefeuille, et en deriver une VaR a 99.5% - plus riche
qu'un choc ponctuel, meme si le choc reglementaire M4 reste la reference
pour le calcul officiel du SCR (formule standard).

Optimisation - regroupement du portefeuille par profil (produit, genre, age) :
Simuler 5000+ contrats individuellement sur 200+ trajectoires serait trop
lent (des millions d'evaluations). On agrege donc le portefeuille par profil
identique (meme produit, meme genre, meme age exact), en sommant capital et
prime au sein de chaque groupe, puisque deux contrats avec le meme profil
ont exactement le meme qx projete - une seule evaluation actuarielle suffit
par groupe, multipliee par le nombre de contrats concernes.

LIMITE ASSUMEE (a documenter dans le memoire) : nombre de simulations reduit
(200 par defaut, contre 1000 dans M1/M4) pour un temps de calcul raisonnable
sur machine standard. Un intervalle de confiance sur la VaR elle-meme
necessiterait davantage de simulations ou une methode de reduction de
variance (hors perimetre ici).
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from src.common.config_loader import load_config, get_logger
from src.common.synthetic_portfolio import load_synthetic_portfolio
from src.m1_mortality.lee_carter import fit_lee_carter, project_mortality
from src.m3_reserving.actuarial_functions import prospective_reserve
from src.m7_longevity.actuarial_functions import value_at_risk, distribution_summary

logger = get_logger(__name__)


def _bucket_portfolio_for_risk_products(portfolio: pd.DataFrame) -> pd.DataFrame:
    """Regroupe le portefeuille par (produit, genre, age_actuel), en sommant
    capital et prime au sein de chaque groupe. Ne garde que les produits à
    risque (même périmètre que M2/M3/M4)."""
    cfg = load_config()
    risk_products = set(cfg["pricing"]["risk_products"])
    subset = portfolio[portfolio["produit"].isin(risk_products)]

    grouped = subset.groupby(["produit", "genre", "age_actuel"], as_index=False).agg(
        capital_assure_eur=("capital_assure_eur", "sum"),
        prime_annuelle_eur=("prime_annuelle_eur", "sum"),
        n_contrats=("policy_id", "count"),
    )
    logger.info(
        "Portefeuille regroupé pour simulation M7 : %d profils uniques (depuis %d contrats à risque)",
        len(grouped), len(subset),
    )
    return grouped


def _duration_for_product(produit: str, age_actuel: int, cfg: dict) -> int:
    pricing_cfg = cfg["pricing"]
    if produit == "Vie Entière":
        return max(pricing_cfg["whole_life_max_age"] - age_actuel, 0)
    return min(
        pricing_cfg["term_product_duration_years"],
        max(pricing_cfg["term_product_max_age"] - age_actuel, 0),
    )


def simulate_longevity_capital_impact(portfolio: pd.DataFrame | None = None,
                                       n_simulations: int = 200,
                                       confidence: float = 0.995,
                                       seed: int = 42) -> dict:
    """Simule la distribution du Best Estimate du portefeuille sous n_simulations
    trajectoires de mortalite Lee-Carter, et en deduit une VaR de longevite.

    Retourne un dict avec la VaR, le Best Estimate central, un resume
    statistique de la distribution, et la distribution brute (pour tracer
    un histogramme dans M12/dashboard plus tard).
    """
    cfg = load_config()
    portfolio = portfolio if portfolio is not None else load_synthetic_portfolio()
    current_year = cfg["pricing"]["current_year"]
    radix = cfg["pricing"]["radix"]
    discount_rate = cfg["pricing"]["technical_rate"]
    whole_life_max_age = cfg["pricing"]["whole_life_max_age"]

    bucketed = _bucket_portfolio_for_risk_products(portfolio)
    max_duration_needed = whole_life_max_age  # borne haute large et sûre
    jump_off_year = cfg["lee_carter"]["jump_off_year"]
    horizon = current_year + max_duration_needed - jump_off_year

    simulations_by_sex = {}
    for sex_hmd in ["Male", "Female"]:
        result = fit_lee_carter(sex=sex_hmd)
        projection = project_mortality(result, horizon=horizon, n_simulations=n_simulations, seed=seed)
        simulations_by_sex[sex_hmd] = {
            "ages": result.ages,
            "years": projection["years"],
            "mx_sims": projection["simulations"],  # (n_sim, n_ages, horizon)
        }
        logger.info("Simulations Lee-Carter prêtes pour sex=%s (%d trajectoires)",
                    sex_hmd, n_simulations)

    be_per_simulation = np.zeros(n_simulations)

    for _, row in bucketed.iterrows():
        duration = _duration_for_product(row["produit"], row["age_actuel"], cfg)
        if duration <= 0:
            continue

        sex_hmd = "Male" if row["genre"] == "M" else "Female"
        sim_data = simulations_by_sex[sex_hmd]
        ages_index = {age: idx for idx, age in enumerate(sim_data["ages"])}
        years_index = {year: idx for idx, year in enumerate(sim_data["years"])}

        # Détermine les indices (âge, année) de la diagonale pour ce profil,
        # tronqués si on sort des bornes disponibles.
        t_indices = []
        for t in range(duration):
            age_t = row["age_actuel"] + t
            year_t = current_year + t
            if age_t not in ages_index or year_t not in years_index:
                break
            t_indices.append((ages_index[age_t], years_index[year_t]))

        if not t_indices:
            continue

        age_idxs = np.array([a for a, _ in t_indices])
        year_idxs = np.array([y for _, y in t_indices])

        for s in range(n_simulations):
            qx_path = sim_data["mx_sims"][s, age_idxs, year_idxs]
            qx_path = np.clip(qx_path, 0.0, 1.0)
            # row["capital_assure_eur"] et row["prime_annuelle_eur"] sont déjà les
            # SOMMES sur tous les contrats du profil (voir _bucket_portfolio_...) :
            # la provision calculée ici est donc déjà le total du groupe, pas une
            # valeur unitaire à remultiplier par n_contrats (piège de double comptage).
            reserve = prospective_reserve(
                qx_path, row["capital_assure_eur"], row["prime_annuelle_eur"],
                discount_rate, radix,
            )
            be_per_simulation[s] += reserve

    be_central = float(be_per_simulation.mean())
    var_longevity = value_at_risk(be_per_simulation, central=be_central, confidence=confidence)
    summary = distribution_summary(be_per_simulation)

    logger.info(
        "Simulation longévité terminée : BE moyen=%.0f EUR | VaR %.1f%%=%.0f EUR",
        be_central, confidence * 100, var_longevity,
    )

    return {
        "best_estimate_mean_simulated": be_central,
        "value_at_risk_longevity": var_longevity,
        "confidence": confidence,
        "n_simulations": n_simulations,
        "distribution_summary": summary,
        "distribution_raw": be_per_simulation,
    }


if __name__ == "__main__":
    result = simulate_longevity_capital_impact(n_simulations=200)
    print(f"Best Estimate moyen simulé : {result['best_estimate_mean_simulated']:,.0f} EUR")
    print(f"VaR longévité {result['confidence']*100:.1f}% : {result['value_at_risk_longevity']:,.0f} EUR")
    print("\nRésumé de la distribution :")
    for k, v in result["distribution_summary"].items():
        print(f"  {k:8s} : {v:>15,.0f}")
