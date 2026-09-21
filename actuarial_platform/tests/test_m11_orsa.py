"""
Tests des fonctions pures de M11 (vieillissement du portefeuille).

Aucune dépendance de données (HMD/EIOPA) : portefeuille fabriqué à la main.
"""
import pandas as pd
import pytest

from src.m11_orsa.actuarial_functions import project_portfolio_aging


def _tiny_portfolio() -> pd.DataFrame:
    return pd.DataFrame({
        "policy_id": ["A", "B"],
        "age_actuel": [30, 50],
        "anciennete_annees": [2, 10],
        "produit": ["Temporaire Décès", "Vie Entière"],
    })


def test_aging_increments_age_and_anciennete():
    portfolio = _tiny_portfolio()
    aged = project_portfolio_aging(portfolio, years_forward=5)
    assert list(aged["age_actuel"]) == [35, 55]
    assert list(aged["anciennete_annees"]) == [7, 15]


def test_aging_zero_years_returns_unchanged_ages():
    portfolio = _tiny_portfolio()
    aged = project_portfolio_aging(portfolio, years_forward=0)
    assert list(aged["age_actuel"]) == list(portfolio["age_actuel"])


def test_aging_does_not_mutate_original_portfolio():
    portfolio = _tiny_portfolio()
    original_ages = portfolio["age_actuel"].copy()
    project_portfolio_aging(portfolio, years_forward=10)
    assert list(portfolio["age_actuel"]) == list(original_ages)


def test_aging_rejects_negative_years():
    with pytest.raises(ValueError):
        project_portfolio_aging(_tiny_portfolio(), years_forward=-1)
