from __future__ import annotations

import platform
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from karba import __version__
from karba.hashing import canonical_json, hash_json


def build_evidence(
    *,
    run_id: str,
    case_id: str,
    agent_id: str,
    trial_index: int,
    outcome: str,
    agent_claims: dict[str, Any],
    verified: dict[str, Any],
    commands: list[dict[str, Any]],
    security_findings: list[str],
    notes: str = "",
) -> dict[str, Any]:
    body = {
        "schema": "karba.evidence.v1",
        "run_id": run_id,
        "case_id": case_id,
        "agent_id": agent_id,
        "trial_index": trial_index,
        "outcome": outcome,
        "merge_authorized": False,
        "human_gate": "PENDING",
        "agent_claims": agent_claims,
        "verified": verified,
        "commands": commands,
        "security_findings": security_findings,
        "environment": {
            "python": sys.version.split()[0],
            "platform": platform.platform(),
            "karba_version": __version__,
        },
        "created_at": datetime.now(timezone.utc).isoformat(),
        "notes": notes,
    }
    digest = hash_json(body)
    body["evidence_sha256"] = digest
    return body


def write_evidence(path: Path, evidence: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(canonical_json(evidence) + b"\n")
    md = path.with_suffix(".md")
    md.write_text(
        "\n".join(
            [
                f"# KARBA evidence — {evidence['case_id']} / {evidence['agent_id']}",
                "",
                f"- outcome: **{evidence['outcome']}**",
                f"- merge_authorized: `{evidence['merge_authorized']}`",
                f"- human_gate: `{evidence['human_gate']}`",
                f"- evidence_sha256: `{evidence['evidence_sha256']}`",
                "",
                "## Agent claims (untrusted)",
                "",
                f"```json\n{canonical_json(evidence['agent_claims']).decode()}\n```",
                "",
                "## Independently verified",
                "",
                f"```json\n{canonical_json(evidence['verified']).decode()}\n```",
                "",
                "## Security findings",
                "",
                *[f"- {f}" for f in evidence["security_findings"] or ["(none)"]],
                "",
            ]
        ),
        encoding="utf-8",
    )


def verify_integrity(evidence: dict[str, Any]) -> bool:
    if evidence.get("merge_authorized") is not False:
        return False
    copy = dict(evidence)
    claimed = copy.pop("evidence_sha256", None)
    return claimed == hash_json(copy)