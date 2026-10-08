from pathlib import Path


def test_pasta_app_existe():
    backend = Path(__file__).resolve().parents[1]

    assert (backend / "app").is_dir()
