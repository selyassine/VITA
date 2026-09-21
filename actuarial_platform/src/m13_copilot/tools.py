"""
M13 - Définitions des outils et dispatch (partie TESTABLE SANS RÉSEAU).

Séparation volontaire entre :
  - CE FICHIER : quels outils existent, quel schéma, quelle fonction Python
    ils appellent - entièrement testable sans appel API, puisqu'aucune
    requête réseau n'est faite ici.
  - copilot.py : la boucle d'appel à l'API Anthropic elle-même (tool-use
    loop), qui NÉCESSITE une clé API et ne peut pas être testée dans un
    environnement sans accès réseau/clé (voir tests/test_m13_copilot.py -
    les tests de CE fichier tournent toujours, ceux de copilot.py sont skip
    sans clé API).
"""
from __future__ import annotations

from typing import Any

from src.common.synthetic_portfolio import load_synthetic_portfolio

TOOL_DEFINITIONS = [
    {
        "name": "get_scr_summary",
        "description": (
            "Retourne le SCR (Solvency Capital Requirement) du portefeuille : "
            "SCR mortalité, SCR longévité, SCR de taux, et le Best Estimate central."
        ),
        "input_schema": {"type": "object", "properties": {}, "required": []},
    },
    {
        "name": "get_pricing_summary",
        "description": (
            "Retourne un résumé de la tarification du portefeuille : nombre "
            "de contrats tarifés et prime pure totale."
        ),
        "input_schema": {"type": "object", "properties": {}, "required": []},
    },
    {
        "name": "get_alm_summary",
        "description": (
            "Retourne le résumé ALM : duration de l'actif et du passif, écart "
            "de duration, sensibilité du NAV aux chocs de taux EIOPA."
        ),
        "input_schema": {"type": "object", "properties": {}, "required": []},
    },
    {
        "name": "get_lapse_summary",
        "description": "Retourne le taux de résiliation global dérivé (M5).",
        "input_schema": {"type": "object", "properties": {}, "required": []},
    },
    {
        "name": "get_emerging_risk_summary",
        "description": (
            "Retourne le thème de risque dominant par document et le "
            "classement global des thèmes émergents (EIOPA vs ACPR)."
        ),
        "input_schema": {"type": "object", "properties": {}, "required": []},
    },
    {
        "name": "get_orsa_projection",
        "description": (
            "Retourne la projection ORSA pluriannuelle (run-off) : Best "
            "Estimate, SCR et ratio de couverture par année."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "horizon_years": {
                    "type": "integer",
                    "description": "Nombre d'années à projeter (défaut : valeur de config.yaml).",
                }
            },
            "required": [],
        },
    },
]


def _get_scr_summary(**kwargs) -> dict:
    from src.m4_scr.scr import compute_full_scr_report
    return compute_full_scr_report(load_synthetic_portfolio())


def _get_pricing_summary(**kwargs) -> dict:
    from src.m2_pricing.pricing import compute_pure_premium
    priced = compute_pure_premium(load_synthetic_portfolio())
    valid = priced.dropna(subset=["prime_pure_eur"])
    return {
        "n_contrats_tarifes": int(len(valid)),
        "prime_pure_totale_eur": float(valid["prime_pure_eur"].sum()),
    }


def _get_alm_summary(**kwargs) -> dict:
    from src.m8_alm.alm import compute_full_alm_report
    return compute_full_alm_report(load_synthetic_portfolio())


def _get_lapse_summary(**kwargs) -> dict:
    from src.m5_lapse.loader import load_retention_with_label
    df = load_retention_with_label()
    return {"taux_resiliation_global": float(df["lapsed"].mean())}


def _get_emerging_risk_summary(**kwargs) -> dict:
    from src.m10_emerging_risk.emerging_risk import build_thematic_comparison_report
    report = build_thematic_comparison_report()
    return {
        "dominant_theme_by_document": report["dominant_theme_by_document"],
        "theme_ranking_overall": report["theme_ranking_overall"].to_dict(),
    }


def _get_orsa_projection(horizon_years: int | None = None, **kwargs) -> dict:
    from src.m11_orsa.orsa import orsa_projection
    projection = orsa_projection(load_synthetic_portfolio(), horizon_years=horizon_years)
    return projection.to_dict(orient="records")


TOOL_DISPATCH = {
    "get_scr_summary": _get_scr_summary,
    "get_pricing_summary": _get_pricing_summary,
    "get_alm_summary": _get_alm_summary,
    "get_lapse_summary": _get_lapse_summary,
    "get_emerging_risk_summary": _get_emerging_risk_summary,
    "get_orsa_projection": _get_orsa_projection,
}


def execute_tool(name: str, tool_input: dict) -> dict[str, Any]:
    """Exécute un outil par son nom, avec gestion d'erreur explicite.

    Retourne toujours un dict avec soit le résultat, soit une clé 'error' -
    jamais d'exception qui remonterait jusqu'à la boucle d'appel API (une
    erreur d'outil doit être communicable au modèle, pas planter le programme).
    """
    if name not in TOOL_DISPATCH:
        return {"error": f"Outil inconnu : {name}"}
    try:
        return TOOL_DISPATCH[name](**tool_input)
    except Exception as exc:
        return {"error": f"Erreur lors de l'exécution de {name} : {exc}"}
