from src.calc import add


def test_add_basic() -> None:
    assert add(2, 3) == 5


def test_add_zero() -> None:
    assert add(0, 4) == 4
