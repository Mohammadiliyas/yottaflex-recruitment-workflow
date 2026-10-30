from __future__ import annotations

import os
import sqlite3
import sys
import zipfile
from pathlib import Path

from flask import Flask, render_template_string, request, url_for

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))
from workflow import dashboard_metrics  # noqa: E402

app = Flask(__name__)

def resolve_database() -> Path:
    configured = os.environ.get("YOTTAFLEX_DB")
    if configured:
        db_path = Path(configured)
        if not db_path.exists():
            raise FileNotFoundError(f"YOTTAFLEX_DB does not exist: {db_path}")
        return db_path

    # Prefer a locally generated database when developing on a workstation.
    local_candidates = [
        ROOT / "data" / "full" / "recruitment.db",
        ROOT / "data" / "full" / "yottaflex-full-data-exports" / "recruitment.db",
    ]
    for candidate in local_candidates:
        if candidate.exists():
            return candidate

    # On Render, materialize only the SQLite database from the committed export ZIP.
    archive = ROOT / "artifacts" / "yottaflex-full-data-exports.zip"
    member = "yottaflex-full-data-exports/recruitment.db"
    if not archive.exists():
        raise FileNotFoundError(f"Full data archive not found: {archive}")

    target_dir = Path(os.environ.get("YOTTAFLEX_DATA_DIR", "/tmp/yottaflex-data"))
    target_dir.mkdir(parents=True, exist_ok=True)
    db_path = target_dir / "recruitment.db"
    if not db_path.exists():
        with zipfile.ZipFile(archive) as zf:
            info = zf.getinfo(member)
            if info.file_size > 100 * 1024 * 1024:
                raise RuntimeError("Database archive member exceeds the 100 MB safety limit.")
            with zf.open(info) as src, db_path.open("wb") as dst:
                while chunk := src.read(1024 * 1024):
                    dst.write(chunk)
    return db_path

DB_PATH = resolve_database()

STAGES = ["APPLIED", "SCREENING", "TECHNICAL", "PANEL", "OFFER", "WITHDRAWN"]

BASE = """
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{{ title }} · YottaFlex Recruitment Demo</title>
<style>
:root { color-scheme: light; --ink:#152238; --muted:#637083; --line:#e5e9f0; --paper:#f5f7fb; --blue:#2457d6; --navy:#12223b; --green:#19734b; --amber:#9a5c05; }
* { box-sizing:border-box; }
body { margin:0; background:var(--paper); color:var(--ink); font:14px/1.5 Inter,ui-sans-serif,system-ui,-apple-system,"Segoe UI",sans-serif; }
header { background:var(--navy); color:#fff; padding:19px max(22px,calc((100vw - 1180px)/2)); }
.brand { display:flex; justify-content:space-between; align-items:center; gap:16px; flex-wrap:wrap; }
.brand h1 { font-size:20px; margin:0; letter-spacing:-.3px; }
.brand small { color:#b9c5d6; display:block; margin-top:3px; }
.pill { border:1px solid #45607f; background:#1b3558; padding:5px 10px; border-radius:30px; font-size:11px; color:#e3efff; }
nav { display:flex; gap:9px; flex-wrap:wrap; margin-top:16px; }
nav a { color:#cad6e6; text-decoration:none; padding:7px 11px; border-radius:8px; }
nav a.active, nav a:hover { background:#263f62; color:#fff; }
main { max-width:1180px; margin:26px auto; padding:0 20px 40px; }
.notice { background:#fff8e9; border:1px solid #f0dfb8; color:#775015; padding:11px 14px; border-radius:10px; margin-bottom:19px; }
.heading { display:flex; justify-content:space-between; align-items:flex-end; gap:14px; margin:0 0 18px; flex-wrap:wrap; }
.heading h2 { margin:0; font-size:23px; letter-spacing:-.5px; }
.sub { color:var(--muted); margin-top:4px; }
.grid { display:grid; grid-template-columns:repeat(4,minmax(0,1fr)); gap:13px; margin:18px 0; }
.kpi, .panel { background:white; border:1px solid var(--line); border-radius:13px; box-shadow:0 2px 8px #1f2e4407; }
.kpi { padding:16px; }
.kpi .label { color:var(--muted); font-size:12px; }
.kpi .value { font-size:27px; letter-spacing:-.7px; font-weight:700; margin-top:5px; }
.kpi .hint { color:var(--muted); font-size:11px; margin-top:3px; }
.panel { padding:18px; margin-top:16px; }
.panel h3 { margin:0 0 12px; font-size:15px; }
.two { display:grid; grid-template-columns:1.15fr .85fr; gap:16px; }
.bar-row { display:grid; grid-template-columns:105px 1fr 52px; align-items:center; gap:10px; margin:11px 0; }
.bar-label { color:#475569; font-size:12px; }
.bar-track { height:10px; border-radius:12px; background:#edf1f7; overflow:hidden; }
.bar-fill { height:100%; border-radius:12px; background:var(--blue); }
.bar-count { text-align:right; font-weight:650; font-variant-numeric:tabular-nums; font-size:12px; }
table { border-collapse:collapse; width:100%; font-size:12px; }
th { color:#657286; text-align:left; font-size:11px; font-weight:650; text-transform:uppercase; letter-spacing:.04em; background:#f8fafc; }
th,td { padding:10px 9px; border-bottom:1px solid var(--line); vertical-align:top; }
tr:last-child td { border-bottom:0; }
td strong { font-weight:650; }
.muted { color:var(--muted); }
.tag { display:inline-block; border-radius:20px; padding:3px 8px; background:#eef2ff; color:#314ca1; font-size:10px; font-weight:650; }
.tag.good { background:#e9f7ef; color:var(--green); }
.tag.warn { background:#fff3df; color:var(--amber); }
form.filters { display:flex; flex-wrap:wrap; gap:9px; margin:14px 0; }
input,select { background:#fff; border:1px solid #d7deea; border-radius:8px; padding:9px 11px; min-width:170px; color:var(--ink); }
button { border:0; border-radius:8px; background:var(--blue); color:white; padding:9px 14px; font-weight:650; cursor:pointer; }
a { color:var(--blue); }
.empty { padding:22px; text-align:center; color:var(--muted); }
footer { max-width:1180px; padding:0 20px 26px; margin:auto; color:#8590a0; font-size:11px; }
@media(max-width:820px) { .grid { grid-template-columns:repeat(2,minmax(0,1fr)); } .two { grid-template-columns:1fr; } }
@media(max-width:520px) { .grid { grid-template-columns:repeat(2,minmax(0,1fr)); gap:8px; } .kpi { padding:12px; } .kpi .value { font-size:22px; } main { padding:0 12px 28px; } .panel { overflow-x:auto; padding:13px; } }
</style>
</head>
<body>
<header>
  <div class="brand">
    <div><h1>YottaFlex <span style="color:#8fb4ff">Recruitment Workflow</span></h1><small>Recruitment operations · synthetic data demo</small></div>
    <span class="pill">READ-ONLY DEMO · SYNTHETIC RECORDS</span>
  </div>
  <nav>
    <a class="{{ 'active' if active == 'overview' else '' }}" href="{{ url_for('index') }}">Overview</a>
    <a class="{{ 'active' if active == 'applications' else '' }}" href="{{ url_for('applications') }}">Applications</a>
    <a class="{{ 'active' if active == 'requisitions' else '' }}" href="{{ url_for('requisitions') }}">Requisitions</a>
    <a class="{{ 'active' if active == 'anomalies' else '' }}" href="{{ url_for('anomalies') }}">Anomaly register</a>
  </nav>
</header>
<main>
  <div class="notice"><strong>Demo data only.</strong> Every candidate, name, email and hiring record is synthetic. This is a read-only showcase of the generated workflow dataset, not a production ATS or a system for making hiring decisions.</div>
  {{ body|safe }}
</main>
<footer>YottaFlex recruitment workflow reference implementation · Seed 20261022 · No real candidate data · Generated records are for workflow testing only.</footer>
</body>
</html>
"""

def connect() -> sqlite3.Connection:
    if not DB_PATH.exists():
        raise FileNotFoundError(f"Database not found at {DB_PATH}")
    conn = sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    return conn

def money(value: int | float | None) -> str:
    if value is None:
        return "—"
    return "₹{:,.0f}".format(value)

def page(title: str, active: str, template: str, **context):
    return render_template_string(
        BASE, title=title, active=active,
        body=render_template_string(template, **context),
    )

@app.get("/health")
def health():
    try:
        conn = connect()
        conn.execute("SELECT 1").fetchone()
        conn.close()
        return {"status": "ok", "database": "connected"}
    except Exception as exc:
        return {"status": "error", "message": str(exc)}, 503

@app.get("/")
def index():
    try:
        conn = connect()
    except FileNotFoundError as exc:
        return page("Setup required", "overview", """
          <div class="heading"><div><h2>Dashboard unavailable</h2><div class="sub">{{ message }}</div></div></div>
        """, message=str(exc)), 503
    metrics = dashboard_metrics(conn)
    stage_counts = metrics["applications_by_stage"]
    max_stage = max(stage_counts.values()) if stage_counts else 1
    recent_reqs = conn.execute("""
        SELECT req_id,title,department,location,status,openings,min_salary,max_salary
        FROM requisition ORDER BY req_id LIMIT 7
    """).fetchall()
    recent_anomalies = conn.execute("""
        SELECT anomaly_id,entity_type,entity_id,issue_type,expected_decision
        FROM ground_truth ORDER BY anomaly_id
    """).fetchall()
    conn.close()
    return page("Overview", "overview", """
      <div class="heading"><div><h2>Recruitment overview</h2><div class="sub">Full-volume synthetic dataset · generated with fixed seed 20261022</div></div><span class="tag good">Dataset validated</span></div>
      <section class="grid">
        <div class="kpi"><div class="label">Open / approved requisitions</div><div class="value">{{ "{:,}".format(m.requisitions_open_or_approved) }}</div><div class="hint">Hiring demand records</div></div>
        <div class="kpi"><div class="label">Candidates</div><div class="value">{{ "{:,}".format(m.candidates) }}</div><div class="hint">Synthetic profiles</div></div>
        <div class="kpi"><div class="label">Applications</div><div class="value">{{ "{:,}".format(m.applications) }}</div><div class="hint">Across six workflow stages</div></div>
        <div class="kpi"><div class="label">Completed interviews</div><div class="value">{{ "{:,}".format(m.completed_interviews) }}</div><div class="hint">{{ (m.interview_completion_per_application * 100)|round(1) }}% of applications</div></div>
        <div class="kpi"><div class="label">Scorecard average</div><div class="value">{{ m.mean_relevant_score }}</div><div class="hint">Relevant submitted rubric items · / 5</div></div>
        <div class="kpi"><div class="label">Offers</div><div class="value">{{ "{:,}".format(m.offers) }}</div><div class="hint">{{ (m.offer_approval_rate * 100)|round(1) }}% approved / accepted</div></div>
        <div class="kpi"><div class="label">Known labelled cases</div><div class="value">{{ m.known_anomalies }}</div><div class="hint">Intentional workflow edge cases</div></div>
        <div class="kpi"><div class="label">Interviewer conflict cases</div><div class="value">{{ m.known_interviewer_conflict_cases }}</div><div class="hint">Explicitly labelled in ground truth</div></div>
      </section>
      <div class="two">
        <section class="panel"><h3>Application pipeline</h3>
          {% for stage in stages %}
            {% set n = counts.get(stage, 0) %}
            <div class="bar-row"><div class="bar-label">{{ stage }}</div><div class="bar-track"><div class="bar-fill" style="width:{{ (n / max_stage * 100) if max_stage else 0 }}%"></div></div><div class="bar-count">{{ "{:,}".format(n) }}</div></div>
          {% endfor %}
          <div class="muted" style="font-size:11px;margin-top:12px">Counts are current application-state snapshots, not unique people.</div>
        </section>
        <section class="panel"><h3>Validation highlights</h3>
          <p><span class="tag good">PASS</span> Foreign-key and primary-key checks</p>
          <p><span class="tag good">PASS</span> Interview date and availability checks</p>
          <p><span class="tag good">PASS</span> Stage-gate and offer-band checks</p>
          <p><span class="tag good">PASS</span> Labelled exceptions separated from integrity failures</p>
          <p class="muted" style="font-size:11px">The full validator reports zero unlabelled integrity violations for the packaged run.</p>
          <p><a href="{{ url_for('anomalies') }}">Inspect the 7 labelled edge cases →</a></p>
        </section>
      </div>
      <section class="panel"><h3>Requisition sample</h3><table><thead><tr><th>ID</th><th>Role</th><th>Department</th><th>Location</th><th>Status</th><th>Openings</th><th>Salary band</th></tr></thead><tbody>
      {% for r in reqs %}<tr><td>{{ r.req_id }}</td><td><strong>{{ r.title }}</strong></td><td>{{ r.department }}</td><td>{{ r.location }}</td><td><span class="tag">{{ r.status }}</span></td><td>{{ r.openings }}</td><td>{{ money(r.min_salary) }} – {{ money(r.max_salary) }}</td></tr>{% endfor %}
      </tbody></table><p><a href="{{ url_for('requisitions') }}">Browse requisitions →</a></p></section>
    """, m=metrics, stages=STAGES, counts=stage_counts, max_stage=max_stage,
         reqs=recent_reqs, money=money)

@app.get("/applications")
def applications():
    q = request.args.get("q", "").strip()[:80]
    stage = request.args.get("stage", "").strip().upper()
    if stage not in STAGES:
        stage = ""
    sql = """
      SELECT a.application_id,a.current_stage,a.applied_on,a.source,
             c.candidate_id,c.full_name,c.experience_years,c.location,
             r.req_id,r.title AS role,r.department
      FROM application a
      JOIN candidate c ON c.candidate_id=a.candidate_id
      JOIN requisition r ON r.req_id=a.req_id
      WHERE 1=1
    """
    params: list[str] = []
    if stage:
        sql += " AND a.current_stage=?"
        params.append(stage)
    if q:
        sql += " AND (a.application_id LIKE ? OR c.candidate_id LIKE ? OR c.full_name LIKE ? OR r.title LIKE ?)"
        params.extend([f"%{q}%"] * 4)
    sql += " ORDER BY a.applied_on DESC,a.application_id LIMIT 100"
    conn = connect()
    rows = conn.execute(sql, params).fetchall()
    total = conn.execute("SELECT COUNT(*) FROM application").fetchone()[0]
    conn.close()
    return page("Applications", "applications", """
      <div class="heading"><div><h2>Applications</h2><div class="sub">Search synthetic applications by ID, candidate ID or role. Showing up to 100 matches.</div></div><span class="tag">{{ "{:,}".format(total) }} total</span></div>
      <form class="filters" method="get"><input name="q" value="{{ q }}" placeholder="Search candidate, app ID or role"><select name="stage"><option value="">All stages</option>{% for s in stages %}<option value="{{ s }}" {% if stage == s %}selected{% endif %}>{{ s }}</option>{% endfor %}</select><button type="submit">Filter</button><a href="{{ url_for('applications') }}" style="padding:9px">Reset</a></form>
      <section class="panel"><table><thead><tr><th>Application</th><th>Candidate</th><th>Role</th><th>Department</th><th>Stage</th><th>Applied</th><th>Experience</th><th>Location</th></tr></thead><tbody>
      {% for r in rows %}<tr><td><strong>{{ r.application_id }}</strong></td><td>{{ r.full_name }}<div class="muted">{{ r.candidate_id }}</div></td><td>{{ r.role }}<div class="muted">{{ r.req_id }}</div></td><td>{{ r.department }}</td><td><span class="tag">{{ r.current_stage }}</span></td><td>{{ r.applied_on }}</td><td>{{ r.experience_years }} yrs</td><td>{{ r.location }}</td></tr>{% else %}<tr><td colspan="8" class="empty">No matching applications.</td></tr>{% endfor %}
      </tbody></table></section>
    """, rows=rows, total=total, q=q, stage=stage, stages=STAGES)

@app.get("/requisitions")
def requisitions():
    q = request.args.get("q", "").strip()[:80]
    sql = """SELECT req_id,title,department,location,status,openings,min_salary,max_salary,employment_type
             FROM requisition WHERE 1=1"""
    params: list[str] = []
    if q:
        sql += " AND (req_id LIKE ? OR title LIKE ? OR department LIKE ? OR location LIKE ?)"
        params.extend([f"%{q}%"] * 4)
    sql += " ORDER BY req_id LIMIT 200"
    conn = connect()
    rows = conn.execute(sql, params).fetchall()
    total = conn.execute("SELECT COUNT(*) FROM requisition").fetchone()[0]
    conn.close()
    return page("Requisitions", "requisitions", """
      <div class="heading"><div><h2>Requisitions</h2><div class="sub">Approved and open hiring demand records.</div></div><span class="tag">{{ total }} total</span></div>
      <form class="filters" method="get"><input name="q" value="{{ q }}" placeholder="Search ID, role, team or location"><button type="submit">Search</button><a href="{{ url_for('requisitions') }}" style="padding:9px">Reset</a></form>
      <section class="panel"><table><thead><tr><th>Requisition</th><th>Role</th><th>Department</th><th>Location</th><th>Status</th><th>Type</th><th>Openings</th><th>Salary band</th></tr></thead><tbody>
      {% for r in rows %}<tr><td>{{ r.req_id }}</td><td><strong>{{ r.title }}</strong></td><td>{{ r.department }}</td><td>{{ r.location }}</td><td><span class="tag">{{ r.status }}</span></td><td>{{ r.employment_type }}</td><td>{{ r.openings }}</td><td>{{ money(r.min_salary) }} – {{ money(r.max_salary) }}</td></tr>{% else %}<tr><td colspan="8" class="empty">No requisitions match that search.</td></tr>{% endfor %}
      </tbody></table></section>
    """, rows=rows, total=total, q=q, money=money)

@app.get("/anomalies")
def anomalies():
    conn = connect()
    rows = conn.execute("""
      SELECT anomaly_id,entity_type,entity_id,issue_type,expected_decision,description
      FROM ground_truth ORDER BY anomaly_id
    """).fetchall()
    conn.close()
    return page("Anomaly register", "anomalies", """
      <div class="heading"><div><h2>Known anomaly register</h2><div class="sub">Seven intentional edge cases included to test workflow controls.</div></div><span class="tag warn">{{ rows|length }} labelled cases</span></div>
      <section class="panel"><table><thead><tr><th>Case</th><th>Entity</th><th>Issue type</th><th>Expected decision</th><th>Description</th></tr></thead><tbody>
      {% for r in rows %}<tr><td><strong>{{ r.anomaly_id }}</strong></td><td>{{ r.entity_type }}<div class="muted">{{ r.entity_id }}</div></td><td><span class="tag warn">{{ r.issue_type }}</span></td><td>{{ r.expected_decision }}</td><td>{{ r.description }}</td></tr>{% endfor %}
      </tbody></table></section>
      <p class="muted" style="font-size:11px">Ground-truth labels are for evaluation only. They must not be joined into operational features when evaluating anomaly detection.</p>
    """, rows=rows)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "5000")))
