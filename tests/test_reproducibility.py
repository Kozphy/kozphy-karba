from karba.reproducibility import compare_attempt_sets


def test_perfect_reproducibility() -> None:
    a = [
        {"case_id": "c1", "agent_id": "oracle", "trial_index": 0, "outcome": "accepted"},
        {"case_id": "c1", "agent_id": "buggy", "trial_index": 0, "outcome": "rejected"},
    ]
    b = [
        {"case_id": "c1", "agent_id": "oracle", "trial_index": 0, "outcome": "accepted"},
        {"case_id": "c1", "agent_id": "buggy", "trial_index": 0, "outcome": "rejected"},
    ]
    r = compare_attempt_sets(a, b)
    assert r["paired_attempts"] == 2
    assert r["evaluation_reproducibility"] == 1.0
    assert r["mismatched_outcomes"] == 0


def test_mismatch_detected() -> None:
    a = [{"case_id": "c1", "agent_id": "oracle", "trial_index": 0, "outcome": "accepted"}]
    b = [{"case_id": "c1", "agent_id": "oracle", "trial_index": 0, "outcome": "rejected"}]
    r = compare_attempt_sets(a, b)
    assert r["evaluation_reproducibility"] == 0.0
    assert r["mismatched_outcomes"] == 1
