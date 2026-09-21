"""
M4 - Chargement des courbes de taux EIOPA (Risk-Free Rate term structures).

Source : EIOPA, classeur officiel mensuel Term_Structures.xlsx.
Nature : donnee reelle officielle.

Structure du classeur (verifiee sur fichier reel EIOPA_RFR_20260531) :
  - Feuille "RFR_spot_no_VA" : courbe spot par pays, sans ajustement de
    volatilite. Ligne 2 = noms de pays (colonne C = "Euro"), lignes 11+ =
    donnees (colonne B = maturite en annees, colonnes suivantes = taux).
  - Feuille "Shocks" : facteurs de choc reglementaires RELATIFS par maturite
    (a_up(t), a_down(t)), lignes 11+, colonnes D="Shock downwards",
    E="Shock upwards". Ce sont les vrais parametres publies par EIOPA pour
    le sous-module de risque de taux de la formule standard.

IMPORTANT - choix méthodologique documenté :
Les feuilles "Spot_NO_VA_shock_UP/DOWN" du classeur contiennent des valeurs
qui se sont averees suspectes a l'inspection (plates a 1% sur toutes les
maturites et tous les pays, sans en-tete de colonne pays) - vraisemblablement
des cellules de formule inter-feuilles non recalculees a l'enregistrement du
fichier. Plutot que de leur faire confiance, ce module recalcule lui-meme la
courbe choquee a partir de la courbe de base (RFR_spot_no_VA) et des vrais
facteurs de choc relatifs publiés dans la feuille "Shocks", selon la formule
standard Solvabilite II :
    taux_choque_up(t)   = taux_spot(t) * (1 + a_up(t))
    taux_choque_down(t) = taux_spot(t) * (1 - a_down(t))
Cette approche est plus robuste et plus transparente (les facteurs utilises
sont directement traçables et audités depuis les données EIOPA sources)
qu'une dépendance à des cellules pré-calculées potentiellement obsolètes.
A mentionner explicitement dans le mémoire comme un choix méthodologique
assumé, pas une donnée manquante.
"""
from __future__ import annotations

from functools import lru_cache
from pathlib import Path

import openpyxl
import pandas as pd

from src.common.config_loader import load_config, resolve_path, get_logger

logger = get_logger(__name__)

SHEET_BASE = "RFR_spot_no_VA"
SHEET_SHOCKS = "Shocks"


def _find_eiopa_workbook_path() -> Path:
    cfg = load_config()
    rfr_dir: Path = resolve_path(cfg["data_sources"]["eiopa"]["rfr_dir"])
    if not rfr_dir.exists():
        raise FileNotFoundError(
            f"Dossier introuvable : {rfr_dir}\n"
            "Dézippe EIOPA_RFR_20260531.zip dans data/raw/eiopa/ (voir README.md)."
        )
    candidates = list(rfr_dir.glob("*Term_Structures.xlsx"))
    if not candidates:
        # Recherche récursive au cas où le zip aurait été extrait dans un sous-dossier
        candidates = list(rfr_dir.rglob("*Term_Structures.xlsx"))
    if not candidates:
        raise FileNotFoundError(
            f"Aucun fichier '*Term_Structures.xlsx' trouvé sous {rfr_dir}."
        )
    return candidates[0]


@lru_cache(maxsize=1)
def _load_workbook():
    path = _find_eiopa_workbook_path()
    logger.info("Chargement du classeur EIOPA : %s", path.name)
    return openpyxl.load_workbook(path, data_only=True, read_only=True)


def _find_country_column(ws, country: str) -> int:
    """Trouve l'index de colonne (0-based) d'un pays dans la ligne d'en-tête (ligne 2)."""
    header_row = next(ws.iter_rows(min_row=2, max_row=2, values_only=True))
    for idx, value in enumerate(header_row):
        if value == country:
            return idx
    raise ValueError(
        f"Pays '{country}' introuvable dans l'en-tête EIOPA. "
        f"Pays disponibles : {[v for v in header_row if v]}"
    )


def load_base_spot_curve(country: str = "Euro") -> pd.Series:
    """Charge la courbe spot de base (sans ajustement de volatilité) pour un pays.

    Retourne une Series indexée par maturité (1 à 150 ans), valeurs = taux spot.
    """
    wb = _load_workbook()
    ws = wb[SHEET_BASE]
    col_idx = _find_country_column(ws, country)

    maturities, rates = [], []
    for row in ws.iter_rows(min_row=11, values_only=True):
        maturity = row[1]
        if maturity is None:
            break
        maturities.append(int(maturity))
        rates.append(row[col_idx])

    series = pd.Series(rates, index=pd.Index(maturities, name="maturity"), name=f"spot_{country}")
    logger.info("Courbe spot de base chargée pour %s : %d maturités (1 à %d ans)",
                country, len(series), series.index.max())
    return series


def load_shock_factors() -> pd.DataFrame:
    """Charge les facteurs de choc relatifs réglementaires (a_up, a_down) par maturité.

    Retourne un DataFrame indexé par maturité, colonnes 'shock_up' et 'shock_down'.
    """
    wb = _load_workbook()
    ws = wb[SHEET_SHOCKS]

    maturities, shocks_down, shocks_up = [], [], []
    for row in ws.iter_rows(min_row=11, values_only=True):
        maturity = row[1]
        if maturity is None:
            break
        maturities.append(int(maturity))
        shocks_down.append(row[3])
        shocks_up.append(row[4])

    df = pd.DataFrame(
        {"shock_down": shocks_down, "shock_up": shocks_up},
        index=pd.Index(maturities, name="maturity"),
    )
    logger.info("Facteurs de choc de taux chargés : %d maturités", len(df))
    return df


def get_shocked_curves(country: str = "Euro") -> pd.DataFrame:
    """Calcule les courbes choquées (up/down) à partir de la courbe de base
    et des facteurs de choc officiels (voir docstring du module pour la
    justification de ce recalcul plutôt que d'utiliser les feuilles
    Spot_..._shock_UP/DOWN directement).

    Retourne un DataFrame indexé par maturité, colonnes :
      spot_central, spot_shock_up, spot_shock_down
    """
    base = load_base_spot_curve(country)
    shocks = load_shock_factors()

    df = pd.DataFrame({"spot_central": base}).join(shocks, how="inner")
    df["spot_shock_up"] = df["spot_central"] * (1 + df["shock_up"])
    df["spot_shock_down"] = df["spot_central"] * (1 - df["shock_down"])

    return df[["spot_central", "spot_shock_up", "spot_shock_down"]]


if __name__ == "__main__":
    curves = get_shocked_curves("Euro")
    print(curves.head(10))
    print("...")
    print(curves.tail(5))
