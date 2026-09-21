"""
Test d'intégration M15 - exécute l'ensemble de la plateforme (mode quick)
et vérifie que le rapport est complet et exportable.
"""
import json
import os
import pytest

from src.m1_mortality.loader import load_mortality_rates

HMD_AVAILABLE = True
try:
    load_mortality_rates()
except FileNotFoundError:
    HMD_AVAILABLE = False

pytestmark = pytest.mark.skipif(not HMD_AVAILABLE, reason="HMD non présent")


def test_digital_twin_all_modules_succeed_in_quick_mode():
    from src.m15_digital_twin.digital_twin import build_digital_twin
    report = build_digital_twin(quick=True)

    failed = [k for k, ok in report["module_evidence"].items() if not ok]
    assert not failed, f"Modules en échec : {failed}"
    assert (report["compliance"]["status"] == "OK").all()


def test_digital_twin_report_is_exportable_and_valid_json():
    from src.m15_digital_twin.digital_twin import build_digital_twin, export_digital_twin_report
    report = build_digital_twin(quick=True)
    path = export_digital_twin_report(report, filename="test_digital_twin_report.json")

    assert os.path.exists(path)
    with open(path, encoding="utf-8") as f:
        reloaded = json.load(f)  # doit être un JSON valide, sans exception
    assert reloaded["n_policies"] == report["n_policies"]

    os.remove(path)  # nettoyage : ce fichier de test ne doit pas persister
