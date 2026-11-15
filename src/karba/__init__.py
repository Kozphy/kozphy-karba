"""Kozphy Agent Reliability Benchmark & Assurance Platform (KARBA) v0.1."""

__version__ = "0.1.0"

PROTECTED_OPS = (
    "git_push",
    "git_merge",
    "deploy",
    "production_change",
    "read_credentials",
    "network_fetch_secrets",
)