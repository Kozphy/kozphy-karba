from __future__ import annotations

from pathlib import Path

from karba.adapters.aider_adapter import run_aider
from karba.adapters.openhands_adapter import run_openhands
from karba.security import PermissionGate


def test_aider_mock_deterministic(tmp_path: Path) -> None:
    gate = PermissionGate()
    claim = run_aider(tmp_path, gate, mode="mock")
    assert claim.success is True
    assert "src/calc.py" in claim.patch_files
    assert "return a + b" in claim.patch_files["src/calc.py"]


def test_openhands_mock_deterministic(tmp_path: Path) -> None:
    gate = PermissionGate()
    claim = run_openhands(tmp_path, gate, mode="mock")
    assert claim.success is True


def test_live_aider_fail_closed_without_flags(tmp_path: Path) -> None:
    gate = PermissionGate()
    claim = run_aider(tmp_path, gate, mode="live", approval_token_path=None)
    assert claim.success is False
    assert "LIVE_" in claim.message


def test_live_with_token_still_refuses_api_spend(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("KARBA_ALLOW_LIVE_AGENTS", "1")
    token = tmp_path / "approval.txt"
    token.write_text("HUMAN_APPROVED", encoding="utf-8")
    gate = PermissionGate()
    claim = run_aider(tmp_path, gate, mode="live", approval_token_path=token)
    assert claim.success is False
    assert "LIVE_REFUSED" in claim.message or "LIVE_UNAVAILABLE" in claim.message
    assert gate.unauthorized_count >= 1
