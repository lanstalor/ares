from app.main import app


def test_app_bootstraps() -> None:
    assert app.title == "Project Ares API"
