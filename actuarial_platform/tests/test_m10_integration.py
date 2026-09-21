"""
Test d'intégration M10 - vérifie que le rapport complet s'exécute et que
la comparaison EIOPA vs ACPR reflète bien le contraste observé.
"""
from src.m10_emerging_risk.emerging_risk import build_thematic_comparison_report


def test_full_report_runs_and_has_expected_structure():
    report = build_thematic_comparison_report()
    assert len(report["raw_counts"]) == 3
    assert set(report["dominant_theme_by_document"].keys()) == {
        "EIOPA_Financial_Stability_Report",
        "ACPR_Assurance_Vie_2025",
        "ACPR_Situation_Assureurs_S1_2025",
    }


def test_eiopa_more_thematically_dense_than_acpr_on_average():
    """Confirme le contraste observé : EIOPA couvre les 6 thèmes de façon
    bien plus dense que les deux rapports ACPR analysés (qui restent très
    silencieux sur cyber/IA/climat dans ces publications spécifiques)."""
    report = build_thematic_comparison_report()
    by_source = report["comparison_by_source"]
    eiopa_total = by_source.loc["EIOPA"].sum()
    acpr_total = by_source.loc["ACPR"].sum()
    assert eiopa_total > acpr_total
