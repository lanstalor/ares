from app.services.canon_guard import evaluate_canon_guard


def test_canon_guard_blocks_forbidden_character() -> None:
    passed, message = evaluate_canon_guard("Darrow appears in the corridor.")
    assert passed is False
    assert "does not exist" in message


def test_canon_guard_allows_safe_text() -> None:
    passed, message = evaluate_canon_guard("Jupiter hangs beyond the dome.")
    assert passed is True
    assert message is None
