"""
Tests unitaires du module M1 (mortalité / Lee-Carter).

Nécessite les fichiers HMD dans data/raw/hmd/ pour s'exécuter
(voir README.md - section "Données requises").
"""
import numpy as np
import pytest

from src.m1_mortality.loader import load_mortality_rates, get_mortality_matrix
from src.m1_mortality.lee_carter import fit_lee_carter, project_mortality


HMD_AVAILABLE = True
try:
    load_mortality_rates()
except FileNotFoundError:
    HMD_AVAILABLE = False

pytestmark = pytest.mark.skipif(
    not HMD_AVAILABLE, reason="Fichiers HMD non présents dans data/raw/hmd/"
)


def test_mortality_rates_loaded_correctly():
    df = load_mortality_rates()
    assert not df.empty
    assert {"Year", "Age", "Female", "Male", "Total"}.issubset(df.columns)
    assert df["Year"].min() >= 1800
    assert df["Age"].min() == 0


def test_mortality_matrix_shape():
    matrix = get_mortality_matrix(sex="Total", age_min=0, age_max=100, year_min=2000, year_max=2020)
    assert matrix.shape[0] == 101  # âges 0 à 100 inclus
    assert matrix.shape[1] <= 21   # années 2000 à 2020 inclus


def test_lee_carter_fit_produces_valid_parameters():
    result = fit_lee_carter(sex="Total")
    # b(x) doit sommer à 1 (contrainte de normalisation standard)
    assert np.isclose(result.b_x.sum(), 1.0, atol=1e-6)
    # k(t) doit sommer à ~0 (contrainte de normalisation standard)
    assert np.isclose(result.k_t.sum(), 0.0, atol=1e-3)
    # a(x) ne doit contenir aucune valeur infinie/NaN
    assert result.a_x.notna().all()
    assert np.isfinite(result.a_x.values).all()


def test_lee_carter_mortality_generally_decreases_with_drift():
    result = fit_lee_carter(sex="Total")
    # La dérive de k(t) doit être négative en tendance longue (progrès médical)
    assert result.drift < 0, "La dérive de k(t) devrait être négative sur longue période"


def test_projection_output_shape():
    result = fit_lee_carter(sex="Total")
    projection = project_mortality(result, horizon=10, n_simulations=100)
    assert projection["central"].shape[1] == 10
    assert projection["simulations"].shape == (100, len(result.ages), 10)
    # Les taux de mortalité projetés doivent rester positifs
    assert (projection["central"].values > 0).all()
