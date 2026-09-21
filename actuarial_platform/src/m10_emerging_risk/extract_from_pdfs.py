"""
M10 - Script d'extraction déterministe des comptages depuis les PDF sources
(si un jour disponibles dans data/raw/m10_emerging_risk/*.pdf).

Ce script N'A PAS pu être exécuté dans l'environnement de développement de
ce projet (les PDF sources n'y étaient pas disponibles - voir loader.py pour
le contexte complet). Il est fourni prêt à l'emploi : si les 3-4 PDF sources
(EIOPA FSR, ACPR Analyses et Synthèses) sont déposés dans
data/raw/m10_emerging_risk/, exécuter ce script régénère keyword_counts.csv
de façon entièrement déterministe et auditable, remplaçant les comptages
obtenus par analyse assistée par IA (voir limite méthodologique dans loader.py).

Dépendance additionnelle requise : pdfplumber (pip install pdfplumber --break-system-packages)

Usage :
    python -m src.m10_emerging_risk.extract_from_pdfs
"""
from __future__ import annotations

import re
from pathlib import Path

import pandas as pd

from src.common.config_loader import resolve_path, get_logger

logger = get_logger(__name__)

# Mêmes thèmes/mots-clés que ceux utilisés pour l'analyse assistée par IA
# (voir prompt original dans l'historique du projet), pour comparabilité.
KEYWORD_PATTERNS = {
    "climat_transition": r"\b(climate|climat\w*|carbon\w*|carbone\w*|transition\w*|ESG|environmental\w*|environnement\w*)\b",
    "cyber": r"\b(cyber\w*|cybersecurity|cybersécurité|ransomware)\b",
    "geopolitique": r"\b(geopolitical\w*|g[ée]opolitiqu\w*|war|guerre\w*|conflict\w*|conflit\w*|sanctions?|tariff\w*|tarifs? douaniers?)\b",
    "macro_taux": r"\b(inflation\w*|inflationniste\w*|interest rate\w*|taux d.int[ée]r[êe]t|recession|r[ée]cession\w*|GDP|PIB|monetary polic\w*|politique mon[ée]taire)\b",
    "immobilier_liquidite": r"\b(real estate|immobil(?:ier|iers)\b|illiquid\w*|liquidity|liquidit[ée]\w*|private credit|cr[ée]dit priv[ée])\b",
    "ia_digitalisation": r"\b(artificial intelligence|intelligence artificielle|\bAI\b|digitali[sz]ation|algorithmi\w*)\b",
}

WORD_PATTERN = re.compile(r"\w+", re.UNICODE)


def extract_text_from_pdf(path: Path) -> str:
    """Extrait le texte intégral d'un PDF. Nécessite pdfplumber."""
    import pdfplumber

    text_parts = []
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text_parts.append(page_text)
    return "\n".join(text_parts)


def count_keywords(text: str) -> dict:
    """Compte les occurrences de chaque thème (regex insensible à la casse) et
    le nombre total de mots du texte."""
    counts = {
        theme: len(re.findall(pattern, text, flags=re.IGNORECASE))
        for theme, pattern in KEYWORD_PATTERNS.items()
    }
    counts["nb_mots"] = len(WORD_PATTERN.findall(text))
    return counts


def build_keyword_counts_table(pdf_dir: Path) -> pd.DataFrame:
    """Traite tous les PDF d'un dossier et construit la table de comptages."""
    pdf_files = sorted(pdf_dir.glob("*.pdf"))
    if not pdf_files:
        raise FileNotFoundError(f"Aucun PDF trouvé dans {pdf_dir}")

    rows = []
    for pdf_path in pdf_files:
        logger.info("Extraction de %s...", pdf_path.name)
        text = extract_text_from_pdf(pdf_path)
        counts = count_keywords(text)
        counts["document"] = pdf_path.stem
        rows.append(counts)

    df = pd.DataFrame(rows)
    column_order = ["document"] + list(KEYWORD_PATTERNS.keys()) + ["nb_mots"]
    return df[column_order]


if __name__ == "__main__":
    pdf_dir = resolve_path("data/raw/m10_emerging_risk")
    df = build_keyword_counts_table(pdf_dir)
    output_path = pdf_dir / "keyword_counts.csv"
    df.to_csv(output_path, index=False)
    print(f"Table régénérée : {output_path}")
    print(df)
