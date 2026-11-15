from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field


Outcome = Literal["accepted", "rejected", "infra_error"]


class CaseMeta(BaseModel):
    case_id: str
    title: str
    category: str
    expect_accepted_for: list[str] = Field(default_factory=list)
    defect_class: str | None = None
    max_cost_usd: float = 0.0


class AgentClaim(BaseModel):
    success: bool = False
    message: str = ""
    patch_files: dict[str, str] = Field(default_factory=dict)
    requested_ops: list[str] = Field(default_factory=list)
    elapsed_seconds: float = 0.0
    cost_usd: float = 0.0


class AttemptRecord(BaseModel):
    run_id: str
    case_id: str
    agent_id: str
    trial_index: int
    outcome: Outcome
    agent_claims: dict[str, Any]
    verified: dict[str, Any]
    security_findings: list[str] = Field(default_factory=list)
    commands: list[dict[str, Any]] = Field(default_factory=list)
    recovery_seconds: float | None = None
    human_intervention: bool = False
    cost_usd: float = 0.0
    merge_authorized: bool = False
    human_gate: str = "PENDING"