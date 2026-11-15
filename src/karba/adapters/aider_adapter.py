from __future__ import annotations

import shutil
import time
from pathlib import Path

from karba.adapters.common import live_agents_allowed, mock_success_claim
from karba.models import AgentClaim
from karba.security import PermissionGate


def run_aider(
    case_dir: Path,
    gate: PermissionGate,
    *,
    mode: str = "mock",
    approval_token_path: Path | None = None,
) -> AgentClaim:
    """Aider adapter. Default mock is deterministic. Live mode is fail-closed."""
    t0 = time.perf_counter()
    if mode in ("mock", "aider-mock", "aider"):
        # Default "aider" id uses mock unless live explicitly requested via mode=live
        if mode != "live":
            claim = mock_success_claim("aider")
            claim.elapsed_seconds = time.perf_counter() - t0
            return claim

    allowed, reason = live_agents_allowed(gate, approval_token_path)
    if not allowed:
        claim = AgentClaim(success=False, message=reason, cost_usd=0.0)
        claim.elapsed_seconds = time.perf_counter() - t0
        return claim

    if shutil.which("aider") is None:
        claim = AgentClaim(success=False, message="LIVE_UNAVAILABLE: aider not on PATH", cost_usd=0.0)
        claim.elapsed_seconds = time.perf_counter() - t0
        return claim

    # Refuse to auto-invoke network LLM in this MVP without further explicit ops —
    # keep fail-closed even when flags are set (no silent API spend).
    gate.request("network_fetch_secrets")
    claim = AgentClaim(
        success=False,
        message=(
            "LIVE_REFUSED: aider binary found but KARBA MVP does not auto-spend LLM APIs; "
            "use aider-mock for deterministic evaluation"
        ),
        requested_ops=["network_fetch_secrets"],
        cost_usd=0.0,
    )
    claim.elapsed_seconds = time.perf_counter() - t0
    return claim
