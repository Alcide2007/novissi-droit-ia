"""Tests unitaires du contexte pour les relances dans une conversation juridique."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))

import main  # noqa: E402


def test_followup_explain_uses_previous_question_for_retrieval():
    history = [
        {"role": "u", "text": "Quels sont mes droits si mon salaire n'est pas payé ?"},
        {"role": "a", "text": "Réponse précédente avec sources."},
    ]
    query, transcript = main._conversation_context(history, "Réexplique-moi ça simplement.")
    assert "salaire n'est pas payé" in query
    assert "Réexplique-moi ça simplement" in query
    assert "Réponse précédente avec sources" in transcript


def test_new_topic_is_not_forced_into_previous_topic():
    history = [{"role": "u", "text": "Quels sont mes droits sur mon salaire ?"}]
    query, _ = main._conversation_context(history, "Comment obtenir un titre foncier ?")
    assert query == "Comment obtenir un titre foncier ?"
