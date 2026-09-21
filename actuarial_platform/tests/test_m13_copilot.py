"""
Tests de M13 (copilote).

- Tests des définitions d'outils : toujours exécutés, aucune dépendance.
- Tests du dispatch : nécessitent HMD/EIOPA/Retention (les données sous-jacentes).
- Tests de la boucle API : skip si ANTHROPIC_API_KEY absente (jamais
  configurée dans l'environnement de développement de ce projet).
"""
import os
import pytest

from src.m13_copilot.tools import TOOL_DEFINITIONS, TOOL_DISPATCH, execute_tool
from src.m1_mortality.loader import load_mortality_rates

HMD_AVAILABLE = True
try:
    load_mortality_rates()
except FileNotFoundError:
    HMD_AVAILABLE = False

API_KEY_AVAILABLE = bool(os.environ.get("ANTHROPIC_API_KEY"))


def test_tool_definitions_have_required_fields():
    for tool in TOOL_DEFINITIONS:
        assert "name" in tool
        assert "description" in tool
        assert "input_schema" in tool
        assert tool["input_schema"]["type"] == "object"


def test_every_tool_definition_has_a_dispatch_entry():
    defined_names = {tool["name"] for tool in TOOL_DEFINITIONS}
    dispatch_names = set(TOOL_DISPATCH.keys())
    assert defined_names == dispatch_names


def test_execute_unknown_tool_returns_error_not_exception():
    result = execute_tool("outil_qui_n_existe_pas", {})
    assert "error" in result


@pytest.mark.skipif(not HMD_AVAILABLE, reason="HMD non présent")
def test_execute_scr_summary_tool():
    result = execute_tool("get_scr_summary", {})
    assert "error" not in result
    assert "scr_vie_biometrique" in result


@pytest.mark.skipif(not HMD_AVAILABLE, reason="HMD non présent")
def test_execute_orsa_projection_tool_with_input():
    result = execute_tool("get_orsa_projection", {"horizon_years": 1})
    assert "error" not in result
    assert len(result) == 2  # années 0 et 1


@pytest.mark.skipif(not API_KEY_AVAILABLE, reason="ANTHROPIC_API_KEY non configurée")
def test_query_copilot_end_to_end():
    from src.m13_copilot.copilot import query_copilot
    answer = query_copilot("Quel est le SCR mortalité du portefeuille ?")
    assert isinstance(answer, str) and len(answer) > 0


def test_query_copilot_raises_clear_error_without_api_key(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    from src.m13_copilot.copilot import query_copilot
    with pytest.raises(RuntimeError, match="ANTHROPIC_API_KEY"):
        query_copilot("Une question quelconque")
