"""
M13 - Copilote IA (AI Copilot).

Boucle d'appel à l'API Anthropic avec tool-use, permettant des requêtes en
langage naturel sur les résultats de la plateforme (ex: "quel est le SCR de
taux ?", "quel est le risque de rachat ?").

NÉCESSITE la variable d'environnement ANTHROPIC_API_KEY (voir
https://docs.claude.com pour l'obtenir). Ce module n'a pas pu être testé de
bout en bout dans l'environnement de développement de ce projet (pas de clé
API configurée) - voir tests/test_m13_copilot.py, dont les tests réseau sont
marqués `skipif` en l'absence de clé. La partie sans réseau (définition des
outils, dispatch) est testée séparément dans tools.py.

PÉRIMÈTRE ASSUMÉ : le copilote ne répond QUE sur la base des outils fournis
(SCR, ALM, pricing, lapse, risques émergents, ORSA) - il ne doit pas
halluciner de chiffres. Le prompt système le précise explicitement.
"""
from __future__ import annotations

import json
import os

from src.common.config_loader import get_logger
from src.m13_copilot.tools import TOOL_DEFINITIONS, execute_tool

logger = get_logger(__name__)

SYSTEM_PROMPT = """Tu es le copilote actuariel d'une plateforme de 15 modules \
simulant une compagnie d'assurance-vie (mémoire d'actuariat).

Tu réponds aux questions UNIQUEMENT à partir des outils fournis (SCR, ALM, \
tarification, rachat, risques émergents, projection ORSA) - ne jamais \
inventer de chiffre qui ne provient pas d'un appel d'outil.

Rappelle si pertinent que le portefeuille sous-jacent est SYNTHÉTIQUE \
(contrats fictifs), même si le risque de mortalité et les courbes de taux \
sont basés sur de vraies données (HMD, EIOPA). Reste concis et actuariellement \
rigoureux dans tes réponses."""

DEFAULT_MODEL = "claude-sonnet-4-6"


def query_copilot(question: str, model: str = DEFAULT_MODEL, max_iterations: int = 5) -> str:
    """Pose une question au copilote, avec boucle de tool-use.

    Lève RuntimeError si ANTHROPIC_API_KEY n'est pas configurée, plutôt que
    d'échouer silencieusement ou avec une erreur SDK peu claire.
    """
    if not os.environ.get("ANTHROPIC_API_KEY"):
        raise RuntimeError(
            "ANTHROPIC_API_KEY non configurée. "
            "Définis cette variable d'environnement pour utiliser M13."
        )

    import anthropic

    client = anthropic.Anthropic()
    messages = [{"role": "user", "content": question}]

    for _ in range(max_iterations):
        response = client.messages.create(
            model=model,
            max_tokens=1024,
            system=SYSTEM_PROMPT,
            tools=TOOL_DEFINITIONS,
            messages=messages,
        )

        if response.stop_reason != "tool_use":
            return "".join(block.text for block in response.content if block.type == "text")

        messages.append({"role": "assistant", "content": response.content})
        tool_results = []
        for block in response.content:
            if block.type == "tool_use":
                logger.info("Copilote appelle l'outil : %s(%s)", block.name, block.input)
                result = execute_tool(block.name, block.input)
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": json.dumps(result, default=str, ensure_ascii=False),
                })
        messages.append({"role": "user", "content": tool_results})

    return "Nombre maximal d'itérations d'outils atteint sans réponse finale."


if __name__ == "__main__":
    question = "Quel est le SCR de taux du portefeuille et comment se compare-t-il au SCR mortalité ?"
    print(f"Question : {question}\n")
    print(query_copilot(question))
