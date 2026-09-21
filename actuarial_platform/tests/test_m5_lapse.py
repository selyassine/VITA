"""
Tests du module M5 (lapse / rachat).

Nécessite le CSV Retention dans data/raw/kaggle_retention/.
"""
import numpy as np
import pandas as pd
import pytest

from src.m5_lapse.loader import load_retention_raw, derive_lapse_label, load_retention_with_label

RETENTION_AVAILABLE = True
try:
    load_retention_raw()
except FileNotFoundError:
    RETENTION_AVAILABLE = False

pytestmark = pytest.mark.skipif(
    not RETENTION_AVAILABLE, reason="CSV Retention non présent dans data/raw/kaggle_retention/"
)


def test_retention_data_loaded():
    df = load_retention_raw()
    assert not df.empty
    assert "policy_start_date" in df.columns


def test_derived_label_achieves_target_rate_closely():
    df = load_retention_raw()
    result = derive_lapse_label(df, target_rate=0.175, seed=42)
    achieved = result["lapsed"].mean()
    # La calibration doit être précise (recherche exacte de racine, pas une approximation)
    assert abs(achieved - 0.175) < 0.02


def test_derived_label_is_binary():
    df = load_retention_raw()
    result = derive_lapse_label(df)
    assert set(result["lapsed"].unique()).issubset({0, 1})


def test_derived_label_reproducible_with_same_seed():
    df = load_retention_raw()
    result1 = derive_lapse_label(df, seed=123)
    result2 = derive_lapse_label(df, seed=123)
    assert (result1["lapsed"] == result2["lapsed"]).all()


def test_term_life_has_higher_lapse_rate_than_whole_life():
    # Vérifie que la règle de dérivation produit bien l'effet attendu
    # (Temporaire > Vie Entière en taux de résiliation), pas juste un taux global correct
    df = load_retention_with_label(seed=42)
    rates = df.groupby("policy_type")["lapsed"].mean()
    assert rates["Term Life"] > rates["Whole Life"]


def test_anciennete_and_ratio_columns_are_sane():
    df = load_retention_with_label()
    assert (df["anciennete_years"] > 0).all()
    assert (df["premium_to_income_ratio"] > 0).all()
    assert (df["lapse_probability"].between(0, 1)).all()


def test_different_target_rate_shifts_achieved_rate():
    df = load_retention_raw()
    low = derive_lapse_label(df, target_rate=0.08, seed=1)
    high = derive_lapse_label(df, target_rate=0.30, seed=1)
    assert low["lapsed"].mean() < high["lapsed"].mean()
