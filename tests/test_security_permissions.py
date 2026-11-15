from karba.security import PermissionGate


def test_protected_ops_denied() -> None:
    gate = PermissionGate()
    assert gate.request("git_push") is False
    assert gate.request("deploy") is False
    assert gate.request("read_credentials") is False
    assert len(gate.attempts) == 3


def test_benign_allowed() -> None:
    gate = PermissionGate()
    assert gate.request("run_pytest") is True
    assert gate.attempts == []