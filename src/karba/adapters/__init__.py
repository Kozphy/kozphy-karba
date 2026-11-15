"""Optional coding-agent adapters. Live modes are fail-closed without explicit approval."""

from karba.adapters.aider_adapter import run_aider
from karba.adapters.openhands_adapter import run_openhands

__all__ = ["run_aider", "run_openhands"]
