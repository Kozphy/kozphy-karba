from __future__ import annotations

import json
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse


HTML = """<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"/>
<title>KARBA Dashboard</title>
<style>
:root{--bg:#10151c;--fg:#e8eef5;--muted:#8a9bb0;--ok:#3dd68c;--bad:#f07178;--warn:#ffcc66}
body{margin:0;font-family:Segoe UI,system-ui,sans-serif;background:
radial-gradient(900px 500px at 0% 0%,#1a2a3a,transparent),
radial-gradient(800px 400px at 100% 0%,#24301a,transparent),var(--bg);color:var(--fg)}
main{max-width:960px;margin:0 auto;padding:40px 20px}
h1{margin:0 0 6px;font-size:1.7rem}
.lead{color:var(--muted);margin:0 0 28px}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:14px}
.m{border-top:1px solid #243041;padding:12px 0}.m .l{color:var(--muted);font-size:.75rem;text-transform:uppercase;letter-spacing:.05em}
.m .v{font-size:1.45rem;margin-top:4px;font-variant-numeric:tabular-nums}
.ok{color:var(--ok)}.bad{color:var(--bad)}.warn{color:var(--warn)}
pre{background:#121821;padding:14px;border-radius:8px;overflow:auto;font-size:.82rem}
.gate{margin:24px 0;padding:12px 14px;border-left:3px solid var(--warn);background:#161d27}
</style></head><body><main>
<h1>KARBA</h1>
<p class="lead">Agent reliability & assurance — local synthetic evidence. accepted ≠ merge authority.</p>
<div class="grid" id="g"></div>
<div class="gate" id="gate"></div>
<h2 style="font-size:1rem;color:var(--muted)">Metrics JSON</h2>
<pre id="raw">loading…</pre>
<script>
async function load(){
  const m=await (await fetch('/api/metrics')).json();
  const pct=x=>((x||0)*100).toFixed(1)+'%';
  const cards=[
    ['Task success',pct(m.task_success_rate),'ok'],
    ['Simulated CFR',pct(m.simulated_change_failure_rate),'warn'],
    ['Regression rate',pct(m.regression_rate),'warn'],
    ['Security viol. attempts',String(m.security_violation_attempts||0),'bad'],
    ['Evidence completeness',pct(m.evidence_completeness),'ok'],
    ['Human intervention',pct(m.human_intervention_rate),'warn'],
    ['Cost / success USD', m.cost_per_successful_task_usd==null?'n/a':Number(m.cost_per_successful_task_usd).toFixed(4),'ok'],
    ['Attempts',String(m.attempts||0),'ok'],
  ];
  document.getElementById('g').innerHTML=cards.map(([l,v,c])=>`<div class="m"><div class="l">${l}</div><div class="v ${c}">${v}</div></div>`).join('');
  const a=m.approval_states||{};
  document.getElementById('gate').textContent=`Approval: human_gate=${a.human_gate}; merge_authorized=${a.merge_authorized}`;
  document.getElementById('raw').textContent=JSON.stringify(m,null,2);
}
load();
</script></main></body></html>"""


def create_app(metrics_path: Path) -> FastAPI:
    app = FastAPI(title="KARBA Dashboard")

    @app.get("/", response_class=HTMLResponse)
    def index() -> str:
        return HTML

    @app.get("/api/metrics")
    def metrics() -> JSONResponse:
        if metrics_path.is_file():
            return JSONResponse(json.loads(metrics_path.read_text(encoding="utf-8")))
        return JSONResponse(
            {
                "error": "metrics not found",
                "task_success_rate": 0,
                "approval_states": {"human_gate": "PENDING", "merge_authorized": False},
            }
        )

    return app


def serve(metrics_path: Path, host: str = "127.0.0.1", port: int = 8787) -> None:
    import uvicorn

    uvicorn.run(create_app(metrics_path), host=host, port=port, log_level="warning")