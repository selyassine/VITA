"""
M2 - Moteur de tarification (Pricing Engine).

Orchestration : combine les projections de mortalite de M1 (Lee-Carter) avec
le portefeuille synthetique commun pour calculer la prime pure de chaque
contrat par equivalence actuarielle (voir actuarial_functions.py pour le
detail des formules, testees independamment de toute donnee reelle).

Perimetre : uniquement les produits a composante de risque deces
(config["pricing"]["risk_products"]). Les produits d'epargne pure
(Epargne Euro, Epargne UC) sont hors perimetre de M2 - leur tarification
releve d'une logique financiere (rendement des actifs), traitee par M8/ALM.

Hypotheses documentees (config.yaml, section "pricing") :
  - Duree des produits temporaires : 20 ans ou jusqu'a 65 ans, le plus proche
  - Produits vie entiere : couverture jusqu'a 100 ans
  - Taux technique : 1% (hypothese prudente, a discuter/ajuster dans le memoire)
  - Mortalite par sexe (Female/Male) projetee separement via Lee-Carter (M1)
  - Approximation qx ~= mx (taux central), usuelle pour de petites valeurs de mx
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from src.common.config_loader import load_config, get_logger
from src.common.synthetic_portfolio import load_synthetic_portfolio
from src.m1_mortality.lee_carter import fit_lee_carter, project_mortality
from src.m2_pricing.actuarial_functions import net_level_premium

logger = get_logger(__name__)

_MORTALITY_PROJECTION_CACHE: dict[str, pd.DataFrame] = {}


def _get_projected_mortality_by_sex(sex_hmd: str) -> pd.DataFrame:
    """Fitte et projette Lee-Carter pour un sexe donne, avec mise en cache memoire
    (evite de refitter deux fois Male/Female si compute_pure_premium est appele
    plusieurs fois dans la meme session)."""
    if sex_hmd not in _MORTALITY_PROJECTION_CACHE:
        cfg = load_config()
        result = fit_lee_carter(sex=sex_hmd)
        horizon = cfg["lee_carter"]["forecast_horizon"]
        projection = project_mortality(result, horizon=horizon)
        _MORTALITY_PROJECTION_CACHE[sex_hmd] = projection["central"]
        logger.info("Projection Lee-Carter mise en cache pour sex=%s", sex_hmd)
    return _MORTALITY_PROJECTION_CACHE[sex_hmd]


def _get_qx_path_for_policy(age_actuel: int, genre: str, duration_years: int,
                             mortality_shock: float = 0.0) -> np.ndarray:
    """Extrait la diagonale (age x, annee courante+t) de la matrice de mortalite
    projetee pour un individu donne, sur la duree de couverture demandee.

    mortality_shock : choc multiplicatif optionnel applique aux qx (ex: +0.15
    pour le choc mortalite SCR, -0.20 pour le choc longevite). 0.0 = aucun choc
    (comportement par defaut, utilise par M2/M3 hors calcul SCR). Le resultat
    est toujours borne a [0, 1] (une probabilite ne peut pas depasser 1, meme
    apres un choc a la hausse important sur un age deja tres eleve).

    Approximation qx ~= mx (taux central) : usuelle en premiere approche, a
    documenter comme limite methodologique dans le memoire (l'ecart est
    negligeable pour les mx faibles mais se creuse aux ages tres eleves).
    """
    cfg = load_config()
    sex_hmd = "Male" if genre == "M" else "Female"
    current_year = cfg["pricing"]["current_year"]

    mortality_matrix = _get_projected_mortality_by_sex(sex_hmd)
    max_age = mortality_matrix.index.max()

    qx_values = []
    for t in range(duration_years):
        age_t = age_actuel + t
        year_t = current_year + t
        if age_t > max_age or year_t not in mortality_matrix.columns:
            logger.warning(
                "Duree de couverture tronquee pour age_actuel=%d, genre=%s : "
                "demandee=%d ans, obtenue=%d ans (horizon Lee-Carter insuffisant). "
                "Augmenter lee_carter.forecast_horizon dans config.yaml si ce cas "
                "n'est pas volontaire.",
                age_actuel, genre, duration_years, t,
            )
            break
        qx_values.append(mortality_matrix.loc[age_t, year_t])

    qx_array = np.array(qx_values) * (1 + mortality_shock)
    return np.clip(qx_array, 0.0, 1.0)


def compute_pure_premium(portfolio: pd.DataFrame | None = None) -> pd.DataFrame:
    """Calcule la prime pure de chaque contrat a risque du portefeuille.

    Retourne le portefeuille enrichi de deux colonnes :
      - prime_pure_eur : prime pure calculee par equivalence actuarielle
      - chargement_implicite_pct : ecart relatif entre prime commerciale
        (prime_annuelle_eur, deja dans le portefeuille synthetique) et prime pure

    Les produits d'epargne (hors perimetre, voir docstring module) ont ces
    deux colonnes a NaN.
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

    prime_pure = np.full(len(portfolio), np.nan)

    for i, row in portfolio.iterrows():
        if row["produit"] not in risk_products:
            continue

        if row["produit"] == "Vie Entière":
            duration = max(whole_life_max_age - row["age_actuel"], 0)
        else:
            duration = min(term_duration, max(term_max_age - row["age_actuel"], 0))

        if duration <= 0:
            prime_pure[i] = 0.0
            continue

        qx = _get_qx_path_for_policy(row["age_actuel"], row["genre"], duration)
        prime_pure[i] = net_level_premium(
            qx, capital=row["capital_assure_eur"], discount_rate=discount_rate, radix=radix
        )

    result = portfolio.copy()
    result["prime_pure_eur"] = np.round(prime_pure, 2)
    result["chargement_implicite_pct"] = np.where(
        result["prime_pure_eur"] > 0,
        np.round(
            100 * (result["prime_annuelle_eur"] - result["prime_pure_eur"]) / result["prime_pure_eur"],
            1,
        ),
        np.nan,
    )

    n_priced = result["prime_pure_eur"].notna().sum()
    logger.info(
        "Prime pure calculee pour %d/%d contrats (produits a risque uniquement)",
        n_priced, len(result),
    )
    return result


if __name__ == "__main__":
    priced = compute_pure_premium()
    print(priced[["policy_id", "produit", "age_actuel", "capital_assure_eur",
                   "prime_annuelle_eur", "prime_pure_eur", "chargement_implicite_pct"]].head(15))
    print("\nResume du chargement implicite par produit (contrats tarifes uniquement):")
    print(priced.dropna(subset=["prime_pure_eur"]).groupby("produit")["chargement_implicite_pct"].describe())
