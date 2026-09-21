"""
M15 - Jumeau numérique (Digital Twin).

Aucune donnée brute propre : exécute et compile M1 à M14 en un rapport
unique, avec le portefeuille synthétique comme backbone commun. C'est le
module d'orchestration final de la plateforme.

PRINCIPE DE CONCEPTION (dependency injection, évite les recalculs) :
M15 calcule chaque module UNE SEULE FOIS, puis transmet directement les
résultats de succès/échec à M14 (evaluate_checklist) plutôt que de laisser
M14 tout recalculer une seconde fois de son côté - un seul passage complet
sur l'ensemble de la plateforme, comme le ferait une vraie orchestration de
production plutôt qu'un empilement de scripts indépendants.

ROBUSTESSE : chaque module est exécuté dans un bloc isolé (même principe que
M12/M14) - un échec localisé n'empêche pas la compilation du reste du rapport.

Mode quick=True (défaut) : réduit le nombre de simulations Monte-Carlo (M7)
et l'horizon ORSA (M11), et n'entraîne pas le modèle M6 (juste les
statistiques du jeu de données) - pour un temps d'exécution raisonnable.
Mode quick=False : calculs complets, plus long.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone

import pandas as pd
import numpy as np

from src.common.config_loader import load_config, resolve_path, get_logger
from src.common.synthetic_portfolio import load_synthetic_portfolio
from src.m14_compliance.actuarial_functions import evaluate_checklist

logger = get_logger(__name__)


def _to_jsonable(obj):
    """Convertit récursivement DataFrames/Series/numpy en structures JSON-compatibles."""
    if isinstance(obj, pd.DataFrame):
        return obj.to_dict(orient="records")
    if isinstance(obj, pd.Series):
        return obj.to_dict()
    if isinstance(obj, dict):
        return {k: _to_jsonable(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_to_jsonable(v) for v in obj]
    if isinstance(obj, (np.integer, np.floating)):
        return obj.item()
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    return obj


def build_digital_twin(portfolio: pd.DataFrame | None = None, quick: bool = True) -> dict:
    """Exécute l'ensemble de la plateforme et compile un rapport unique.

    Retourne un dict avec deux clés principales :
      - 'results' : les sorties de chaque module (structure imbriquée)
      - 'compliance' : la checklist M14 évaluée sur les succès/échecs observés
    """
    portfolio = portfolio if portfolio is not None else load_synthetic_portfolio()
    results: dict = {}
    evidence: dict[str, bool] = {}

    def _run(key: str, evidence_key: str, func):
        try:
            results[key] = func()
            evidence[evidence_key] = True
        except Exception as exc:
            logger.warning("Module '%s' non exécuté dans le digital twin : %s", key, exc)
            results[key] = None
            evidence[evidence_key] = False

    # --- M1 : mortalité ---
    def _m1():
        from src.m1_mortality.lee_carter import fit_lee_carter
        result = fit_lee_carter(sex="Total")
        return {"drift_k_t": result.drift, "n_ages": len(result.ages), "n_years": len(result.years)}
    _run("m1_mortality", "m1_mortality_computed", _m1)

    # --- M2 : pricing ---
    def _m2():
        from src.m2_pricing.pricing import compute_pure_premium
        priced = compute_pure_premium(portfolio)
        valid = priced.dropna(subset=["prime_pure_eur"])
        return {
            "n_contrats_tarifes": int(len(valid)),
            "prime_pure_totale_eur": float(valid["prime_pure_eur"].sum()),
        }
    _run("m2_pricing", "m2_pricing_computed", _m2)

    # --- M3 : provisionnement ---
    def _m3():
        from src.m3_reserving.reserving import compute_total_best_estimate
        return {"best_estimate_eur": compute_total_best_estimate(portfolio)}
    _run("m3_reserving", "m3_reserving_computed", _m3)

    # --- M4 : SCR ---
    def _m4():
        from src.m4_scr.scr import compute_full_scr_report
        return compute_full_scr_report(portfolio)
    _run("m4_scr", "m4_scr_computed", _m4)

    # --- M5 : rachat ---
    def _m5():
        from src.m5_lapse.loader import load_retention_with_label
        df = load_retention_with_label()
        return {"taux_resiliation_global": float(df["lapsed"].mean())}
    _run("m5_lapse", "m5_lapse_computed", _m5)

    # --- M6 : underwriting ---
    def _m6():
        from src.m6_underwriting.loader import load_prudential_raw
        df = load_prudential_raw()
        result = {"n_individus": int(len(df)), "n_colonnes": int(df.shape[1])}
        if not quick:
            from src.m6_underwriting.model import train_baseline_model
            model_result = train_baseline_model()
            result["quadratic_weighted_kappa"] = float(model_result["quadratic_weighted_kappa"])
        return result
    _run("m6_underwriting", "m6_underwriting_computed", _m6)

    # --- M7 : longévité ---
    def _m7():
        from src.m7_longevity.longevity import simulate_longevity_capital_impact
        n_sim = 20 if quick else 200
        sim = simulate_longevity_capital_impact(portfolio, n_simulations=n_sim)
        return {
            "best_estimate_mean_simulated": sim["best_estimate_mean_simulated"],
            "value_at_risk_longevity": sim["value_at_risk_longevity"],
        }
    _run("m7_longevity", "m7_longevity_computed", _m7)

    # --- M8 : ALM ---
    def _m8():
        from src.m8_alm.alm import compute_full_alm_report
        report = compute_full_alm_report(portfolio)
        return {k: v for k, v in report.items()}
    _run("m8_alm", "m8_alm_computed", _m8)

    # --- M9 : optimizer ---
    def _m9():
        from src.m9_optimizer.optimizer import optimize_portfolio_loading
        return optimize_portfolio_loading(portfolio)
    _run("m9_optimizer", "m9_optimizer_computed", _m9)

    # --- M10 : risques émergents ---
    def _m10():
        from src.m10_emerging_risk.emerging_risk import build_thematic_comparison_report
        report = build_thematic_comparison_report()
        return {
            "dominant_theme_by_document": report["dominant_theme_by_document"],
            "theme_ranking_overall": report["theme_ranking_overall"],
        }
    _run("m10_emerging_risk", "m10_emerging_risk_computed", _m10)

    # --- M11 : ORSA ---
    def _m11():
        from src.m11_orsa.orsa import orsa_projection
        cfg = load_config()
        horizon = 2 if quick else cfg["m11_orsa"]["projection_horizon_years"]
        return orsa_projection(portfolio, horizon_years=horizon)
    _run("m11_orsa", "m11_orsa_computed", _m11)

    compliance_report = evaluate_checklist(evidence)

    logger.info(
        "Digital Twin construit : %d/%d modules exécutés avec succès",
        sum(evidence.values()), len(evidence),
    )

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "quick_mode": quick,
        "n_policies": int(len(portfolio)),
        "results": results,
        "module_evidence": evidence,
        "compliance": compliance_report,
    }


def export_digital_twin_report(report: dict, filename: str = "digital_twin_report.json") -> str:
    """Exporte le rapport complet en JSON dans outputs/reports/."""
    output_dir = resolve_path("outputs/reports")
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / filename

    serializable = _to_jsonable(report)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(serializable, f, indent=2, ensure_ascii=False, default=str)

    logger.info("Rapport Digital Twin exporté : %s", path)
    return str(path)


if __name__ == "__main__":
    report = build_digital_twin(quick=True)
    path = export_digital_twin_report(report)
    print(f"Rapport exporté : {path}")
    print(f"\nModules exécutés avec succès : {sum(report['module_evidence'].values())}/{len(report['module_evidence'])}")
    for key, ok in report["module_evidence"].items():
        print(f"  {key}: {'OK' if ok else 'ÉCHEC'}")
