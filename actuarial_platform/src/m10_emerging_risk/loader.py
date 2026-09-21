"""
M10 - Chargement de la table de comptages de mots-clés thématiques.

Source des comptages : rapports officiels EIOPA (Financial Stability Report)
et ACPR (Analyses et Synthèses), extraits et comptés via analyse assistée
par IA (voir note méthodologique ci-dessous), PAS par un script déterministe
propre à ce projet — limite à documenter explicitement dans le mémoire.

LIMITE MÉTHODOLOGIQUE IMPORTANTE :
Contrairement à HMD/EIOPA(taux)/Kaggle, les comptages de mots-clés de ce
fichier n'ont PAS été extraits par un script Python audité dans ce dépôt :
ils proviennent d'une analyse manuelle assistée par un autre modèle de
langage sur le texte des PDF (voir data/raw/m10_emerging_risk/keyword_counts.csv).
C'est une limite de reproductibilité stricte à mentionner dans le mémoire.
Si les PDF sources sont un jour déposés dans data/raw/m10_emerging_risk/,
un script d'extraction propre (pdfplumber + regex) peut être ajouté pour
regénérer ce fichier de façon entièrement déterministe et auditable -
voir extract_from_pdfs.py (squelette prêt, non exécuté faute de PDF source
dans l'environnement de développement).

AUTRE LIMITE DE PÉRIMÈTRE : les 3 documents disponibles ne sont PAS des
éditions successives d'une même publication (2 rapports ACPR différents +
1 seule édition EIOPA) - il ne s'agit donc PAS d'une analyse de TENDANCE
temporelle comme initialement envisagé, mais d'une COMPARAISON THÉMATIQUE
entre niveaux de supervision (européen EIOPA vs français ACPR). Une vraie
analyse de tendance nécessiterait au moins 2 éditions successives du même
rapport (ex: EIOPA FSR juin 2025 + décembre 2025).
"""
from __future__ import annotations

import pandas as pd

from src.common.config_loader import load_config, resolve_path, get_logger

logger = get_logger(__name__)


def load_keyword_counts() -> pd.DataFrame:
    """Charge la table de comptages thématiques par document."""
    cfg = load_config()
    path = resolve_path("data/raw/m10_emerging_risk/keyword_counts.csv")
    if not path.exists():
        raise FileNotFoundError(
            f"Fichier introuvable : {path}\n"
            "keyword_counts.csv doit être présent dans data/raw/m10_emerging_risk/."
        )
    df = pd.read_csv(path)
    logger.info("Comptages thématiques chargés : %d documents", len(df))
    return df
