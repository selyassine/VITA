"""
M12 - Dashboard exécutif.

Aucune donnée brute propre : orchestre M1, M4, M8, M9, M10, M11 pour produire
un ensemble de visualisations de synthèse (PNG), destinées à une direction
ou à l'annexe graphique du mémoire.

PRINCIPE DE ROBUSTESSE : chaque graphique est généré dans un bloc isolé
(try/except). Si un module sous-jacent échoue (ex: données manquantes),
le dashboard continue de produire les AUTRES graphiques plutôt que d'échouer
entièrement - comportement attendu d'un vrai tableau de bord de production,
qui doit rester utile même en cas de panne partielle d'une source.
"""
from __future__ import annotations

import matplotlib
matplotlib.use("Agg")  # génération sans interface graphique (headless)
import matplotlib.pyplot as plt
import numpy as np

from src.common.config_loader import load_config, resolve_path, get_logger

logger = get_logger(__name__)


def _save_figure(fig, filename: str) -> str:
    output_dir = resolve_path("outputs/figures")
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / filename
    fig.savefig(path, dpi=120, bbox_inches="tight")
    plt.close(fig)
    logger.info("Graphique sauvegardé : %s", path)
    return str(path)


def plot_mortality_curve() -> str | None:
    """Courbe de mortalité centrale projetée (M1), quelques âges clés."""
    from src.m1_mortality.lee_carter import fit_lee_carter, project_mortality

    result = fit_lee_carter(sex="Total")
    projection = project_mortality(result, horizon=30)
    central = projection["central"]

    fig, ax = plt.subplots(figsize=(8, 5))
    for age in [30, 50, 70, 90]:
        if age in central.index:
            ax.plot(central.columns, central.loc[age], label=f"Âge {age}")
    ax.set_yscale("log")
    ax.set_xlabel("Année")
    ax.set_ylabel("Taux de mortalité projeté (log)")
    ax.set_title("M1 — Mortalité centrale projetée (Lee-Carter)")
    ax.legend()
    return _save_figure(fig, "m1_mortality_curve.png")


def plot_scr_breakdown() -> str | None:
    """Répartition du SCR biométrique (M4)."""
    from src.m4_scr.scr import compute_scr_biometric

    report = compute_scr_biometric()
    labels = ["Mortalité", "Longévité", "Total (agrégé)"]
    values = [report["scr_mortality"], report["scr_longevity"], report["scr_vie_biometrique"]]

    fig, ax = plt.subplots(figsize=(7, 5))
    ax.bar(labels, values, color=["#c0392b", "#2980b9", "#2c3e50"])
    ax.set_ylabel("SCR (EUR)")
    ax.set_title("M4 — Répartition du SCR vie biométrique")
    for i, v in enumerate(values):
        ax.text(i, v, f"{v:,.0f}", ha="center", va="bottom", fontsize=9)
    return _save_figure(fig, "m4_scr_breakdown.png")


def plot_alm_duration_gap() -> str | None:
    """Comparaison duration actif vs passif (M8)."""
    from src.m8_alm.alm import compute_full_alm_report

    report = compute_full_alm_report()
    labels = ["Actif (obligataire pondéré)", "Passif (prestations)"]
    values = [report["blended_asset_duration"], report["liability_duration"]]

    fig, ax = plt.subplots(figsize=(7, 5))
    ax.bar(labels, values, color=["#27ae60", "#8e44ad"])
    ax.set_ylabel("Duration (années)")
    ax.set_title("M8 — Écart de duration actif / passif")
    for i, v in enumerate(values):
        ax.text(i, v, f"{v:.1f} ans", ha="center", va="bottom", fontsize=9)
    return _save_figure(fig, "m8_alm_duration_gap.png")


def plot_margin_curve() -> str | None:
    """Courbe de marge en fonction du chargement (M9) - ne nécessite aucune
    donnée réelle, la forme unimodale est illustrée pour un contrat type."""
    from src.m9_optimizer.actuarial_functions import margin_per_policy, optimal_loading_closed_form

    cfg = load_config()
    elasticity = cfg["m9_optimizer"]["lapse_elasticity"]
    loadings = np.linspace(1.001, 3.0, 200)
    margins = margin_per_policy(pure_premium=1000, ax=10, loading=loadings,
                                 lapse_elasticity=elasticity)
    optimum = optimal_loading_closed_form(elasticity)

    fig, ax = plt.subplots(figsize=(7, 5))
    ax.plot(loadings, margins, color="#16a085")
    ax.axvline(optimum, color="#e67e22", linestyle="--", label=f"Optimum = {optimum:.2f}")
    ax.set_xlabel("Chargement commercial")
    ax.set_ylabel("Marge technique (contrat type)")
    ax.set_title("M9 — Arbitrage marge / rachat")
    ax.legend()
    return _save_figure(fig, "m9_margin_curve.png")


def plot_emerging_risk_comparison() -> str | None:
    """Comparaison thématique EIOPA vs ACPR (M10)."""
    from src.m10_emerging_risk.emerging_risk import build_thematic_comparison_report

    report = build_thematic_comparison_report()
    by_source = report["comparison_by_source"]

    fig, ax = plt.subplots(figsize=(9, 5))
    by_source.T.plot(kind="bar", ax=ax)
    ax.set_ylabel("Occurrences pour 1000 mots")
    ax.set_title("M10 — Comparaison thématique EIOPA vs ACPR")
    ax.legend(title="Source")
    plt.xticks(rotation=30, ha="right")
    return _save_figure(fig, "m10_emerging_risk_comparison.png")


def plot_orsa_trajectory() -> str | None:
    """Trajectoire du ratio de couverture SCR sur l'horizon ORSA (M11)."""
    from src.m11_orsa.orsa import orsa_projection

    projection = orsa_projection()

    fig, ax = plt.subplots(figsize=(7, 5))
    ax.plot(projection["year"], projection["solvency_ratio"], marker="o", color="#2c3e50")
    ax.axhline(1.0, color="#c0392b", linestyle="--", label="Seuil réglementaire (100%)")
    ax.set_xlabel("Année de projection")
    ax.set_ylabel("Ratio de couverture SCR")
    ax.set_title("M11 — Trajectoire de solvabilité (run-off)")
    ax.legend()
    return _save_figure(fig, "m11_orsa_trajectory.png")


def build_executive_dashboard() -> dict:
    """Génère l'ensemble des visualisations disponibles. Retourne un dict
    {nom_graphique: chemin_ou_None} - None si le graphique a échoué (voir
    logs pour la raison), sans bloquer les autres graphiques."""
    plots = {
        "mortality_curve": plot_mortality_curve,
        "scr_breakdown": plot_scr_breakdown,
        "alm_duration_gap": plot_alm_duration_gap,
        "margin_curve": plot_margin_curve,
        "emerging_risk_comparison": plot_emerging_risk_comparison,
        "orsa_trajectory": plot_orsa_trajectory,
    }
    results = {}
    for name, func in plots.items():
        try:
            results[name] = func()
        except Exception as exc:
            logger.warning("Graphique '%s' non généré : %s", name, exc)
            results[name] = None
    return results


if __name__ == "__main__":
    results = build_executive_dashboard()
    print("Résultat de la génération du dashboard :")
    for name, path in results.items():
        status = path if path else "ÉCHEC (voir logs)"
        print(f"  {name}: {status}")
