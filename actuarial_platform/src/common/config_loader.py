"""
Chargement centralisé de la configuration du projet.

Tous les modules (M1 à M15) importent `load_config()` plutôt que de coder
des chemins ou paramètres en dur. Cela garantit un seul point de vérité :
si un chemin de données change, on ne modifie qu'un seul fichier (config.yaml).
"""
from __future__ import annotations

import logging
from pathlib import Path
from functools import lru_cache

import yaml

# Racine du projet = 2 niveaux au-dessus de ce fichier (src/common/ -> racine)
PROJECT_ROOT = Path(__file__).resolve().parents[2]
CONFIG_PATH = PROJECT_ROOT / "config" / "config.yaml"


@lru_cache(maxsize=1)
def load_config() -> dict:
    """Charge config.yaml une seule fois (mise en cache) et le retourne en dict."""
    if not CONFIG_PATH.exists():
        raise FileNotFoundError(
            f"Fichier de configuration introuvable : {CONFIG_PATH}. "
            "Le projet doit être exécuté depuis sa racine, ou config.yaml a été déplacé."
        )
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def resolve_path(relative_path: str) -> Path:
    """Convertit un chemin relatif du config.yaml en chemin absolu utilisable."""
    return PROJECT_ROOT / relative_path


def get_logger(name: str) -> logging.Logger:
    """Logger standardisé pour tous les modules (remplace les print() épars)."""
    cfg = load_config()
    log_cfg = cfg.get("logging", {})
    logging.basicConfig(
        level=log_cfg.get("level", "INFO"),
        format=log_cfg.get("format", "%(asctime)s | %(levelname)s | %(message)s"),
    )
    return logging.getLogger(name)
