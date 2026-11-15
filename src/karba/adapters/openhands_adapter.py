from __future__ import annotations

import shutil
import time
from pathlib import Path

from karba.adapters.common import live_agents_allowed, mock_success_claim
from karba.models import AgentClaim
from karba.security import PermissionGate


def run_openhands(
    case_dir: Path,
    gate: PermissionGate,
    *,
    mode: str = "mock",
    approval_token_path: Path | None = None,
) -> AgentClaim:
    """OpenHands adapter. Default mock is deterministic. Live mode is fail-closed."""
    t0 = time.perf_counter()
    if mode != "live":
        claim = mock_success_claim("openhands")
        claim.elapsed_seconds = time.perf_counter() - t0
        return claim

    allowed, reason = live_agents_allowed(gate, approval_token_path)
    if not allowed:
        claim = AgentClaim(success=False, message=reason, cost_usd=0.0)
        claim.elapsed_seconds = time.perf_counter() - t0
        return claim

    # Detect common OpenHands CLI entrypoints without executing them.
    has_bin = shutil.which("openhands") is not None or shutil.which("python") is not None
    if not has_bin:
        claim = AgentClaim(success=False, message="LIVE_UNAVAILABLE: openhands not found", cost_usd=0.0)
        claim.elapsed_seconds = time.perf_counter() - t0
        return claim

    gate.request("network_fetch_secrets")
    claim = AgentClaim(
        success=False,
        message=(
            "LIVE_REFUSED: OpenHands live invoke blocked in KARBA MVP (no autonomous API spend); "
            "use openhands-mock for deterministic evaluation"
        ),
        requested_ops=["network_fetch_secrets"],
        cost_usd=0.0,
    )
    claim.elapsed_seconds = time.perf_counter() - t0
    return claim
