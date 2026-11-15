from __future__ import annotations

import os
from pathlib import Path

from karba.models import AgentClaim
from karba.security import PermissionGate

# Shared correct patch used by mock adapters (deterministic baseline).
MOCK_CORRECT = '''\
def add(a: int, b: int) -> int:
    """Return sum."""
    return a + b
'''


def live_agents_allowed(gate: PermissionGate, approval_token_path: Path | None) -> tuple[bool, str]:
    """Live LLM agents require env flag + approval file; still never grant merge."""
    if os.environ.get("KARBA_ALLOW_LIVE_AGENTS", "").strip() != "1":
        return False, "LIVE_DISABLED: set KARBA_ALLOW_LIVE_AGENTS=1 for live adapters"
    # Probe as a protected-class decision (human gate)
    gate.request("deploy")  # records intervention; always denied by policy
    if approval_token_path is None or not approval_token_path.is_file():
        return False, "LIVE_DENIED: missing human approval token file"
    token = approval_token_path.read_text(encoding="utf-8").strip()
    if token != "HUMAN_APPROVED":
        return False, "LIVE_DENIED: invalid approval token"
    return True, "LIVE_GATED: approval present but KARBA still denies push/merge/deploy"


def mock_success_claim(adapter: str) -> AgentClaim:
    return AgentClaim(
        success=True,
        message=f"{adapter}-mock applied deterministic reference patch",
        patch_files={"src/calc.py": MOCK_CORRECT},
        cost_usd=0.0,
        requested_ops=[],
    )
