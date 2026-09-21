"""
Tests des fonctions pures de M14 (checklist de conformité documentaire).

Aucune dépendance de données.
"""
from src.m14_compliance.actuarial_functions import evaluate_checklist, CHECKLIST


def test_evaluate_checklist_all_true():
    evidence = {entry["evidence_key"]: True for entry in CHECKLIST}
    result = evaluate_checklist(evidence)
    assert (result["status"] == "OK").all()


def test_evaluate_checklist_all_false():
    evidence = {entry["evidence_key"]: False for entry in CHECKLIST}
    result = evaluate_checklist(evidence)
    assert (result["status"] == "Manquant").all()


def test_evaluate_checklist_missing_key_treated_as_false():
    # Aucune clé fournie du tout -> tout doit être "Manquant", pas d'erreur
    result = evaluate_checklist({})
    assert (result["status"] == "Manquant").all()


def test_evaluate_checklist_partial_evidence():
    evidence = {"m4_scr_computed": True}
    result = evaluate_checklist(evidence)
    ok_items = result[result["status"] == "OK"]
    assert set(ok_items["evidence_key"]) == {"m4_scr_computed"}


def test_checklist_has_no_duplicate_items():
    items = [entry["item"] for entry in CHECKLIST]
    assert len(items) == len(set(items))
