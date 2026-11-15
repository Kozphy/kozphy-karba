from __future__ import annotations

import re
import shutil
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal

from karba.hashing import sha256_bytes
from karba.security import scan_secrets

Isolation = Literal["host", "container", "auto"]


@dataclass
class VerifyResult:
    ok: bool
    pytest_ok: bool
    ruff_ok: bool
    security_ok: bool
    hidden_ok: bool
    isolation: str = "host"
    network: str = "host"
    commands: list[dict] = field(default_factory=list)
    findings: list[str] = field(default_factory=list)
    test_summary: dict[str, int] = field(
        default_factory=lambda: {"passed": 0, "failed": 0, "errors": 0, "skipped": 0}
    )


def _run(argv: list[str], cwd: Path, name: str) -> dict:
    proc = subprocess.run(argv, cwd=cwd, capture_output=True, text=True)
    return {
        "name": name,
        "argv": argv,
        "exit_code": proc.returncode,
        "stdout_sha256": sha256_bytes(proc.stdout.encode("utf-8", errors="replace")),
        "stderr_sha256": sha256_bytes(proc.stderr.encode("utf-8", errors="replace")),
    }


def restore_pristine_tests(workspace: Path, case_dir: Path) -> None:
    src_tests = case_dir / "tests"
    dst_tests = workspace / "tests"
    if dst_tests.exists():
        shutil.rmtree(dst_tests)
    shutil.copytree(src_tests, dst_tests)
    hidden_src = case_dir / "hidden_tests"
    if hidden_src.is_dir():
        hidden_dst = workspace / "hidden_tests"
        if hidden_dst.exists():
            shutil.rmtree(hidden_dst)
        shutil.copytree(hidden_src, hidden_dst)


def apply_src_patches_only(workspace: Path, patches: dict[str, str]) -> list[str]:
    ignored: list[str] = []
    for rel, content in patches.items():
        norm = rel.replace("\\", "/")
        if not norm.startswith("src/"):
            ignored.append(norm)
            continue
        path = workspace / norm
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
    return ignored


def _verify_host(workspace: Path, result: VerifyResult) -> VerifyResult:
    py = sys.executable
    src = workspace / "src"
    rec = _run([py, "-m", "ruff", "check", str(src)], cwd=workspace, name="ruff")
    result.commands.append(rec)
    result.ruff_ok = rec["exit_code"] == 0
    if not result.ruff_ok:
        result.findings.append(f"ruff_exit_{rec['exit_code']}")

    junit = workspace / ".karba-junit.xml"
    rec = _run(
        [py, "-m", "pytest", "tests", f"--junitxml={junit}", "-q"],
        cwd=workspace,
        name="pytest",
    )
    result.commands.append(rec)
    result.pytest_ok = rec["exit_code"] == 0
    if junit.is_file():
        xml = junit.read_text(encoding="utf-8", errors="replace")
        m = re.search(r'tests="(\d+)".*?failures="(\d+)".*?errors="(\d+)".*?skipped="(\d+)"', xml, re.S)
        if m:
            tests, failed, errors, skipped = map(int, m.groups())
            result.test_summary = {
                "passed": max(0, tests - failed - errors - skipped),
                "failed": failed,
                "errors": errors,
                "skipped": skipped,
            }
    if not result.pytest_ok:
        result.findings.append(f"pytest_exit_{rec['exit_code']}")

    if (workspace / "hidden_tests").is_dir():
        rec = _run([py, "-m", "pytest", "hidden_tests", "-q"], cwd=workspace, name="hidden_pytest")
        result.commands.append(rec)
        result.hidden_ok = rec["exit_code"] == 0
        if not result.hidden_ok:
            result.findings.append("hidden_regression_failed")
    return result


def _verify_container(workspace: Path, result: VerifyResult) -> VerifyResult:
    from karba.docker_verify import run_verify_container

    data = run_verify_container(workspace)
    result.isolation = "container"
    result.network = "none"
    result.ruff_ok = data.get("ruff_exit") == 0
    result.pytest_ok = data.get("pytest_exit") == 0
    result.hidden_ok = data.get("hidden_exit") == 0
    result.test_summary = data.get("test_summary") or result.test_summary
    result.commands.append(
        {
            "name": "docker_verify",
            "argv": ["docker", "run", "--network", "none", data.get("_image", "kozphy-karba-verifier:py312")],
            "exit_code": int(data.get("_docker_exit") or 0),
            "stdout_sha256": sha256_bytes(b""),
            "stderr_sha256": sha256_bytes(json_bytes := __import__("json").dumps(data).encode()),
            "image_fingerprint": data.get("_image_fingerprint"),
        }
    )
    if not result.ruff_ok:
        result.findings.append(f"ruff_exit_{data.get('ruff_exit')}")
    if not result.pytest_ok:
        result.findings.append(f"pytest_exit_{data.get('pytest_exit')}")
    if not result.hidden_ok:
        result.findings.append("hidden_regression_failed")
    return result


def run_verify(
    workspace: Path,
    case_dir: Path,
    *,
    isolation: Isolation = "auto",
) -> VerifyResult:
    result = VerifyResult(ok=False, pytest_ok=False, ruff_ok=False, security_ok=False, hidden_ok=True)
    restore_pristine_tests(workspace, case_dir)

    use_container = isolation == "container"
    if isolation == "auto":
        try:
            from karba.docker_verify import docker_available

            use_container = docker_available()
        except Exception:  # noqa: BLE001
            use_container = False

    if use_container:
        try:
            _verify_container(workspace, result)
        except Exception as exc:  # noqa: BLE001 — fail soft to host if isolation=auto
            if isolation == "container":
                raise
            result.findings.append(f"docker_fallback:{type(exc).__name__}")
            result.isolation = "host"
            result.network = "host"
            _verify_host(workspace, result)
    else:
        result.isolation = "host"
        result.network = "host"
        _verify_host(workspace, result)

    findings = scan_secrets(workspace / "src")
    result.findings.extend(findings)
    result.security_ok = not any(
        f.startswith("secret_pattern") or f.startswith("syntax_error") for f in findings
    )
    result.commands.append(
        {
            "name": "security_scan",
            "argv": ["karba-security-scan"],
            "exit_code": 0 if result.security_ok else 1,
            "stdout_sha256": sha256_bytes(b""),
            "stderr_sha256": sha256_bytes("\n".join(findings).encode()),
        }
    )
    result.ok = result.pytest_ok and result.ruff_ok and result.security_ok and result.hidden_ok
    return result
