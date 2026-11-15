from __future__ import annotations

import json
from pathlib import Path

from karba.engine import run_attempt

ROOT = Path(__file__).resolve().parents[1]


def test_oracle_accepts_generated_case(tmp_path: Path) -> None:
    cases = ROOT / "benchmarks" / "cases"
    if not cases.exists():
        return
    case = next(cases.iterdir())
    rec = run_attempt(
        run_id="test-run",
        case_dir=case,
        agent_id="oracle",
        trial_index=0,
        out_dir=tmp_path,
    )
    assert rec["outcome"] == "accepted"
    assert rec["merge_authorized"] is False
    assert Path(rec["evidence_path"]).is_file()


def test_buggy_rejected(tmp_path: Path) -> None:
    cases = ROOT / "benchmarks" / "cases"
    if not cases.exists():
        return
    case = next(cases.iterdir())
    rec = run_attempt(
        run_id="test-run",
        case_dir=case,
        agent_id="buggy",
        trial_index=0,
        out_dir=tmp_path,
    )
    assert rec["outcome"] == "rejected"