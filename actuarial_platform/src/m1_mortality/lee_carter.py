"""
Modèle de mortalité Lee-Carter (Lee & Carter, 1992).

log m(x,t) = a(x) + b(x) * k(t) + erreur

où :
  a(x) : niveau moyen de log-mortalité par âge (moyenne sur la période d'ajustement)
  b(x) : sensibilité de chaque âge à l'évolution générale de la mortalité
  k(t) : indice temporel global de mortalité (tendance)

Ajustement par SVD (décomposition en valeurs singulières) sur la matrice
centrée des log-mortalités, comme dans la formulation originale.
Projection de k(t) par marche aléatoire avec dérive (random walk with drift),
approche standard pour Lee-Carter.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

from src.common.config_loader import load_config, get_logger
from src.m1_mortality.loader import get_mortality_matrix

logger = get_logger(__name__)


@dataclass
class LeeCarterResult:
    ages: np.ndarray
    years: np.ndarray
    a_x: pd.Series          # a(x), indexé par âge
    b_x: pd.Series          # b(x), indexé par âge
    k_t: pd.Series          # k(t), indexé par année
    drift: float            # dérive annuelle moyenne de k(t)
    sigma_drift: float      # écart-type des innovations de k(t)
    fitted_log_mx: pd.DataFrame  # log(mx) reconstruit, âge x année


def fit_lee_carter(sex: str = "Total") -> LeeCarterResult:
    """Ajuste le modèle Lee-Carter sur les données HMD chargées via M1/loader.py."""
    cfg = load_config()
    lc_cfg = cfg["lee_carter"]
    year_min, year_max = lc_cfg["fitting_years"]
    age_min, age_max = lc_cfg["fitting_ages"]

    matrix = get_mortality_matrix(
        sex=sex, age_min=age_min, age_max=age_max, year_min=year_min, year_max=year_max
    )
    matrix = matrix.dropna(axis=1, how="any")  # années incomplètes écartées
    log_mx = np.log(matrix)

    a_x = log_mx.mean(axis=1)
    centered = log_mx.sub(a_x, axis=0)

    # SVD : premier vecteur singulier = b(x), première valeur singulière * vecteur = k(t)
    U, S, Vt = np.linalg.svd(centered.values, full_matrices=False)
    b_x_raw = U[:, 0]
    k_t_raw = S[0] * Vt[0, :]

    # Normalisation standard Lee-Carter : somme(b_x) = 1, somme(k_t) = 0
    norm = b_x_raw.sum()
    b_x = b_x_raw / norm
    k_t = k_t_raw * norm

    b_x = pd.Series(b_x, index=matrix.index, name="b_x")
    k_t = pd.Series(k_t, index=matrix.columns, name="k_t")

    # Dérive de k(t) : marche aléatoire avec dérive (moyenne des différences)
    diffs = k_t.diff().dropna()
    drift = diffs.mean()
    sigma_drift = diffs.std()

    fitted_log_mx = a_x.values[:, None] + np.outer(b_x.values, k_t.values)
    fitted_log_mx = pd.DataFrame(fitted_log_mx, index=matrix.index, columns=matrix.columns)

    logger.info(
        "Lee-Carter ajusté (sex=%s) : %d âges, %d années, dérive k(t)=%.4f/an",
        sex, len(a_x), len(k_t), drift,
    )

    return LeeCarterResult(
        ages=matrix.index.values,
        years=matrix.columns.values,
        a_x=a_x, b_x=b_x, k_t=k_t,
        drift=drift, sigma_drift=sigma_drift,
        fitted_log_mx=fitted_log_mx,
    )


def project_mortality(result: LeeCarterResult, horizon: int | None = None,
                       n_simulations: int = 1000, seed: int = 42) -> dict:
    """Projette la mortalité future par simulation de Monte-Carlo sur k(t).

    Retourne un dict avec :
      - 'central': DataFrame des taux projetés centraux (âge x année future)
      - 'simulations': array (n_simulations, n_ages, horizon) pour intervalles de confiance
    """
    cfg = load_config()
    horizon = horizon or cfg["lee_carter"]["forecast_horizon"]
    jump_off_year = cfg["lee_carter"]["jump_off_year"]

    last_k = result.k_t.iloc[-1]
    future_years = np.arange(jump_off_year + 1, jump_off_year + 1 + horizon)

    rng = np.random.default_rng(seed)
    innovations = rng.normal(0, result.sigma_drift, size=(n_simulations, horizon))
    k_paths = last_k + np.cumsum(result.drift + innovations, axis=1)  # (n_sim, horizon)

    # log m(x,t) = a(x) + b(x) * k(t), pour chaque simulation
    # shape finale: (n_simulations, n_ages, horizon)
    log_mx_sims = (
        result.a_x.values[None, :, None]
        + result.b_x.values[None, :, None] * k_paths[:, None, :]
    )
    mx_sims = np.exp(log_mx_sims)

    central_k = last_k + result.drift * np.arange(1, horizon + 1)
    central_log_mx = result.a_x.values[:, None] + np.outer(result.b_x.values, central_k)
    central = pd.DataFrame(np.exp(central_log_mx), index=result.ages, columns=future_years)

    logger.info("Projection Lee-Carter : horizon=%d ans, %d simulations", horizon, n_simulations)

    return {"central": central, "simulations": mx_sims, "years": future_years}


if __name__ == "__main__":
    result = fit_lee_carter(sex="Total")
    print("a(x) [extrait]:\n", result.a_x.head())
    print("\nb(x) [extrait]:\n", result.b_x.head())
    print(f"\nDérive k(t): {result.drift:.4f} par an (sigma={result.sigma_drift:.4f})")

    projection = project_mortality(result, horizon=30)
    print(f"\nMortalité centrale projetée, âge 65, 2030-2035:")
    print(projection["central"].loc[65, 2054:2059] if 65 in projection["central"].index else "âge 65 hors bornes")
