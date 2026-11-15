from __future__ import annotations

from pathlib import Path

import pytest

from karba.docker_verify import docker_available
from karba.engine import run_attempt

ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.skipif(not docker_available(), reason="Docker daemon not available")
def test_container_isolation_oracle(tmp_path: Path) -> None:
    cases = ROOT / "benchmarks" / "cases"
    case = next(cases.iterdir())
    rec = run_attempt(
        run_id="docker-smoke",
        case_dir=case,
        agent_id="oracle",
        trial_index=0,
        out_dir=tmp_path,
        isolation="container",
    )
    assert rec["outcome"] == "accepted"
    assert rec["verified"]["isolation"] == "container"
    assert rec["verified"]["network"] == "none"
