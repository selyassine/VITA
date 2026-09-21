"""
M10 - Fonctions pures : normalisation et classement de fréquences thématiques.

Même principe que les autres modules : aucune dépendance de données,
testable seule.
"""
from __future__ import annotations

import pandas as pd

THEME_COLUMNS = [
    "climat_transition", "cyber", "geopolitique",
    "macro_taux", "immobilier_liquidite", "ia_digitalisation",
]


def normalize_frequency(count: int, total_words: int, per: int = 1000) -> float:
    """Fréquence normalisée : occurrences pour `per` mots (défaut 1000).

    Indispensable pour comparer des documents de longueurs très différentes
    (ex: un rapport de 20 000 mots vs une synthèse de 4 000 mots) - un
    comptage brut favoriserait toujours le document le plus long.
    """
    if total_words <= 0:
        raise ValueError("total_words doit être strictement positif.")
    return (count / total_words) * per


def normalize_document_row(row: pd.Series, per: int = 1000) -> pd.Series:
    """Applique normalize_frequency à toutes les colonnes thématiques d'une ligne."""
    return pd.Series(
        {theme: normalize_frequency(row[theme], row["nb_mots"], per) for theme in THEME_COLUMNS}
    )


def dominant_theme(normalized_row: pd.Series) -> str:
    """Retourne le thème le plus fréquent (fréquence normalisée) d'un document."""
    themes_only = normalized_row[THEME_COLUMNS] if set(THEME_COLUMNS).issubset(normalized_row.index) else normalized_row
    return themes_only.idxmax()


def rank_themes_across_documents(normalized_df: pd.DataFrame) -> pd.Series:
    """Classe les thèmes par fréquence normalisée MOYENNE sur tous les documents
    (permet d'identifier quels risques dominent l'ensemble du corpus)."""
    return normalized_df[THEME_COLUMNS].mean(axis=0).sort_values(ascending=False)
