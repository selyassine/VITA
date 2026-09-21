"""
M14 - IA de conformité réglementaire (checklist documentaire).

Aucune donnée brute propre : exécute (ou reçoit déjà exécutés) les modules
M2, M4, M5, M6, M7, M8, M9, M10, M11 pour vérifier qu'une preuve chiffrée
existe pour chaque rubrique de la checklist (voir actuarial_functions.py).

Conçu pour accepter un dict de preuves DÉJÀ CALCULÉ (paramètre `evidence`) -
typiquement fourni par M15 (Digital Twin) qui exécute déjà tous les modules
une fois pour son propre rapport, évitant de tout recalculer une seconde
fois ici. Si aucune preuve n'est fournie, ce module calcule lui-même un jeu
de preuves minimal (mode autonome), avec gestion d'échec isolée par module
(même principe que M12 : un module en échec n'empêche pas d'évaluer les autres).
"""
from __future__ import annotations

from src.common.config_loader import get_logger
from src.common.synthetic_portfolio import load_synthetic_portfolio
from src.m14_compliance.actuarial_functions import evaluate_checklist

logger = get_logger(__name__)


def compute_module_evidence(portfolio=None, quick: bool = True) -> dict[str, bool]:
    """Exécute chaque module et enregistre s'il a produit un résultat
    exploitable (mode autonome - voir docstring du module pour le mode
    "preuves déjà fournies", à préférer si M15 a déjà tout calculé).

    quick=True : réduit le nombre de simulations Monte-Carlo de M7 pour un
    contrôle rapide (n_simulations=20 au lieu de 200) - suffisant pour
    vérifier que le module PRODUIT un résultat, pas pour un chiffre définitif.
    """
    portfolio = portfolio if portfolio is not None else load_synthetic_portfolio()
    evidence = {}

    checks = {
        "m2_pricing_computed": lambda: __import__(
            "src.m2_pricing.pricing", fromlist=["compute_pure_premium"]
        ).compute_pure_premium(portfolio) is not None,
        "m4_scr_computed": lambda: __import__(
            "src.m4_scr.scr", fromlist=["compute_scr_biometric"]
        ).compute_scr_biometric(portfolio)["scr_vie_biometrique"] >= 0,
        "m5_lapse_computed": lambda: __import__(
            "src.m5_lapse.loader", fromlist=["load_retention_with_label"]
        ).load_retention_with_label() is not None,
        "m6_underwriting_computed": lambda: __import__(
            "src.m6_underwriting.loader", fromlist=["load_prudential_raw"]
        ).load_prudential_raw() is not None,
        "m7_longevity_computed": lambda: __import__(
            "src.m7_longevity.longevity", fromlist=["simulate_longevity_capital_impact"]
        ).simulate_longevity_capital_impact(
            portfolio, n_simulations=20 if quick else 200
        ) is not None,
        "m8_alm_computed": lambda: __import__(
            "src.m8_alm.alm", fromlist=["compute_full_alm_report"]
        ).compute_full_alm_report(portfolio) is not None,
        "m9_optimizer_computed": lambda: __import__(
            "src.m9_optimizer.optimizer", fromlist=["optimize_portfolio_loading"]
        ).optimize_portfolio_loading(portfolio) is not None,
        "m10_emerging_risk_computed": lambda: __import__(
            "src.m10_emerging_risk.emerging_risk", fromlist=["build_thematic_comparison_report"]
        ).build_thematic_comparison_report() is not None,
        "m11_orsa_computed": lambda: __import__(
            "src.m11_orsa.orsa", fromlist=["orsa_projection"]
        ).orsa_projection(portfolio, horizon_years=1) is not None,
    }

    for key, check_fn in checks.items():
        try:
            evidence[key] = bool(check_fn())
        except Exception as exc:
            logger.warning("Preuve '%s' non obtenue : %s", key, exc)
            evidence[key] = False

    return evidence


def check_compliance_requirements(evidence: dict[str, bool] | None = None,
                                   portfolio=None, quick: bool = True):
    """Retourne le DataFrame de checklist évalué. Si `evidence` n'est pas
    fourni, le calcule en mode autonome (voir compute_module_evidence)."""
    if evidence is None:
        evidence = compute_module_evidence(portfolio, quick=quick)
    return evaluate_checklist(evidence)


if __name__ == "__main__":
    report = check_compliance_requirements()
    print(report[["item", "module_source", "status"]].to_string(index=False))
    n_ok = (report["status"] == "OK").sum()
    print(f"\n{n_ok}/{len(report)} rubriques documentées.")
