"""
Chargement et nettoyage des données de mortalité HMD (Human Mortality Database).

Source : https://www.mortality.org — France, fichiers Mx_1x1.txt (taux de mortalité
centraux) et Exposures_1x1.txt (exposition au risque), format 1x1 (1 an x 1 an d'âge).
Nature : donnée réelle officielle.
"""
from __future__ import annotations

import pandas as pd

from src.common.config_loader import load_config, resolve_path, get_logger

logger = get_logger(__name__)


def _read_hmd_raw_file(path) -> pd.DataFrame:
    """Parse le format texte HMD.

    Plusieurs variantes existent selon la version/le pays téléchargé sur
    mortality.org :
      - avec ou sans ligne de titre avant l'en-tête
      - en-tête avec ou sans guillemets ("Year" "Age" ... vs Year Age ...)
      - âge terminal ouvert soit suffixé "110+", soit signalé par une colonne
        booléenne séparée OpenInterval (TRUE/FALSE)

    On détecte donc la ligne d'en-tête dynamiquement (ligne contenant le mot
    "Year", guillemets ou non) plutôt que de supposer un nombre de lignes
    à sauter ou un format d'âge fixe.
    """
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        lines = f.readlines()

    header_idx = None
    for i, line in enumerate(lines):
        cleaned = line.strip().strip('"').replace('"', "")
        if cleaned.startswith("Year"):
            header_idx = i
            break

    if header_idx is None:
        raise ValueError(
            f"Impossible de trouver la ligne d'en-tête (attendu: un token 'Year') "
            f"dans {path}. Premières lignes du fichier :\n" + "".join(lines[:5])
        )

    df = pd.read_csv(
        path, skiprows=header_idx, sep=r"\s+", na_values=".", quotechar='"'
    )
    df.columns = [c.strip().strip('"') for c in df.columns]

    # Deux conventions possibles pour l'âge terminal ouvert selon la version HMD :
    # soit suffixé "110+" dans la colonne Age, soit une colonne OpenInterval séparée
    # (TRUE/FALSE) avec Age déjà numérique. On gère les deux.
    df["Age"] = df["Age"].astype(str).str.replace("+", "", regex=False).astype(int)
    df["Year"] = df["Year"].astype(int)
    return df


def load_mortality_rates() -> pd.DataFrame:
    """Charge les taux de mortalité centraux Mx (colonnes Female, Male, Total)."""
    cfg = load_config()
    path = resolve_path(cfg["data_sources"]["hmd"]["mortality_rates_file"])
    if not path.exists():
        raise FileNotFoundError(
            f"Fichier HMD introuvable : {path}\n"
            "Dépose Mx_1x1.txt dans data/raw/hmd/ (voir README.md)."
        )
    df = _read_hmd_raw_file(path)
    logger.info(
        "Taux de mortalité HMD chargés : %d lignes, années %d-%d",
        len(df), df["Year"].min(), df["Year"].max(),
    )
    return df


def load_exposures() -> pd.DataFrame:
    """Charge les expositions au risque (population moyenne par âge/année)."""
    cfg = load_config()
    path = resolve_path(cfg["data_sources"]["hmd"]["exposures_file"])
    if not path.exists():
        raise FileNotFoundError(
            f"Fichier HMD introuvable : {path}\n"
            "Dépose Exposures_1x1.txt dans data/raw/hmd/ (voir README.md)."
        )
    df = _read_hmd_raw_file(path)
    logger.info("Expositions HMD chargées : %d lignes", len(df))
    return df


def get_mortality_matrix(sex: str = "Total", age_min: int = 0, age_max: int = 100,
                          year_min: int = 1950, year_max: int = 2023) -> pd.DataFrame:
    """Retourne une matrice Age x Année de taux de mortalité (log Mx), prête pour Lee-Carter.

    sex: "Female", "Male" ou "Total"
    """
    if sex not in {"Female", "Male", "Total"}:
        raise ValueError(f"sex doit être 'Female', 'Male' ou 'Total', reçu: {sex}")

    df = load_mortality_rates()
    df = df[
        (df["Age"] >= age_min) & (df["Age"] <= age_max)
        & (df["Year"] >= year_min) & (df["Year"] <= year_max)
    ]
    matrix = df.pivot(index="Age", columns="Year", values=sex)
    matrix = matrix.sort_index()
    logger.info("Matrice de mortalité construite : %d âges x %d années", *matrix.shape)
    return matrix


if __name__ == "__main__":
    mx = load_mortality_rates()
    print(mx.head())
    matrix = get_mortality_matrix()
    print(f"\nMatrice: {matrix.shape[0]} âges x {matrix.shape[1]} années")
