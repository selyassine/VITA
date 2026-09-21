"""
Test d'intégration M12 - vérifie que le dashboard génère les graphiques
attendus (ceux dont les données sous-jacentes sont disponibles).
"""
import os
import pytest

from src.m1_mortality.loader import load_mortality_rates

HMD_AVAILABLE = True
try:
    load_mortality_rates()
except FileNotFoundError:
    HMD_AVAILABLE = False

pytestmark = pytest.mark.skipif(not HMD_AVAILABLE, reason="HMD non présent")


def test_dashboard_generates_all_figures_when_data_available():
    from src.m12_dashboard.dashboard import build_executive_dashboard
    results = build_executive_dashboard()

    assert len(results) == 6
    for name, path in results.items():
        assert path is not None, f"Le graphique '{name}' a échoué (voir logs)"
        assert os.path.exists(path)
        assert os.path.getsize(path) > 0


def test_margin_curve_never_fails_even_without_hmd():
    # Ce graphique ne dépend d'aucune donnée réelle (voir docstring de
    # plot_margin_curve) - doit toujours réussir, même isolément.
    from src.m12_dashboard.dashboard import plot_margin_curve
    path = plot_margin_curve()
    assert path is not None
    import os
    assert os.path.exists(path)
