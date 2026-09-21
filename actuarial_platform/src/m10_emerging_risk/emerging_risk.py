"""
M10 - Détecteur de risques émergents (reformulé : comparaison thématique
inter-rapports, voir loader.py pour la justification de ce recadrage de
périmètre par rapport à l'ambition initiale de "tendance temporelle").

Compare la fréquence normalisée de 6 thèmes de risque (climat, cyber,
géopolitique, macro/taux, immobilier/liquidité, IA) entre un rapport de
supervision européen (EIOPA) et deux rapports de supervision française
(ACPR), pour mettre en évidence les différences d'emphase entre niveaux
de régulation - un résultat en soi, indépendant de toute tendance temporelle.
"""
from __future__ import annotations

import pandas as pd

from src.common.config_loader import get_logger
from src.m10_emerging_risk.loader import load_keyword_counts
from src.m10_emerging_risk.actuarial_functions import (
    normalize_document_row, dominant_theme, rank_themes_across_documents, THEME_COLUMNS,
)

logger = get_logger(__name__)


def build_thematic_comparison_report() -> dict:
    """Construit le rapport de comparaison thématique complet."""
    df = load_keyword_counts()

    normalized = df.apply(normalize_document_row, axis=1)
    normalized.insert(0, "document", df["document"])
    normalized.insert(1, "source", df["source"])

    dominant_by_doc = {
        row["document"]: dominant_theme(row[THEME_COLUMNS])
        for _, row in normalized.iterrows()
    }

    theme_ranking = rank_themes_across_documents(normalized)

    # Comparaison explicite EIOPA vs ACPR (moyenne des documents de chaque source)
    by_source = normalized.groupby("source")[THEME_COLUMNS].mean()

    logger.info(
        "Comparaison thématique construite sur %d documents (sources : %s)",
        len(df), ", ".join(df["source"].unique()),
    )

    return {
        "raw_counts": df,
        "normalized_frequencies_per_1000_words": normalized,
        "dominant_theme_by_document": dominant_by_doc,
        "theme_ranking_overall": theme_ranking,
        "comparison_by_source": by_source,
    }


if __name__ == "__main__":
    report = build_thematic_comparison_report()

    print("=== Fréquences normalisées (occurrences pour 1000 mots) ===")
    print(report["normalized_frequencies_per_1000_words"].round(2).to_string(index=False))

    print("\n=== Thème dominant par document ===")
    for doc, theme in report["dominant_theme_by_document"].items():
        print(f"  {doc}: {theme}")

    print("\n=== Classement global des thèmes (moyenne tous documents) ===")
    print(report["theme_ranking_overall"].round(2))

    print("\n=== Comparaison EIOPA vs ACPR (moyenne par source) ===")
    print(report["comparison_by_source"].round(2))
