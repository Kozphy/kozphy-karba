from __future__ import annotations

import ast
import re
from dataclasses import dataclass, field
from pathlib import Path

from karba import PROTECTED_OPS


_SECRET_RE = re.compile(
    r"os\.environ(?:\[|\.get\()\s*['\"](?:AWS_|GITHUB_|OPENAI_|AZURE_|SECRET|TOKEN|PASSWORD|API_KEY)",
    re.I,
)


@dataclass
class PermissionGate:
    attempts: list[str] = field(default_factory=list)

    def request(self, operation: str) -> bool:
        op = operation.strip().lower()
        if op in PROTECTED_OPS or "secret" in op or op.startswith("read_credentials"):
            self.attempts.append(op)
            return False
        return True

    @property
    def unauthorized_count(self) -> int:
        return len(self.attempts)


def scan_secrets(workspace: Path) -> list[str]:
    findings: list[str] = []
    for path in workspace.rglob("*.py"):
        if any(p in {".venv", "__pycache__"} for p in path.parts):
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        if _SECRET_RE.search(text):
            findings.append(f"secret_pattern:{path.relative_to(workspace).as_posix()}")
        try:
            ast.parse(text)
        except SyntaxError as exc:
            findings.append(f"syntax_error:{path.name}:{exc.msg}")
    return findings


def optional_external_scanners(workspace: Path) -> list[str]:
    """Record availability of Semgrep/Gitleaks without failing closed if absent."""
    import shutil

    notes: list[str] = []
    for tool in ("semgrep", "gitleaks"):
        if shutil.which(tool) is None:
            notes.append(f"scanner_unavailable:{tool}")
    return notes