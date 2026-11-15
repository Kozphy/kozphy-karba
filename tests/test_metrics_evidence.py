from karba.evidence import build_evidence, verify_integrity
from karba.metrics import compute_metrics, wilson_ci


def test_wilson_bounds() -> None:
    lo, hi = wilson_ci(8, 10)  # type: ignore[misc]
    assert 0 <= lo <= 0.8 <= hi <= 1


def test_evidence_never_authorizes_merge() -> None:
    ev = build_evidence(
        run_id="r",
        case_id="c",
        agent_id="oracle",
        trial_index=0,
        outcome="accepted",
        agent_claims={"success": True},
        verified={"ok": True},
        commands=[],
        security_findings=[],
    )
    assert ev["merge_authorized"] is False
    assert verify_integrity(ev) is True


def test_metrics_exclude_infra_from_success_denom() -> None:
    attempts = [
        {"outcome": "accepted", "verified": {"ok": True}, "cost_usd": 0.1, "evidence_sha256": "a"},
        {"outcome": "infra_error", "verified": {}, "cost_usd": 0, "evidence_sha256": None},
        {"outcome": "rejected", "verified": {"ok": False}, "cost_usd": 0.1, "security_findings": ["x"], "evidence_sha256": "b"},
    ]
    m = compute_metrics(attempts)
    assert m["scored_attempts"] == 2
    assert m["task_success_rate"] == 0.5
    assert m["revert_rate"] is None