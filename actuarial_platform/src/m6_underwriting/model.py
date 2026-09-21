"""
Modèle de classification du risque assuré (M6 - Underwriting).

Baseline : Random Forest multi-classe sur les 8 niveaux de risque `Response`.
Objectif du mémoire : comparer ce baseline à des approches plus avancées
(gradient boosting, ordinal regression vu que Response est une échelle ordonnée)
et surtout démontrer l'usage dans le pipeline de tarification (M2).
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, cohen_kappa_score
from sklearn.impute import SimpleImputer

from src.common.config_loader import get_logger
from src.m6_underwriting.loader import load_prudential_raw, train_test_split_prudential

logger = get_logger(__name__)


def prepare_features(X: pd.DataFrame) -> pd.DataFrame:
    """Imputation + encodage — baseline volontairement simple.

    Note méthodologique pour le mémoire : Medical_History_10 et 32 ont un taux de
    valeurs manquantes très élevé dans ce dataset (connu de la compétition Kaggle
    d'origine) ; une imputation plus fine (indicateur de missingness, MICE) est
    une piste d'amélioration à discuter plutôt qu'un prérequis du baseline.

    Product_Info_2 est la seule variable catégorielle non-numérique du dataset
    (ex: 'D2', 'A1') ; elle est encodée en one-hot. Toutes les autres colonnes
    sont déjà numériques (y compris les 48 Medical_Keyword_X, binaires 0/1).
    """
    X = X.copy()
    categorical_cols = X.select_dtypes(exclude=[np.number]).columns.tolist()
    if categorical_cols:
        X = pd.get_dummies(X, columns=categorical_cols, drop_first=False)

    numeric_cols = X.select_dtypes(include=[np.number]).columns
    imputer = SimpleImputer(strategy="median")
    X[numeric_cols] = imputer.fit_transform(X[numeric_cols])
    return X


def train_baseline_model(random_state: int = 42) -> dict:
    """Entraîne et évalue le modèle baseline. Retourne modèle + métriques."""
    df = load_prudential_raw()
    X_train, X_test, y_train, y_test = train_test_split_prudential(df, seed=random_state)

    X_train = prepare_features(X_train)
    X_test = prepare_features(X_test)

    model = RandomForestClassifier(
        n_estimators=300, max_depth=None, n_jobs=-1, random_state=random_state
    )
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)

    # Cohen's Kappa quadratique : métrique officielle de la compétition Kaggle
    # d'origine, adaptée car Response est une échelle ORDONNÉE (1 à 8), pas
    # des catégories indépendantes -> une erreur de 1 classe pèse moins qu'une
    # erreur de 5 classes.
    qwk = cohen_kappa_score(y_test, y_pred, weights="quadratic")

    logger.info("Modèle M6 entraîné. Quadratic Weighted Kappa = %.4f", qwk)

    return {
        "model": model,
        "quadratic_weighted_kappa": qwk,
        "classification_report": classification_report(y_test, y_pred, zero_division=0),
        "feature_importances": pd.Series(
            model.feature_importances_, index=X_train.columns
        ).sort_values(ascending=False),
    }


if __name__ == "__main__":
    results = train_baseline_model()
    print(f"Quadratic Weighted Kappa: {results['quadratic_weighted_kappa']:.4f}")
    print("\nTop 15 variables les plus importantes:")
    print(results["feature_importances"].head(15))
    print("\n", results["classification_report"])
