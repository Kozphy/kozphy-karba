"""Executed inside the KARBA verifier container. Writes JSON result to /out/result.json."""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path


def main() -> int:
    work = Path("/work")
    out = Path("/out")
    out.mkdir(parents=True, exist_ok=True)
    result = {
        "ruff_exit": None,
        "pytest_exit": None,
        "hidden_exit": None,
        "test_summary": {"passed": 0, "failed": 0, "errors": 0, "skipped": 0},
    }

    src = work / "src"
    ruff = subprocess.run(
        [sys.executable, "-m", "ruff", "check", str(src)],
        cwd=work,
        capture_output=True,
        text=True,
    )
    result["ruff_exit"] = ruff.returncode

    junit = out / "junit.xml"
    pytest = subprocess.run(
        [
            sys.executable,
            "-m",
            "pytest",
            "tests",
            "-q",
            "-p",
            "no:cacheprovider",
            f"--basetemp={out / 'basetemp'}",
            f"--junitxml={junit}",
        ],
        cwd=work,
        capture_output=True,
        text=True,
    )
    result["pytest_exit"] = pytest.returncode
    if junit.is_file():
        xml = junit.read_text(encoding="utf-8", errors="replace")
        m = re.search(
            r'tests="(\d+)".*?failures="(\d+)".*?errors="(\d+)".*?skipped="(\d+)"',
            xml,
            re.S,
        )
        if m:
            tests, failed, errors, skipped = map(int, m.groups())
            result["test_summary"] = {
                "passed": max(0, tests - failed - errors - skipped),
                "failed": failed,
                "errors": errors,
                "skipped": skipped,
            }

    if (work / "hidden_tests").is_dir():
        hidden = subprocess.run(
            [
                sys.executable,
                "-m",
                "pytest",
                "hidden_tests",
                "-q",
                "-p",
                "no:cacheprovider",
                f"--basetemp={out / 'basetemp-hidden'}",
            ],
            cwd=work,
            capture_output=True,
            text=True,
        )
        result["hidden_exit"] = hidden.returncode
    else:
        result["hidden_exit"] = 0

    (out / "result.json").write_text(json.dumps(result), encoding="utf-8")
    # Non-zero if any check failed
    ok = result["ruff_exit"] == 0 and result["pytest_exit"] == 0 and result["hidden_exit"] == 0
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
