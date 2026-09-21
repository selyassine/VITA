"""
M14 - Checklist documentaire ORSA / Solvabilité II Pilier 2 (fonctions pures).

IMPORTANT - ce que ce module N'EST PAS : ce n'est PAS un avis juridique, ni
une certification de conformité réglementaire réelle. C'est une checklist
d'AUTO-VÉRIFICATION DOCUMENTAIRE : "la plateforme a-t-elle produit une
preuve chiffrée pour chacune des grandes rubriques qu'un rapport ORSA/SFCR
est censé couvrir (guidelines EIOPA sur l'ORSA) ?" - un contrôle de
complétude, pas une interprétation juridique complexe.

La checklist elle-même est une fonction PURE (mapping statique), testable
sans aucune donnée. L'évaluation (evaluate_checklist) prend en entrée un
dict de "preuves" déjà calculées ailleurs (voir compliance.py) plutôt que de
recalculer quoi que ce soit elle-même - séparation stricte entre la logique
de checklist (ici) et l'obtention des preuves (orchestration).
"""
from __future__ import annotations

import pandas as pd

CHECKLIST = [
    {
        "item": "Profil de risque biométrique",
        "evidence_key": "m4_scr_computed",
        "module_source": "M4",
        "description": "SCR mortalité/longévité calculé et décomposé par sous-module.",
    },
    {
        "item": "Besoin global de solvabilité",
        "evidence_key": "m4_scr_computed",
        "module_source": "M4",
        "description": "Ratio de couverture SCR calculé (fonds propres / SCR).",
    },
    {
        "item": "Évaluation prospective pluriannuelle",
        "evidence_key": "m11_orsa_computed",
        "module_source": "M11",
        "description": "Projection du besoin de capital sur plusieurs années (run-off).",
    },
    {
        "item": "Politique de gestion du capital / tarification",
        "evidence_key": "m9_optimizer_computed",
        "module_source": "M9",
        "description": "Analyse du chargement commercial et de son impact sur le SCR.",
    },
    {
        "item": "Sensibilité au risque de taux",
        "evidence_key": "m8_alm_computed",
        "module_source": "M8",
        "description": "Duration actif/passif et sensibilité du NAV aux chocs de taux EIOPA.",
    },
    {
        "item": "Sensibilité aux risques biométriques (approche stochastique)",
        "evidence_key": "m7_longevity_computed",
        "module_source": "M7",
        "description": "VaR 99.5% par simulation Monte-Carlo des trajectoires de mortalité.",
    },
    {
        "item": "Risque de rachat (lapse)",
        "evidence_key": "m5_lapse_computed",
        "module_source": "M5",
        "description": "Modélisation du risque de résiliation (label dérivé, voir limites M5).",
    },
    {
        "item": "Risque de souscription / tarification",
        "evidence_key": "m2_pricing_computed",
        "module_source": "M2",
        "description": "Prime pure calculée par équivalence actuarielle.",
    },
    {
        "item": "Classification du risque à la souscription",
        "evidence_key": "m6_underwriting_computed",
        "module_source": "M6",
        "description": "Modèle de classification du risque assuré (Prudential).",
    },
    {
        "item": "Veille des risques émergents",
        "evidence_key": "m10_emerging_risk_computed",
        "module_source": "M10",
        "description": "Comparaison thématique de rapports de supervision (EIOPA/ACPR).",
    },
]


def evaluate_checklist(evidence: dict[str, bool]) -> pd.DataFrame:
    """Évalue la checklist à partir d'un dict de preuves {evidence_key: bool}.

    Toute clé absente du dict `evidence` est traitée comme False (preuve non
    disponible) plutôt que de lever une erreur - permet d'évaluer une
    checklist partielle (ex: certains modules non exécutés dans cette session).
    """
    rows = []
    for entry in CHECKLIST:
        status = "OK" if evidence.get(entry["evidence_key"], False) else "Manquant"
        rows.append({**entry, "status": status})
    return pd.DataFrame(rows)
