"""
Tests unitaires du module M6 (underwriting / Prudential).

Nécessite train.csv dans data/raw/kaggle_prudential/.
"""
import pytest

from src.m6_underwriting.loader import load_prudential_raw, get_feature_groups, TARGET_COLUMN

PRUDENTIAL_AVAILABLE = True
try:
    load_prudential_raw()
except FileNotFoundError:
    PRUDENTIAL_AVAILABLE = False

pytestmark = pytest.mark.skipif(
    not PRUDENTIAL_AVAILABLE, reason="train.csv non présent dans data/raw/kaggle_prudential/"
)


def test_prudential_data_loaded():
    df = load_prudential_raw()
    assert not df.empty
    assert TARGET_COLUMN in df.columns


def test_response_values_in_expected_range():
    df = load_prudential_raw()
    assert df[TARGET_COLUMN].min() >= 1
    assert df[TARGET_COLUMN].max() <= 8


def test_feature_groups_cover_known_families():
    df = load_prudential_raw()
    groups = get_feature_groups(df)
    assert len(groups["medical_keyword"]) == 48  # connu : 48 mots-clés médicaux binaires
    assert "Ins_Age" in groups["biometrics"]


def test_no_duplicate_ids():
    df = load_prudential_raw()
    assert df["Id"].is_unique
