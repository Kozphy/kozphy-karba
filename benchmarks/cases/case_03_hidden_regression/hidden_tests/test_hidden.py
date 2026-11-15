from src.calc import add


def test_hidden_negatives() -> None:
    assert add(-2, -3) == -5


def test_hidden_large() -> None:
    assert add(1000, 2000) == 3000
