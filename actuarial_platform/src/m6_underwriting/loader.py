"""
Chargement des données Prudential Life Insurance Assessment (Kaggle).

Source : https://www.kaggle.com/c/prudential-life-insurance-assessment
Nature : donnée réelle tierce, anonymisée (128 colonnes, ~59 000 individus).
Cible : `Response`, niveau de risque assuré de 1 (meilleur) à 8 (pire).

ATTENTION : les noms de colonnes sont anonymisés par Prudential
(Product_Info_X, Medical_History_X, Medical_Keyword_X, etc.). Il n'existe
pas de documentation publique associant ces colonnes à des variables métier
précises — c'est une contrainte connue et documentée du dataset, à mentionner
explicitement dans le mémoire (limite de la donnée, pas une erreur du projet).
"""
from __future__ import annotations

import pandas as pd

from src.common.config_loader import load_config, resolve_path, get_logger

logger = get_logger(__name__)

TARGET_COLUMN = "Response"


def load_prudential_raw() -> pd.DataFrame:
    """Charge train.csv tel quel, sans transformation."""
    cfg = load_config()
    path = resolve_path(cfg["data_sources"]["kaggle_prudential"]["train_file"])
    if not path.exists():
        raise FileNotFoundError(
            f"Fichier introuvable : {path}\n"
            "Dépose train.csv (Prudential) dans data/raw/kaggle_prudential/ (voir README.md)."
        )
    df = pd.read_csv(path)
    logger.info(
        "Données Prudential chargées : %d individus, %d colonnes, cible '%s' présente=%s",
        len(df), df.shape[1], TARGET_COLUMN, TARGET_COLUMN in df.columns,
    )
    return df


def get_feature_groups(df: pd.DataFrame) -> dict[str, list[str]]:
    """Regroupe les colonnes par famille (utile pour l'exploration et le feature engineering)."""
    groups = {
        "product_info": [c for c in df.columns if c.startswith("Product_Info")],
        "employment_info": [c for c in df.columns if c.startswith("Employment_Info")],
        "insured_info": [c for c in df.columns if c.startswith("InsuredInfo")],
        "insurance_history": [c for c in df.columns if c.startswith("Insurance_History")],
        "family_history": [c for c in df.columns if c.startswith("Family_Hist")],
        "medical_history": [c for c in df.columns if c.startswith("Medical_History")],
        "medical_keyword": [c for c in df.columns if c.startswith("Medical_Keyword")],
        "biometrics": [c for c in ["Ins_Age", "Ht", "Wt", "BMI"] if c in df.columns],
    }
    return groups


def train_test_split_prudential(df: pd.DataFrame, test_size: float = 0.2, seed: int = 42):
    """Split simple stratifié sur la cible, pour l'entraînement du modèle M6."""
    from sklearn.model_selection import train_test_split

    X = df.drop(columns=[TARGET_COLUMN, "Id"], errors="ignore")
    y = df[TARGET_COLUMN]
    return train_test_split(X, y, test_size=test_size, random_state=seed, stratify=y)


if __name__ == "__main__":
    df = load_prudential_raw()
    print(df[[TARGET_COLUMN]].value_counts().sort_index())
    groups = get_feature_groups(df)
    for name, cols in groups.items():
        print(f"{name}: {len(cols)} colonnes")
