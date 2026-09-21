"""
M5 - Chargement des donnees de rachat (lapse) et derivation du label.

Source : Kaggle "Life Insurance Customer Retention Dataset".
Nature reelle : SYNTHETIQUE (genere par la plateforme Mostly AI - identifiants
prefixes "mostly...", artefacts de generation dans noms/metiers, categories
rares regroupees en "_RARE_"). Classee "reelle tierce" par erreur au debut du
projet ; corrige apres inspection du fichier reel (voir config.yaml).

Colonnes disponibles (14) : customer_id, age, gender, marital_status,
number_of_dependents, annual_income, occupation, health_status,
smoking_status, policy_type, coverage_amount, monthly_premium,
policy_start_date. AUCUNE colonne de resiliation.

DERIVATION DU LABEL (a documenter explicitement dans le memoire comme un
PROXY STATISTIQUE, pas un historique reel d'evenements de rachat) :

Score de propension au rachat combinant des facteurs actuariels connus
(litterature sur le risque de rachat) :
  - Ratio prime/revenu annuel : tension financiere, facteur de rachat classique
    (coefficient positif : ratio eleve -> plus de rachat)
  - "Bosse de rachat" (lapse hump) : le risque de rachat culmine typiquement
    en debut de contrat (pic vers 3 ans) puis diminue - phenomene tres
    documente en assurance vie. Modelise par t * exp(-t/3).
  - Nombre de personnes a charge : plus de charges -> moins de rachat
    (besoin de couverture plus fort) - coefficient negatif
  - Statut de sante : bonne sante -> plus de facilite a re-souscrire ailleurs
    -> plus de rachat. Mauvaise sante -> moins de rachat (contrat difficile
    a remplacer) - coefficient negatif pour "Fair"
  - Type de police : Temporaire (Term Life) sans valeur de rachat -> rachat
    plus frequent. Vie Entiere/Universelle/Variable, avec valeur de rachat,
    retiennent davantage l'assure - coefficient positif pour Term Life

Le score brut est transforme en probabilite via une fonction logistique,
calibree (recherche de l'ordonnee a l'origine par bissection) pour que le
taux de resiliation GLOBAL du portefeuille corresponde a une cible choisie
(target_rate, 17.5% par defaut - ordre de grandeur d'un portefeuille observe
sur plusieurs annees). Le label binaire final est tire aleatoirement (loi de
Bernoulli, seed fixe pour reproductibilite) selon cette probabilite.

LIMITE METHODOLOGIQUE MAJEURE : ce label ne reflete AUCUN evenement reel de
resiliation. Il s'agit d'une construction statistique plausible utilisee
pour demontrer la methodologie de modelisation du risque de rachat (M5),
pas d'une prediction fiable du comportement reel des assures. A rappeler
explicitement dans le memoire a chaque utilisation des resultats de M5.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from scipy.optimize import brentq

from src.common.config_loader import load_config, resolve_path, get_logger

logger = get_logger(__name__)

# Coefficients du score de propension au rachat (echelle arbitraire, calibree
# ensuite par l'ordonnee a l'origine - seules les valeurs RELATIVES comptent)
COEF_PREMIUM_INCOME_RATIO = 3.0
COEF_TENURE_HUMP = 1.5
COEF_DEPENDENTS = -0.15
HEALTH_EFFECT = {"Excellent": 0.3, "Good": 0.0, "Fair": -0.4, "_RARE_": 0.0}
POLICY_TYPE_EFFECT = {"Term Life": 0.6, "Universal Life": -0.1,
                       "Whole Life": -0.5, "Variable Life": -0.1}


def load_retention_raw() -> pd.DataFrame:
    """Charge le CSV brut, sans transformation."""
    cfg = load_config()
    raw_dir = resolve_path(cfg["data_sources"]["kaggle_retention"]["raw_dir"])
    candidates = list(raw_dir.glob("*.csv"))
    if not candidates:
        raise FileNotFoundError(
            f"Aucun CSV trouvé dans {raw_dir}\n"
            "Redépose et dézippe l'archive Retention dans data/raw/kaggle_retention/."
        )
    df = pd.read_csv(candidates[0])
    logger.info("Données Retention chargées : %d lignes, %d colonnes", len(df), df.shape[1])
    return df


def derive_lapse_label(df: pd.DataFrame, target_rate: float = 0.175,
                        seed: int = 42) -> pd.DataFrame:
    """Dérive une cible binaire de résiliation (proxy statistique - voir
    docstring du module pour la justification complète et les limites).

    Retourne le DataFrame enrichi de :
      - anciennete_years : ancienneté du contrat en années (référence = 1er
        janvier de l'année courante de config.yaml)
      - premium_to_income_ratio
      - lapse_probability : probabilité individuelle issue du score calibré
      - lapsed : label binaire tiré aléatoirement (0 = actif, 1 = résilié)
    """
    cfg = load_config()
    current_year = cfg["pricing"]["current_year"]
    reference_date = pd.Timestamp(year=current_year, month=1, day=1)

    df = df.copy()
    df["policy_start_date"] = pd.to_datetime(df["policy_start_date"])
    df["anciennete_years"] = (reference_date - df["policy_start_date"]).dt.days / 365.25
    df["premium_to_income_ratio"] = (df["monthly_premium"] * 12) / df["annual_income"]

    tenure_hump = df["anciennete_years"] * np.exp(-df["anciennete_years"] / 3)
    health_effect = df["health_status"].map(HEALTH_EFFECT).fillna(0.0)
    policy_effect = df["policy_type"].map(POLICY_TYPE_EFFECT).fillna(0.0)

    raw_score = (
        COEF_PREMIUM_INCOME_RATIO * df["premium_to_income_ratio"]
        + COEF_TENURE_HUMP * tenure_hump
        + COEF_DEPENDENTS * df["number_of_dependents"]
        + health_effect
        + policy_effect
    )

    def mean_prob_for_intercept(intercept: float) -> float:
        return float(np.mean(1 / (1 + np.exp(-(raw_score + intercept)))))

    # Calibration de l'ordonnée à l'origine pour atteindre le taux cible global
    intercept = brentq(lambda b: mean_prob_for_intercept(b) - target_rate, -50, 50)

    df["lapse_probability"] = 1 / (1 + np.exp(-(raw_score + intercept)))

    rng = np.random.default_rng(seed)
    df["lapsed"] = (rng.random(len(df)) < df["lapse_probability"]).astype(int)

    achieved_rate = df["lapsed"].mean()
    logger.info(
        "Label de résiliation dérivé : cible=%.1f%%, taux obtenu=%.1f%% (n=%d)",
        target_rate * 100, achieved_rate * 100, len(df),
    )
    return df


def load_retention_with_label(target_rate: float = 0.175, seed: int = 42) -> pd.DataFrame:
    """Raccourci : charge le CSV brut et dérive directement le label."""
    df = load_retention_raw()
    return derive_lapse_label(df, target_rate=target_rate, seed=seed)


if __name__ == "__main__":
    df = load_retention_with_label()
    print(df[["age", "policy_type", "health_status", "anciennete_years",
              "premium_to_income_ratio", "lapse_probability", "lapsed"]].head(10))
    print(f"\nTaux de résiliation global : {df['lapsed'].mean() * 100:.1f}%")
    print("\nTaux de résiliation par type de police :")
    print(df.groupby("policy_type")["lapsed"].mean().sort_values(ascending=False))
