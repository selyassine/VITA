"""
Génération du portefeuille synthétique maison.

IMPORTANT — Cohérence inter-modules :
Ce portefeuille est généré UNE SEULE FOIS avec une graine aléatoire fixe (seed),
puis persisté sur disque (data/processed/synthetic_portfolio.csv).
Il est ensuite réutilisé À L'IDENTIQUE par M2, M3, M8, M9, M11, M12, M13, M15.

Ne jamais appeler generate_synthetic_portfolio() plusieurs fois avec des seeds
différentes en cours de projet : le "digital twin" (M15) doit voir la même
compagnie partout, sinon les résultats agrégés perdent tout sens.

Si le fichier existe déjà sur disque, load_synthetic_portfolio() le charge
directement sans le régénérer.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from src.common.config_loader import load_config, resolve_path, get_logger

logger = get_logger(__name__)

PRODUCTS = ["Temporaire Décès", "Vie Entière", "Épargne Euro", "Épargne UC", "Prévoyance"]
PRODUCT_WEIGHTS = [0.25, 0.15, 0.30, 0.20, 0.10]


def _approx_mortality_rate(age: np.ndarray, base: float = 0.00004,
                            growth: float = 9.5, cap: float = 0.35) -> np.ndarray:
    """Approximation grossière de type Gompertz du taux de mortalite annuel.

    Utilisee UNIQUEMENT pour calibrer une prime commerciale synthetique
    plausible (croissance realiste avec l'age), PAS pour un quelconque calcul
    actuariel serieux — le vrai risque de mortalite est celui projete par
    Lee-Carter sur donnees HMD reelles dans M1/M2. Cette fonction reste
    volontairement independante de M1 : le portefeuille synthetique doit
    pouvoir etre genere seul, sans dependre d'un fit Lee-Carter prealable.
    """
    return np.minimum(base * np.exp(age / growth), cap)


def generate_synthetic_portfolio(n_policies: int, seed: int) -> pd.DataFrame:
    """Genere un portefeuille de contrats vie synthetique mais realiste.

    Les distributions (age, prime, duree) sont calibrees pour ressembler
    a un portefeuille vie francais typique, sans provenir d'une vraie compagnie.

    Pour les produits a risque deces (Temporaire Deces, Vie Entiere,
    Prevoyance), la prime commerciale est generee a partir d'un cout de
    risque approxime par age (courbe de type Gompertz) + un chargement
    commercial realiste (25%-55%), afin que la comparaison avec la prime
    pure actuarielle calculee par M1/M2 (donnees HMD reelles) produise un
    chargement implicite dans un ordre de grandeur credible. Les deux
    courbes de mortalite (celle-ci, approximative, et celle de M1, reelle)
    ne coincident pas exactement — c'est attendu et a documenter dans le
    memoire comme limite du caractere synthetique du portefeuille.
    """
    rng = np.random.default_rng(seed)

    age_souscription = rng.integers(18, 70, size=n_policies)
    anciennete = rng.integers(0, 25, size=n_policies)
    age_actuel = np.clip(age_souscription + anciennete, 18, 95)

    genre = rng.choice(["M", "F"], size=n_policies, p=[0.48, 0.52])
    produit = rng.choice(PRODUCTS, size=n_policies, p=PRODUCT_WEIGHTS)

    fumeur = rng.choice([0, 1], size=n_policies, p=[0.78, 0.22])
    statut_sante = rng.choice(
        ["standard", "aggrave", "surprime"], size=n_policies, p=[0.82, 0.10, 0.08]
    )
    sante_multiplier = np.select(
        [statut_sante == "standard", statut_sante == "aggrave", statut_sante == "surprime"],
        [1.0, 1.25, 1.6],
    )
    fumeur_multiplier = np.where(fumeur == 1, 1.4, 1.0)

    is_risk_product = np.isin(produit, ["Temporaire Décès", "Vie Entière", "Prévoyance"])

    capital_assure = np.round(rng.lognormal(mean=11.8, sigma=0.55, size=n_policies), 2)  # ~130k médiane

    prime_annuelle = np.empty(n_policies)

    # --- Produits à risque : prime liée à un coût de risque approximé par âge ---
    q_approx = _approx_mortality_rate(age_actuel[is_risk_product])
    loading = rng.uniform(1.25, 1.55, size=is_risk_product.sum())  # chargement commercial 25%-55%
    noise = rng.uniform(0.9, 1.1, size=is_risk_product.sum())
    prime_annuelle[is_risk_product] = np.round(
        capital_assure[is_risk_product] * q_approx * loading * noise
        * sante_multiplier[is_risk_product] * fumeur_multiplier[is_risk_product],
        2,
    )

    # --- Produits d'épargne : logique financière, pas actuarielle (inchangé) ---
    n_savings = (~is_risk_product).sum()
    base_prime_savings = rng.lognormal(mean=6.5, sigma=0.6, size=n_savings)
    facteur_age_savings = 1 + (age_actuel[~is_risk_product] - 40) * 0.01
    prime_annuelle[~is_risk_product] = np.round(base_prime_savings * facteur_age_savings, 2)

    df = pd.DataFrame(
        {
            "policy_id": [f"POL{100000 + i}" for i in range(n_policies)],
            "age_souscription": age_souscription,
            "anciennete_annees": anciennete,
            "age_actuel": age_actuel,
            "genre": genre,
            "produit": produit,
            "fumeur": fumeur,
            "statut_sante": statut_sante,
            "prime_annuelle_eur": prime_annuelle,
            "capital_assure_eur": capital_assure,
        }
    )

    logger.info("Portefeuille synthétique généré : %d contrats (seed=%d)", n_policies, seed)
    return df


def load_synthetic_portfolio(force_regenerate: bool = False) -> pd.DataFrame:
    """Charge le portefeuille depuis data/processed/, le génère si absent.

    C'est CETTE fonction que tous les autres modules doivent appeler
    (jamais generate_synthetic_portfolio() directement), pour garantir
    qu'un seul portefeuille existe dans tout le projet.
    """
    cfg = load_config()
    portfolio_cfg = cfg["data_sources"]["synthetic_portfolio"]
    output_path = resolve_path(portfolio_cfg["output_file"])

    if output_path.exists() and not force_regenerate:
        logger.info("Portefeuille synthétique chargé depuis le cache : %s", output_path)
        return pd.read_csv(output_path)

    df = generate_synthetic_portfolio(
        n_policies=portfolio_cfg["n_policies"], seed=portfolio_cfg["seed"]
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)
    logger.info("Portefeuille synthétique persisté : %s", output_path)
    return df


if __name__ == "__main__":
    portfolio = load_synthetic_portfolio()
    print(portfolio.head())
    print(f"\n{len(portfolio)} contrats générés.")
