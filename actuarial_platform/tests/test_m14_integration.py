"""
Test d'intégration M14 - mode autonome (calcule ses propres preuves).
"""
import pytest

from src.m1_mortality.loader import load_mortality_rates

HMD_AVAILABLE = True
try:
    load_mortality_rates()
except FileNotFoundError:
    HMD_AVAILABLE = False

pytestmark = pytest.mark.skipif(not HMD_AVAILABLE, reason="HMD non présent")


def test_autonomous_compliance_check_marks_all_items_ok():
    """Avec toutes les données réelles disponibles, tous les modules
    devraient produire une preuve valide (tous les items 'OK')."""
    from src.m14_compliance.compliance import check_compliance_requirements
    report = check_compliance_requirements(quick=True)
    missing = report[report["status"] == "Manquant"]
    assert missing.empty, f"Rubriques manquantes inattendues : {missing['item'].tolist()}"
