from agents.explainer import generate_explanation


def test_explanation_contains_action():

    result = generate_explanation(
        0.95,
        "CRITICAL",
        "BLOCK",
    )

    assert "BLOCK" in result
    assert "Critical" in result
