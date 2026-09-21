"""
Tests des fonctions pures de M10 (normalisation, classement).

Aucune dépendance de données.
"""
import numpy as np
import pandas as pd
import pytest

from src.m10_emerging_risk.actuarial_functions import (
    normalize_frequency, normalize_document_row, dominant_theme,
    rank_themes_across_documents, THEME_COLUMNS,
)


def test_normalize_frequency_basic():
    assert normalize_frequency(count=10, total_words=1000, per=1000) == 10.0
    assert normalize_frequency(count=5, total_words=500, per=1000) == 10.0


def test_normalize_frequency_rejects_zero_words():
    with pytest.raises(ValueError):
        normalize_frequency(count=5, total_words=0)


def test_normalize_makes_documents_comparable():
    # Un document 2x plus long avec 2x plus d'occurrences doit donner la MÊME
    # fréquence normalisée (c'est tout l'intérêt de la normalisation)
    short_doc = normalize_frequency(count=10, total_words=1000)
    long_doc = normalize_frequency(count=20, total_words=2000)
    assert np.isclose(short_doc, long_doc)


def test_dominant_theme_identifies_max():
    row = pd.Series({
        "climat_transition": 1.0, "cyber": 5.0, "geopolitique": 2.0,
        "macro_taux": 0.5, "immobilier_liquidite": 3.0, "ia_digitalisation": 0.1,
    })
    assert dominant_theme(row) == "cyber"


def test_rank_themes_across_documents_orders_descending():
    df = pd.DataFrame({
        "climat_transition": [1.0, 3.0],
        "cyber": [10.0, 2.0],
        "geopolitique": [0.5, 0.5],
        "macro_taux": [2.0, 2.0],
        "immobilier_liquidite": [0.1, 0.1],
        "ia_digitalisation": [0.0, 0.0],
    })
    ranking = rank_themes_across_documents(df)
    assert list(ranking.index) == sorted(THEME_COLUMNS, key=lambda t: -ranking[t])
    assert ranking.iloc[0] >= ranking.iloc[-1]
