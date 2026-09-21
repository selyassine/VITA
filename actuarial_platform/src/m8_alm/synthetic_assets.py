"""
M8 - Génération du portefeuille obligataire synthétique (actif).

Comme pour le portefeuille de passif (src/common/synthetic_portfolio.py),
aucune vraie donnée de bilan d'assureur n'est publique (secret commercial).
Le portefeuille obligataire est donc généré une fois, avec une graine fixe,
et persisté sur disque - à ne jamais régénérer avec une seed différente en
cours de projet (cohérence inter-runs).

Calibration : notional uniforme sur toutes les obligations, mis à l'échelle
UNE SEULE FOIS pour que la valeur actualisée totale (à la courbe EIOPA
centrale) corresponde exactement à la valeur cible demandée (mise à l'échelle
exacte, sans recherche itérative - la VAP est linéaire au notional pour des
maturités/coupons fixés).
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from src.common.config_loader import load_config, resolve_path, get_logger
from src.m8_alm.actuarial_functions import present_value

logger = get_logger(__name__)


def generate_bond_maturities(n_bonds: int, maturity_min: int, maturity_max: int,
                              seed: int) -> np.ndarray:
    """Répartit les maturités des obligations uniformément sur l'intervalle
    demandé (portefeuille obligataire diversifié en échéances, pratique
    standard de gestion actif-passif)."""
    rng = np.random.default_rng(seed)
    return rng.integers(maturity_min, maturity_max + 1, size=n_bonds)


def build_bond_cash_flows(maturities: np.ndarray, coupon_rate: float,
                           notional_per_bond: np.ndarray, horizon: int) -> np.ndarray:
    """Construit le vecteur agrégé des flux (coupons + principal) de tout le
    portefeuille obligataire, indexé par année 0..horizon."""
    cash_flows = np.zeros(horizon + 1)
    for maturity, notional in zip(maturities, notional_per_bond):
        cash_flows[1:maturity + 1] += coupon_rate * notional  # coupons annuels
        cash_flows[maturity] += notional  # remboursement du principal à l'échéance
    return cash_flows


def generate_synthetic_bond_portfolio(target_market_value: float, spot_curve: pd.Series,
                                       force_regenerate: bool = False) -> pd.DataFrame:
    """Génère (ou charge depuis le cache) le portefeuille obligataire, mis à
    l'échelle pour que sa VAP (courbe centrale) égale target_market_value.
    """
    cfg = load_config()
    alm_cfg = cfg["m8_alm"]
    output_path = resolve_path("data/processed/synthetic_bonds.csv")

    if output_path.exists() and not force_regenerate:
        logger.info("Portefeuille obligataire chargé depuis le cache : %s", output_path)
        return pd.read_csv(output_path)

    n_bonds = alm_cfg["n_bonds"]
    maturities = generate_bond_maturities(
        n_bonds, alm_cfg["bond_maturity_min"], alm_cfg["bond_maturity_max"], alm_cfg["seed"]
    )
    coupon_rate = alm_cfg["bond_coupon_rate"]

    # Notional uniforme initial (1 unité par obligation), puis mise à l'échelle
    # exacte pour atteindre la valeur cible (VAP linéaire au notional).
    unit_notional = np.ones(n_bonds)
    horizon = int(maturities.max())
    unit_cash_flows = build_bond_cash_flows(maturities, coupon_rate, unit_notional, horizon)
    unit_pv = present_value(unit_cash_flows, spot_curve)

    scale = target_market_value / unit_pv if unit_pv > 0 else 0.0
    notional_per_bond = unit_notional * scale

    df = pd.DataFrame({
        "bond_id": [f"BOND{1000 + i}" for i in range(n_bonds)],
        "maturity_years": maturities,
        "coupon_rate": coupon_rate,
        "notional_eur": np.round(notional_per_bond, 2),
    })

    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)
    logger.info(
        "Portefeuille obligataire synthétique généré : %d obligations, VAP cible=%.0f EUR",
        n_bonds, target_market_value,
    )
    return df
