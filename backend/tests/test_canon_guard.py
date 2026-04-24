from app.services.canon_guard import evaluate_canon_guard


def test_canon_guard_blocks_forbidden_character() -> None:
    passed, message = evaluate_canon_guard("Darrow appears in the corridor.")
    assert passed is False
    assert "does not exist" in message


def test_canon_guard_allows_safe_text() -> None:
    passed, message = evaluate_canon_guard("Jupiter hangs beyond the dome.")
    assert passed is True
    assert message is None


def test_canon_guard_allows_west_virginia_as_place() -> None:
    passed, message = evaluate_canon_guard("The convoy passed through West Virginia Depot.")
    assert passed is True
    assert message is None


def test_canon_guard_allows_virginia_as_place() -> None:
    passed, message = evaluate_canon_guard("Virginia Depot lies beyond the dome.")
    assert passed is True
    assert message is None


def test_canon_guard_blocks_virginia_au_augustus() -> None:
    passed, message = evaluate_canon_guard("Virginia au Augustus stepped from the shadows.")
    assert passed is False
    assert "does not exist" in message


def test_canon_guard_blocks_forbidden_character_mixed_case() -> None:
    passed, message = evaluate_canon_guard("DARROW appeared on the comms.")
    assert passed is False
    assert "does not exist" in message


def test_canon_guard_allows_eo_as_substring() -> None:
    passed, message = evaluate_canon_guard("The theory of hegemony collapses under scrutiny.")
    assert passed is True
    assert message is None


def test_canon_guard_blocks_standalone_eo() -> None:
    passed, message = evaluate_canon_guard("Eo sang once beneath the mines.")
    assert passed is False
    assert "does not exist" in message
