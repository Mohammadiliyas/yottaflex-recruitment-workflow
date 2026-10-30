from __future__ import annotations

import argparse
import csv
import hashlib
import json
import random
import shutil
import sqlite3
from collections import Counter
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any

SEED_DEFAULT = 20261022
BASE_DATE = date(2026, 1, 5)
STAGES = ["APPLIED", "SCREENING", "TECHNICAL", "PANEL", "OFFER", "HIRED"]
TERMINAL = {"WITHDRAWN", "REJECTED", "HIRED"}
TRANSITIONS = {
    "APPLIED": {"SCREENING", "WITHDRAWN", "REJECTED"},
    "SCREENING": {"TECHNICAL", "WITHDRAWN", "REJECTED"},
    "TECHNICAL": {"PANEL", "WITHDRAWN", "REJECTED"},
    "PANEL": {"OFFER", "WITHDRAWN", "REJECTED"},
    "OFFER": {"HIRED", "WITHDRAWN", "REJECTED"},
}
ROLE_SKILLS = ["Python", "SQL", "Java", "Django", "REST APIs", "Cloud", "Communication", "Problem Solving", "Data Analysis", "Testing", "React", "System Design"]
ROLE_TITLES = ["Backend Engineer", "Software Engineer", "Data Analyst", "QA Engineer", "Frontend Engineer", "Cloud Engineer", "Data Engineer", "Product Analyst"]
DEPARTMENTS = ["Engineering", "Data", "Product", "Operations", "IT"]
LOCATIONS = ["Hyderabad", "Bengaluru", "Pune", "Remote", "Chennai"]

SCHEMA = """
PRAGMA foreign_keys = ON;
CREATE TABLE IF NOT EXISTS hiring_manager (
  manager_id TEXT PRIMARY KEY, full_name TEXT NOT NULL, email TEXT NOT NULL UNIQUE,
  department TEXT NOT NULL, created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS requisition (
  req_id TEXT PRIMARY KEY, manager_id TEXT NOT NULL REFERENCES hiring_manager(manager_id),
  title TEXT NOT NULL, department TEXT NOT NULL, location TEXT NOT NULL,
  employment_type TEXT NOT NULL CHECK(employment_type IN ('FULL_TIME','CONTRACT','INTERN')),
  status TEXT NOT NULL CHECK(status IN ('APPROVED','OPEN','ON_HOLD','CLOSED','CANCELLED')),
  openings INTEGER NOT NULL CHECK(openings > 0), min_salary INTEGER NOT NULL CHECK(min_salary >= 0),
  max_salary INTEGER NOT NULL CHECK(max_salary >= min_salary), currency TEXT NOT NULL DEFAULT 'INR',
  opened_on TEXT NOT NULL, closes_on TEXT NOT NULL, created_at TEXT NOT NULL,
  CHECK(closes_on >= opened_on)
);
CREATE TABLE IF NOT EXISTS candidate (
  candidate_id TEXT PRIMARY KEY, full_name TEXT NOT NULL, email TEXT NOT NULL UNIQUE,
  experience_years REAL NOT NULL CHECK(experience_years >= 0), location TEXT NOT NULL,
  education TEXT NOT NULL, profile_created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS application (
  application_id TEXT PRIMARY KEY, candidate_id TEXT NOT NULL REFERENCES candidate(candidate_id),
  req_id TEXT NOT NULL REFERENCES requisition(req_id), current_stage TEXT NOT NULL,
  applied_on TEXT NOT NULL, updated_at TEXT NOT NULL, source TEXT NOT NULL,
  issue_type TEXT, UNIQUE(candidate_id, req_id)
);
CREATE TABLE IF NOT EXISTS skill_requirement (
  skill_requirement_id TEXT PRIMARY KEY, req_id TEXT NOT NULL REFERENCES requisition(req_id),
  skill_name TEXT NOT NULL, required_level INTEGER NOT NULL CHECK(required_level BETWEEN 1 AND 5),
  is_mandatory INTEGER NOT NULL CHECK(is_mandatory IN (0,1)), weight REAL NOT NULL CHECK(weight > 0),
  UNIQUE(req_id, skill_name)
);
CREATE TABLE IF NOT EXISTS candidate_skill (
  candidate_id TEXT NOT NULL REFERENCES candidate(candidate_id), skill_name TEXT NOT NULL,
  proficiency INTEGER NOT NULL CHECK(proficiency BETWEEN 1 AND 5),
  PRIMARY KEY(candidate_id, skill_name)
);
CREATE TABLE IF NOT EXISTS interview_panel (
  panel_id TEXT PRIMARY KEY, req_id TEXT NOT NULL REFERENCES requisition(req_id),
  panel_name TEXT NOT NULL, panel_type TEXT NOT NULL CHECK(panel_type IN ('TECHNICAL','CULTURE','FINAL'))
);
CREATE TABLE IF NOT EXISTS panel_interviewer (
  panel_id TEXT NOT NULL REFERENCES interview_panel(panel_id), interviewer_id TEXT NOT NULL REFERENCES hiring_manager(manager_id),
  role_on_panel TEXT NOT NULL CHECK(role_on_panel IN ('TECH_LEAD','PEER','HR','IT_OPERATIONS')),
  PRIMARY KEY(panel_id, interviewer_id)
);
CREATE TABLE IF NOT EXISTS availability (
  availability_id TEXT PRIMARY KEY, interviewer_id TEXT NOT NULL REFERENCES hiring_manager(manager_id),
  starts_at TEXT NOT NULL, ends_at TEXT NOT NULL, status TEXT NOT NULL CHECK(status IN ('AVAILABLE','BLOCKED')),
  CHECK(ends_at > starts_at)
);
CREATE TABLE IF NOT EXISTS interview (
  interview_id TEXT PRIMARY KEY, application_id TEXT NOT NULL REFERENCES application(application_id),
  panel_id TEXT NOT NULL REFERENCES interview_panel(panel_id), starts_at TEXT NOT NULL, ends_at TEXT NOT NULL,
  interview_type TEXT NOT NULL CHECK(interview_type IN ('TECHNICAL_PANEL','CULTURE_PANEL','FINAL_PANEL')),
  status TEXT NOT NULL CHECK(status IN ('SCHEDULED','COMPLETED','CANCELLED','RESCHEDULED')),
  rescheduled_from TEXT REFERENCES interview(interview_id), issue_type TEXT,
  CHECK(ends_at > starts_at)
);
CREATE TABLE IF NOT EXISTS scorecard (
  scorecard_id TEXT PRIMARY KEY, interview_id TEXT NOT NULL REFERENCES interview(interview_id),
  reviewer_id TEXT NOT NULL REFERENCES hiring_manager(manager_id), overall_score REAL,
  status TEXT NOT NULL CHECK(status IN ('DRAFT','SUBMITTED')), comments TEXT NOT NULL,
  submitted_at TEXT, issue_type TEXT,
  UNIQUE(interview_id, reviewer_id)
);
CREATE TABLE IF NOT EXISTS scorecard_item (
  scorecard_item_id TEXT PRIMARY KEY, scorecard_id TEXT NOT NULL REFERENCES scorecard(scorecard_id),
  criterion TEXT NOT NULL, score INTEGER NOT NULL CHECK(score BETWEEN 1 AND 5),
  comments TEXT NOT NULL, is_relevant INTEGER NOT NULL CHECK(is_relevant IN (0,1)), issue_type TEXT,
  UNIQUE(scorecard_id, criterion)
);
CREATE TABLE IF NOT EXISTS offer (
  offer_id TEXT PRIMARY KEY, application_id TEXT NOT NULL REFERENCES application(application_id),
  annual_salary INTEGER NOT NULL CHECK(annual_salary > 0), currency TEXT NOT NULL DEFAULT 'INR',
  status TEXT NOT NULL CHECK(status IN ('DRAFT','PENDING_APPROVAL','APPROVED','REJECTED','ACCEPTED','DECLINED')),
  issued_on TEXT NOT NULL, expires_on TEXT NOT NULL, issue_type TEXT,
  CHECK(expires_on >= issued_on)
);
CREATE TABLE IF NOT EXISTS approval (
  approval_id TEXT PRIMARY KEY, offer_id TEXT NOT NULL REFERENCES offer(offer_id),
  approver_id TEXT NOT NULL REFERENCES hiring_manager(manager_id), decision TEXT NOT NULL CHECK(decision IN ('APPROVED','REJECTED','PENDING')),
  decided_at TEXT NOT NULL, comments TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS application_event (
  event_id TEXT PRIMARY KEY, application_id TEXT NOT NULL REFERENCES application(application_id),
  from_stage TEXT CHECK(from_stage IS NULL OR from_stage IN ('APPLIED','SCREENING','TECHNICAL','PANEL','OFFER','HIRED','WITHDRAWN','REJECTED')),
  to_stage TEXT NOT NULL CHECK(to_stage IN ('APPLIED','SCREENING','TECHNICAL','PANEL','OFFER','HIRED','WITHDRAWN','REJECTED')),
  event_at TEXT NOT NULL, actor_id TEXT NOT NULL,
  reason TEXT NOT NULL, gate_passed INTEGER NOT NULL CHECK(gate_passed IN (0,1)), issue_type TEXT
);
CREATE TABLE IF NOT EXISTS ground_truth (
  anomaly_id TEXT PRIMARY KEY, entity_type TEXT NOT NULL, entity_id TEXT NOT NULL,
  issue_type TEXT NOT NULL, expected_decision TEXT NOT NULL, description TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_application_req ON application(req_id);
CREATE INDEX IF NOT EXISTS idx_interview_application ON interview(application_id);
CREATE INDEX IF NOT EXISTS idx_interview_start ON interview(starts_at);
CREATE INDEX IF NOT EXISTS idx_scorecard_interview ON scorecard(interview_id);
"""

CSV_TABLES = ["hiring_manager", "requisition", "candidate", "application", "skill_requirement", "candidate_skill", "interview_panel", "panel_interviewer", "availability", "interview", "scorecard", "scorecard_item", "offer", "approval", "application_event"]


def iso(d: date | datetime) -> str:
    if isinstance(d, datetime):
        if d.tzinfo is None:
            d = d.replace(tzinfo=timezone.utc)
        return d.isoformat(timespec="minutes")
    return d.isoformat()


def deterministic_email(prefix: str, n: int) -> str:
    return f"{prefix}{n:06d}@example.test"


def make_id(prefix: str, n: int, year: int | None = None) -> str:
    return f"{prefix}-{year}-{n:06d}" if year else f"{prefix}-{n:06d}"


def insert_many(conn: sqlite3.Connection, table: str, rows: list[dict[str, Any]]) -> None:
    if not rows:
        return
    cols = list(rows[0].keys())
    sql = f"INSERT INTO {table} ({','.join(cols)}) VALUES ({','.join('?' for _ in cols)})"
    conn.executemany(sql, [[row[c] for c in cols] for row in rows])


def generate(output: Path, seed: int = SEED_DEFAULT, scale: float = 1.0) -> dict[str, Any]:
    if scale <= 0:
        raise ValueError("scale must be > 0")
    rng = random.Random(seed)
    counts = {
        "requisitions": max(1, round(200 * scale)),
        "candidates": max(1, round(5000 * scale)),
        "applications": max(1, round(8000 * scale)),
        "interviews": max(1, round(2000 * scale)),
    }
    output.mkdir(parents=True, exist_ok=True)
    db_path = output / "recruitment.db"
    if db_path.exists():
        db_path.unlink()
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.executescript(SCHEMA)

    # Masters: interviewers/managers first, then requisitions and candidates.
    managers = []
    manager_count = max(40, min(100, counts["requisitions"] // 2))
    for i in range(1, manager_count + 1):
        managers.append({"manager_id": f"HM-{i:04d}", "full_name": f"Hiring Manager {i:03d}",
                         "email": deterministic_email("manager", i), "department": rng.choice(DEPARTMENTS),
                         "created_at": iso(BASE_DATE)})
    insert_many(conn, "hiring_manager", managers)
    manager_ids = [m["manager_id"] for m in managers]

    requisitions = []
    req_skills: dict[str, list[dict[str, Any]]] = {}
    panels = []
    panel_interviewers = []
    for i in range(1, counts["requisitions"] + 1):
        rid = make_id("REQ", i, 2026)
        opened = BASE_DATE + timedelta(days=rng.randint(0, 120))
        min_sal = rng.randrange(400_000, 1_200_001, 50_000)
        max_sal = min_sal + rng.randrange(200_000, 900_001, 50_000)
        requisitions.append({"req_id": rid, "manager_id": rng.choice(manager_ids), "title": rng.choice(ROLE_TITLES),
            "department": rng.choice(DEPARTMENTS), "location": rng.choice(LOCATIONS), "employment_type": "FULL_TIME",
            "status": "APPROVED", "openings": rng.randint(1, 5), "min_salary": min_sal, "max_salary": max_sal,
            "currency": "INR", "opened_on": iso(opened), "closes_on": iso(opened + timedelta(days=rng.randint(30, 90))),
            "created_at": iso(opened - timedelta(days=2))})
        picked = rng.sample(ROLE_SKILLS, k=rng.randint(4, 6))
        req_skills[rid] = []
        for j, skill in enumerate(picked, 1):
            req_skills[rid].append({"skill_requirement_id": f"SR-{i:06d}-{j:02d}", "req_id": rid,
                "skill_name": skill, "required_level": rng.choices([2, 3, 4], weights=[0.35, 0.45, 0.20])[0], "is_mandatory": 1 if j <= 3 else 0,
                "weight": round(rng.uniform(0.8, 2.0), 2)})
        pid = f"PANEL-{i:06d}"
        panels.append({"panel_id": pid, "req_id": rid, "panel_name": f"{rid} Interview Panel", "panel_type": "TECHNICAL"})
        for interviewer in rng.sample(manager_ids, k=3):
            panel_interviewers.append({"panel_id": pid, "interviewer_id": interviewer, "role_on_panel": rng.choice(["TECH_LEAD", "PEER", "HR", "IT_OPERATIONS"])})
    insert_many(conn, "requisition", requisitions)
    insert_many(conn, "skill_requirement", [x for values in req_skills.values() for x in values])
    insert_many(conn, "interview_panel", panels)
    insert_many(conn, "panel_interviewer", panel_interviewers)

    candidates = []
    candidate_skills = []
    educations = ["B.Tech", "B.E.", "MCA", "M.Sc", "B.Sc", "Diploma"]
    for i in range(1, counts["candidates"] + 1):
        cid = f"CAND-{i:06d}"
        candidates.append({"candidate_id": cid, "full_name": f"Synthetic Candidate {i:05d}",
            "email": deterministic_email("candidate", i), "experience_years": round(rng.uniform(0, 12), 1),
            "location": rng.choice(LOCATIONS), "education": rng.choice(educations),
            "profile_created_at": iso(BASE_DATE + timedelta(days=rng.randint(0, 150)))})
        for skill in rng.sample(ROLE_SKILLS, k=rng.randint(5, 10)):
            candidate_skills.append({"candidate_id": cid, "skill_name": skill, "proficiency": rng.choices([1, 2, 3, 4, 5], weights=[0.05, 0.15, 0.30, 0.30, 0.20])[0]})
    insert_many(conn, "candidate", candidates)
    insert_many(conn, "candidate_skill", candidate_skills)
    experience_by_candidate = {c["candidate_id"]: c["experience_years"] for c in candidates}

    # Application-parent relationships are valid and unique. Stage outcomes derive from skill match.
    req_rows = {r["req_id"]: r for r in requisitions}
    cand_skill_map: dict[str, dict[str, int]] = {}
    for cs in candidate_skills:
        cand_skill_map.setdefault(cs["candidate_id"], {})[cs["skill_name"]] = cs["proficiency"]
    req_ids = list(req_rows)
    candidate_ids = [c["candidate_id"] for c in candidates]
    pairs: set[tuple[str, str]] = set()
    applications = []
    app_events = []
    # Bounded attempts, with a deterministic fallback to ensure requested count.
    while len(pairs) < min(counts["applications"], len(candidate_ids) * len(req_ids)):
        pair = (rng.choice(candidate_ids), rng.choice(req_ids))
        pairs.add(pair)
        if len(pairs) >= counts["applications"]:
            break
    for idx, (cid, rid) in enumerate(sorted(pairs), 1):
        app_id = f"APP-{cid}-{rid}"
        applied = BASE_DATE + timedelta(days=rng.randint(0, 180))
        skills_needed = req_skills[rid]
        skills_have = cand_skill_map.get(cid, {})
        mandatory = [s for s in skills_needed if s["is_mandatory"]]
        total_weight = sum(s["weight"] for s in mandatory) or 1.0
        matched_weight = sum(s["weight"] for s in mandatory
                             if skills_have.get(s["skill_name"], 0) >= s["required_level"])
        fit_ratio = matched_weight / total_weight
        experience = experience_by_candidate[cid]
        if fit_ratio < 0.34:
            progression = "APPLIED"
        elif fit_ratio < 0.60:
            progression = "SCREENING"
        elif fit_ratio < 0.90 or experience < 3:
            progression = "TECHNICAL"
        elif experience < 7:
            progression = "PANEL"
        else:
            progression = "OFFER"
        withdrawn = rng.random() < 0.055
        stage = "WITHDRAWN" if withdrawn else progression
        app_events.append({"event_id": f"EVT-{idx:07d}-01", "application_id": app_id, "from_stage": None,
            "to_stage": "APPLIED", "event_at": iso(applied), "actor_id": "SYSTEM", "reason": "Application submitted",
            "gate_passed": 1, "issue_type": None})
        if withdrawn:
            event_path = ["WITHDRAWN"]
        else:
            target_index = STAGES.index(progression)
            event_path = STAGES[1:target_index + 1]
        prior_stage = "APPLIED"
        last_event_at = applied
        for event_number, next_stage in enumerate(event_path, 2):
            last_event_at = applied + timedelta(days=(event_number - 1) * 2)
            app_events.append({"event_id": f"EVT-{idx:07d}-{event_number:02d}", "application_id": app_id,
                "from_stage": prior_stage, "to_stage": next_stage, "event_at": iso(last_event_at),
                "actor_id": "SYSTEM", "reason": "Candidate withdrew" if next_stage == "WITHDRAWN" else "Sequential skill-fit stage gate",
                "gate_passed": 1, "issue_type": None})
            prior_stage = next_stage
        updated_at = max(applied + timedelta(days=rng.randint(1, 25)), last_event_at)
        applications.append({"application_id": app_id, "candidate_id": cid, "req_id": rid,
            "current_stage": stage, "applied_on": iso(applied), "updated_at": iso(updated_at),
            "source": rng.choice(["CAREERS_SITE", "REFERRAL", "LINKEDIN", "JOB_BOARD"]), "issue_type": None})
    insert_many(conn, "application", applications)
    insert_many(conn, "application_event", app_events)

    # Availability blocks are generated before interviews.
    availability = []
    for mi, manager_id in enumerate(manager_ids, 1):
        for day_offset in range(0, 240):
            day = BASE_DATE + timedelta(days=day_offset)
            if day.weekday() >= 5:
                continue
            for hour in (9, 11, 13, 15):
                start = datetime(day.year, day.month, day.day, hour, tzinfo=timezone.utc)
                availability.append({"availability_id": f"AVL-{mi:04d}-{day_offset:03d}-{hour:02d}",
                    "interviewer_id": manager_id, "starts_at": iso(start), "ends_at": iso(start + timedelta(hours=1)),
                    "status": "AVAILABLE"})
    insert_many(conn, "availability", availability)

    app_by_id = {a["application_id"]: a for a in applications}
    schedulable = [a for a in applications if a["current_stage"] in {"TECHNICAL", "PANEL", "OFFER"}]
    rng.shuffle(schedulable)
    interviews = []
    scorecards = []
    scorecard_items = []
    booked: dict[str, list[tuple[datetime, datetime]]] = {m: [] for m in manager_ids}
    app_to_interview: dict[str, str] = {}
    interview_n = 0
    exception_slots: dict[str, str] = {}
    for app in schedulable:
        if interview_n >= counts["interviews"]:
            break
        req = req_rows[app["req_id"]]
        panel_id = f"PANEL-{int(req['req_id'].split('-')[-1]):06d}"
        panel_members = [x["interviewer_id"] for x in panel_interviewers if x["panel_id"] == panel_id]
        app_day = date.fromisoformat(app["applied_on"]) + timedelta(days=rng.randint(5, 25))
        selected = None
        for attempt in range(960):
            day = app_day + timedelta(days=attempt // 4)
            hour = (9, 11, 13, 15)[attempt % 4]
            if day < BASE_DATE or (day - BASE_DATE).days >= 240 or day.weekday() >= 5:
                continue
            start = datetime(day.year, day.month, day.day, hour, tzinfo=timezone.utc)
            end = start + timedelta(hours=1)
            if all(not any(start < old_end and end > old_start for old_start, old_end in booked[m]) for m in panel_members):
                selected = (start, end)
                break
        if selected is None:
            continue
        start, end = selected
        for m in panel_members:
            booked[m].append((start, end))
        interview_n += 1
        iid = make_id("INT", interview_n, 2026)
        interviews.append({"interview_id": iid, "application_id": app["application_id"], "panel_id": panel_id,
            "starts_at": iso(start), "ends_at": iso(end), "interview_type": "TECHNICAL_PANEL",
            "status": "COMPLETED", "rescheduled_from": None, "issue_type": None})
        app_to_interview[app["application_id"]] = iid
        for reviewer_idx, reviewer in enumerate(panel_members, 1):
            scorecard_id = f"SCORE-{iid}-{reviewer}"
            item_rows = []
            criteria = ["Problem Solving", "Technical Depth", "Communication", "Role Knowledge"]
            for item_idx, criterion in enumerate(criteria, 1):
                score = rng.randint(2, 5)
                item_id = f"SCITEM-{interview_n:06d}-{reviewer_idx:02d}-{item_idx:02d}"
                item_rows.append({"scorecard_item_id": item_id, "scorecard_id": scorecard_id,
                    "criterion": criterion, "score": score, "comments": "Synthetic rubric assessment", "is_relevant": 1, "issue_type": None})
            complete = not (interview_n == max(1, counts["interviews"] // 2) and reviewer_idx == 1)
            if not complete:
                item_rows = item_rows[:-1]
            item_avg = round(sum(x["score"] for x in item_rows) / len(item_rows), 2)
            submitted = iso(end + timedelta(hours=rng.randint(1, 48))) if complete else None
            scorecards.append({"scorecard_id": scorecard_id, "interview_id": iid,
                "reviewer_id": reviewer, "overall_score": item_avg if complete else None, "status": "SUBMITTED" if complete else "DRAFT",
                "comments": "Synthetic panel rubric assessment", "submitted_at": submitted,
                "issue_type": None if complete else "INCOMPLETE_SCORECARD"})
            scorecard_items.extend(item_rows)
    insert_many(conn, "interview", interviews)
    insert_many(conn, "scorecard", scorecards)
    insert_many(conn, "scorecard_item", scorecard_items)

    # Normal offers are only generated for interview-evaluated candidates and stay within the band.
    offers = []
    approvals = []
    offer_counter = 0
    scorecard_status_by_interview: dict[str, list[str]] = {}
    for sc in scorecards:
        scorecard_status_by_interview.setdefault(sc["interview_id"], []).append(sc["status"])
    complete_interviews = {iid for iid, statuses in scorecard_status_by_interview.items()
                           if statuses and all(status == "SUBMITTED" for status in statuses)}
    for app in applications:
        interview_for_app = app_to_interview.get(app["application_id"])
        if interview_for_app not in complete_interviews or app["current_stage"] != "OFFER":
            continue
        req = req_rows[app["req_id"]]
        offer_counter += 1
        salary = rng.randrange(req["min_salary"], req["max_salary"] + 1, 10_000)
        oid = make_id("OFF", offer_counter, 2026)
        offered = date.fromisoformat(app["updated_at"]) + timedelta(days=1)
        offers.append({"offer_id": oid, "application_id": app["application_id"], "annual_salary": salary,
            "currency": "INR", "status": "APPROVED", "issued_on": iso(offered),
            "expires_on": iso(offered + timedelta(days=14)), "issue_type": None})
        approvals.append({"approval_id": f"APR-{offer_counter:06d}", "offer_id": oid,
            "approver_id": req["manager_id"], "decision": "APPROVED", "decided_at": iso(offered),
            "comments": "Within approved requisition band"})
    insert_many(conn, "offer", offers)
    insert_many(conn, "approval", approvals)

    # Labelled edge cases are explicit, isolated records. They are not silently blended into clean baseline rows.
    truth: list[dict[str, str]] = []
    def add_truth(entity_type: str, entity_id: str, issue: str, decision: str, desc: str) -> None:
        truth.append({"anomaly_id": f"GT-{len(truth)+1:03d}", "entity_type": entity_type, "entity_id": entity_id,
                      "issue_type": issue, "expected_decision": decision, "description": desc})

    # 1. Candidate advanced without completed required review: an event marked gate_passed=0.
    target_app = next((a for a in applications if a["current_stage"] == "SCREENING"), applications[0])
    bad_event = "EVT-ANOM-001"
    conn.execute("UPDATE application SET current_stage='TECHNICAL', updated_at=? WHERE application_id=?",
                 (iso(BASE_DATE + timedelta(days=200)), target_app["application_id"]))
    conn.execute("INSERT INTO application_event VALUES (?,?,?,?,?,?,?,?,?)",
        (bad_event, target_app["application_id"], "SCREENING", "TECHNICAL", iso(BASE_DATE + timedelta(days=200)),
         "SYSTEM", "Injected exception: review missing", 0, "MISSING_REQUIRED_REVIEW"))
    add_truth("application_event", bad_event, "MISSING_REQUIRED_REVIEW", "REJECT_TRANSITION", "Application advanced to technical stage without required screening review.")

    # 2. Double-booked interviewer: create an overlapping conflicting interview with labelled issue_type.
    if interviews:
        base_i = interviews[0]
        member = next(x["interviewer_id"] for x in panel_interviewers if x["panel_id"] == base_i["panel_id"])
        base_req_id = app_by_id[base_i["application_id"]]["req_id"]
        second_app = next((a for a in schedulable if a["application_id"] != base_i["application_id"] and a["req_id"] == base_req_id),
                          next((a for a in applications if a["req_id"] == base_req_id and a["application_id"] != base_i["application_id"]), app_by_id[base_i["application_id"]]))
        conflict_id = make_id("INT", interview_n + 1, 2026)
        start = datetime.fromisoformat(base_i["starts_at"])
        conn.execute("INSERT INTO interview VALUES (?,?,?,?,?,?,?,?,?)",
            (conflict_id, second_app["application_id"], base_i["panel_id"], iso(start + timedelta(minutes=15)),
             iso(start + timedelta(minutes=75)), "TECHNICAL_PANEL", "SCHEDULED", None, "INTERVIEWER_DOUBLE_BOOKED"))
        add_truth("interview", conflict_id, "INTERVIEWER_DOUBLE_BOOKED", "BLOCK_OR_RESCHEDULE", f"Intentional overlap against {base_i['interview_id']} involving interviewer {member}; scheduling validator must flag it.")

    # 3. Out-of-band offer; retain it as labelled exception, not as a valid offer.
    if applications:
        app_for_offer = next((a for a in applications if a["current_stage"] == "OFFER"), applications[0])
        req = req_rows[app_for_offer["req_id"]]
        bad_offer = make_id("OFF", offer_counter + 1, 2026)
        conn.execute("INSERT INTO offer VALUES (?,?,?,?,?,?,?,?)",
            (bad_offer, app_for_offer["application_id"], req["max_salary"] + 250_000, "INR", "PENDING_APPROVAL",
             iso(BASE_DATE + timedelta(days=210)), iso(BASE_DATE + timedelta(days=224)), "OFFER_EXCEEDS_BAND"))
        conn.execute("INSERT INTO approval VALUES (?,?,?,?,?,?)",
            (f"APR-{offer_counter + 1:06d}", bad_offer, req["manager_id"], "PENDING", iso(BASE_DATE + timedelta(days=210)), "Pending compensation exception review"))
        add_truth("offer", bad_offer, "OFFER_EXCEEDS_BAND", "REJECT_OR_ESCALATE", "Annual salary exceeds the linked requisition maximum; approval must not be auto-granted.")

    # 4. Withdrawn candidate still scheduled.
    withdrawn_app = next((a for a in applications if a["current_stage"] == "WITHDRAWN"), None)
    if withdrawn_app:
        p_id = f"PANEL-{int(withdrawn_app['req_id'].split('-')[-1]):06d}"
        bad_int = make_id("INT", interview_n + 2, 2026)
        conn.execute("INSERT INTO interview VALUES (?,?,?,?,?,?,?,?,?)",
            (bad_int, withdrawn_app["application_id"], p_id, iso(BASE_DATE + timedelta(days=230)),
             iso(datetime.combine(BASE_DATE + timedelta(days=230), datetime.min.time()).replace(tzinfo=timezone.utc) + timedelta(hours=1)), "TECHNICAL_PANEL", "SCHEDULED", None, "WITHDRAWN_CANDIDATE_SCHEDULED"))
        add_truth("interview", bad_int, "WITHDRAWN_CANDIDATE_SCHEDULED", "CANCEL_INTERVIEW", "Interview is scheduled for an application whose current lifecycle state is WITHDRAWN.")

    # 5. Irrelevant criterion in a structured scorecard item, explicitly marked.
    if scorecards:
        parent_scorecard = scorecards[-1]["scorecard_id"]
        bad_score = "SCITEM-ANOM001"
        conn.execute("INSERT INTO scorecard_item VALUES (?,?,?,?,?,?,?)",
            (bad_score, parent_scorecard, "Astrology Compatibility", 5, "Injected irrelevant criterion", 0, "IRRELEVANT_EVALUATION_CRITERION"))
        add_truth("scorecard_item", bad_score, "IRRELEVANT_EVALUATION_CRITERION", "EXCLUDE_FROM_DECISION", "Criterion is unrelated to role requirements and must be excluded from evaluation aggregation.")
    incomplete = next((x for x in scorecards if x["issue_type"] == "INCOMPLETE_SCORECARD"), None)
    if incomplete:
        add_truth("scorecard", incomplete["scorecard_id"], "INCOMPLETE_SCORECARD", "HOLD_FOR_COMPLETION", "Rubric is missing one required criterion and has not been submitted; do not use it in decisions.")

    # Mark a reschedule trail on one normal interview (old event retained as RESCHEDULED).
    if interviews:
        old = interviews[-1]
        new_iid = make_id("INT", interview_n + 3, 2026)
        old_start = datetime.fromisoformat(old["starts_at"])
        conn.execute("UPDATE interview SET status='RESCHEDULED' WHERE interview_id=?", (old["interview_id"],))
        conn.execute("INSERT INTO interview VALUES (?,?,?,?,?,?,?,?,?)",
            (new_iid, old["application_id"], old["panel_id"], iso(old_start + timedelta(days=7)),
             iso(old_start + timedelta(days=7, hours=1)), old["interview_type"], "SCHEDULED", old["interview_id"], "RESCHEDULED_INTERVIEW"))
        add_truth("interview", new_iid, "RESCHEDULED_INTERVIEW", "KEEP_BOTH_EVENTS", "Rescheduled interview points to the original record; original status and scheduling history are retained.")

    insert_many(conn, "ground_truth", truth)
    conn.commit()

    # Export source tables to CSV and JSON, keeping ground truth separate from operational inputs.
    for table in CSV_TABLES:
        rows = conn.execute(f"SELECT * FROM {table}").fetchall()
        cols = [d[0] for d in conn.execute(f"SELECT * FROM {table} LIMIT 0").description]
        with (output / f"{table}.csv").open("w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f); writer.writerow(cols); writer.writerows(rows)
        (output / f"{table}.json").write_text(json.dumps([dict(zip(cols, row)) for row in rows], indent=2), encoding="utf-8")
    (output / "ground_truth.json").write_text(json.dumps(truth, indent=2), encoding="utf-8")
    (output / "recruitment.sql").write_text("\n".join(conn.iterdump()) + "\n", encoding="utf-8")
    with (output / "ground_truth.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(truth[0].keys()) if truth else ["anomaly_id"])
        writer.writeheader(); writer.writerows(truth)

    validation = validate(conn)
    actual_counts = {t: conn.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0] for t in CSV_TABLES}
    baseline_counts = {"requisitions": actual_counts["requisition"], "candidates": actual_counts["candidate"],
        "applications": actual_counts["application"], "interviews": len(interviews)}
    volume_targets_met = (baseline_counts["requisitions"] == counts["requisitions"] and
        baseline_counts["candidates"] == counts["candidates"] and baseline_counts["applications"] == counts["applications"] and
        baseline_counts["interviews"] == counts["interviews"])
    summary = {"seed": seed, "scale": scale, "requested_counts": counts, "baseline_counts": baseline_counts,
        "volume_targets_met": volume_targets_met, "actual_counts_including_labelled_cases": actual_counts,
        "ground_truth_count": len(truth), "validation": validation}
    (output / "validation_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    manifest = {"generator": "src.generator", "seed": seed, "scale": scale, "synthetic_only": True,
        "provenance": "Generated locally from documented deterministic rules; no external candidate or employee data used.",
        "external_sources": [], "tables": CSV_TABLES,
        "ground_truth_files": ["ground_truth.csv", "ground_truth.json"],
        "generator_command": f"python -m src.generator --output OUTPUT_DIR --seed {seed} --scale {scale}"}
    (output / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    checksums = {}
    for path in sorted(output.iterdir()):
        if path.is_file() and path.name not in {"checksums.sha256", "recruitment.db"}:
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            checksums[path.name] = digest
    (output / "checksums.sha256").write_text("".join(f"{digest}  {name}\n" for name, digest in checksums.items()), encoding="utf-8")
    conn.close()
    return summary


def validate(conn: sqlite3.Connection) -> dict[str, Any]:
    checks: dict[str, Any] = {}
    checks["foreign_key_violations"] = [list(r) for r in conn.execute("PRAGMA foreign_key_check")]
    checks["duplicate_primary_keys"] = []
    for table in CSV_TABLES + ["ground_truth"]:
        pk = conn.execute(f"PRAGMA table_info({table})").fetchall()
        pk_cols = [r[1] for r in pk if r[5] > 0]
        if pk_cols:
            group = ",".join(pk_cols)
            dupes = conn.execute(f"SELECT {group}, COUNT(*) c FROM {table} GROUP BY {group} HAVING c>1").fetchall()
            if dupes: checks["duplicate_primary_keys"].append({"table": table, "duplicates": [list(x) for x in dupes]})
    checks["invalid_dates"] = conn.execute("SELECT COUNT(*) FROM requisition WHERE closes_on < opened_on").fetchone()[0]
    checks["invalid_interview_ranges"] = conn.execute("SELECT COUNT(*) FROM interview WHERE ends_at <= starts_at").fetchone()[0]
    checks["application_id_mismatches"] = conn.execute("""SELECT COUNT(*) FROM application
        WHERE application_id != 'APP-' || candidate_id || '-' || req_id""").fetchone()[0]
    checks["application_latest_event_mismatches"] = conn.execute("""SELECT COUNT(*) FROM application a
        WHERE a.current_stage != (SELECT e.to_stage FROM application_event e WHERE e.application_id=a.application_id
          ORDER BY e.event_at DESC, e.event_id DESC LIMIT 1)""").fetchone()[0]
    checks["invalid_stage_transitions"] = 0
    transition_rules = {"APPLIED": {"SCREENING", "WITHDRAWN", "REJECTED"},
        "SCREENING": {"TECHNICAL", "WITHDRAWN", "REJECTED"},
        "TECHNICAL": {"PANEL", "WITHDRAWN", "REJECTED"},
        "PANEL": {"OFFER", "WITHDRAWN", "REJECTED"},
        "OFFER": {"HIRED", "WITHDRAWN", "REJECTED"}}
    for from_stage, to_stage in conn.execute("SELECT from_stage,to_stage FROM application_event WHERE from_stage IS NOT NULL"):
        if to_stage not in transition_rules.get(from_stage, set()):
            checks["invalid_stage_transitions"] += 1
    checks["unlabelled_panel_requisition_mismatches"] = conn.execute("""SELECT COUNT(*) FROM interview i
        JOIN application a USING(application_id) JOIN interview_panel p USING(panel_id)
        WHERE p.req_id != a.req_id AND i.issue_type IS NULL""").fetchone()[0]
    checks["unavailable_panel_bookings"] = conn.execute("""SELECT COUNT(*) FROM interview i
        JOIN panel_interviewer pi ON pi.panel_id=i.panel_id
        WHERE i.issue_type IS NULL AND NOT EXISTS (
          SELECT 1 FROM availability av WHERE av.interviewer_id=pi.interviewer_id AND av.status='AVAILABLE'
          AND av.starts_at <= i.starts_at AND av.ends_at >= i.ends_at
        )""").fetchone()[0]
    checks["scorecard_derived_score_mismatches"] = conn.execute("""SELECT COUNT(*) FROM scorecard s
        WHERE s.status='SUBMITTED' AND abs(s.overall_score - (SELECT round(avg(si.score),2) FROM scorecard_item si
          WHERE si.scorecard_id=s.scorecard_id AND si.is_relevant=1)) > 0.001""").fetchone()[0]
    checks["approval_status_mismatches"] = conn.execute("""SELECT COUNT(*) FROM offer o
        WHERE o.status IN ('APPROVED','REJECTED') AND NOT EXISTS (
          SELECT 1 FROM approval ap WHERE ap.offer_id=o.offer_id AND ap.decision=o.status
        )""").fetchone()[0]
    checks["ground_truth_missing_targets"] = 0
    entity_tables = {"application_event": "application_event", "interview": "interview", "offer": "offer",
        "scorecard": "scorecard", "scorecard_item": "scorecard_item"}
    for entity_type, entity_table in entity_tables.items():
        checks["ground_truth_missing_targets"] += conn.execute(
            f"SELECT COUNT(*) FROM ground_truth g WHERE g.entity_type=? AND NOT EXISTS (SELECT 1 FROM {entity_table} x WHERE x.{'scorecard_item_id' if entity_table == 'scorecard_item' else 'scorecard_id' if entity_table == 'scorecard' else 'event_id' if entity_table == 'application_event' else 'interview_id' if entity_table == 'interview' else 'offer_id'}=g.entity_id)",
            (entity_type,)).fetchone()[0]
    checks["unlabelled_issue_records"] = 0
    labelled_tables = [("application_event", "event_id"), ("interview", "interview_id"), ("offer", "offer_id"),
        ("scorecard", "scorecard_id"), ("scorecard_item", "scorecard_item_id")]
    for table, id_col in labelled_tables:
        checks["unlabelled_issue_records"] += conn.execute(
            f"SELECT COUNT(*) FROM {table} x WHERE x.issue_type IS NOT NULL AND NOT EXISTS "
            f"(SELECT 1 FROM ground_truth g WHERE g.entity_type=? AND g.entity_id=x.{id_col} AND g.issue_type=x.issue_type)",
            (table,)).fetchone()[0]
    checks["unlabelled_non_panel_reviewers"] = conn.execute("""SELECT COUNT(*) FROM scorecard s
        JOIN interview i USING(interview_id) LEFT JOIN panel_interviewer pi
          ON pi.panel_id=i.panel_id AND pi.interviewer_id=s.reviewer_id
        WHERE pi.panel_id IS NULL AND s.issue_type IS NULL""").fetchone()[0]
    checks["offer_band_violations"] = conn.execute("""SELECT COUNT(*) FROM offer o JOIN application a USING(application_id)
        JOIN requisition r USING(req_id) WHERE (o.annual_salary < r.min_salary OR o.annual_salary > r.max_salary)
        AND NOT EXISTS (SELECT 1 FROM ground_truth g WHERE g.entity_id=o.offer_id AND g.issue_type=o.issue_type)""").fetchone()[0]
    checks["unlabelled_overlap_count"] = conn.execute("""SELECT COUNT(*) FROM interview i1 JOIN interview i2
        ON i1.interview_id < i2.interview_id AND i1.starts_at < i2.ends_at AND i1.ends_at > i2.starts_at
        WHERE i1.issue_type IS NULL AND i2.issue_type IS NULL
        AND EXISTS (
          SELECT 1 FROM panel_interviewer p1 JOIN panel_interviewer p2 ON p1.interviewer_id=p2.interviewer_id
          WHERE p1.panel_id=i1.panel_id AND p2.panel_id=i2.panel_id
        )""").fetchone()[0]
    checks["ground_truth_labels"] = conn.execute("SELECT COUNT(*) FROM ground_truth").fetchone()[0]
    checks["unlabelled_withdrawn_schedules"] = conn.execute("""SELECT COUNT(*) FROM interview i JOIN application a USING(application_id)
        WHERE a.current_stage='WITHDRAWN' AND i.issue_type IS NULL""").fetchone()[0]
    checks["unlabelled_irrelevant_scorecards"] = conn.execute("""SELECT COUNT(*) FROM scorecard_item s
        WHERE s.is_relevant=0 AND NOT EXISTS (SELECT 1 FROM ground_truth g WHERE g.entity_id=s.scorecard_item_id)""").fetchone()[0]
    checks["unlabelled_incomplete_scorecards"] = conn.execute("""SELECT COUNT(*) FROM scorecard s
        WHERE (s.status='DRAFT' OR s.submitted_at IS NULL) AND NOT EXISTS
        (SELECT 1 FROM ground_truth g WHERE g.entity_id=s.scorecard_id AND g.issue_type='INCOMPLETE_SCORECARD')""").fetchone()[0]
    checks["unlabelled_gate_failures"] = conn.execute("""SELECT COUNT(*) FROM application_event e
        WHERE e.gate_passed=0 AND NOT EXISTS (SELECT 1 FROM ground_truth g WHERE g.entity_id=e.event_id)""").fetchone()[0]
    checks["pass"] = (not checks["foreign_key_violations"] and not checks["duplicate_primary_keys"] and
        checks["invalid_dates"] == 0 and checks["invalid_interview_ranges"] == 0 and checks["application_id_mismatches"] == 0 and
        checks["application_latest_event_mismatches"] == 0 and checks["invalid_stage_transitions"] == 0 and
        checks["unlabelled_panel_requisition_mismatches"] == 0 and checks["unlabelled_non_panel_reviewers"] == 0 and
        checks["unavailable_panel_bookings"] == 0 and checks["scorecard_derived_score_mismatches"] == 0 and
        checks["approval_status_mismatches"] == 0 and checks["ground_truth_missing_targets"] == 0 and
        checks["unlabelled_issue_records"] == 0 and checks["offer_band_violations"] == 0 and checks["unlabelled_overlap_count"] == 0 and
        checks["unlabelled_withdrawn_schedules"] == 0 and checks["unlabelled_irrelevant_scorecards"] == 0 and checks["unlabelled_incomplete_scorecards"] == 0 and checks["unlabelled_gate_failures"] == 0)
    return checks


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate deterministic synthetic recruitment workflow data")
    parser.add_argument("--output", type=Path, default=Path("data/generated"))
    parser.add_argument("--seed", type=int, default=SEED_DEFAULT)
    parser.add_argument("--scale", type=float, default=1.0, help="1.0 = full volume; 0.1 = starter volume")
    args = parser.parse_args()
    summary = generate(args.output, args.seed, args.scale)
    print(json.dumps(summary, indent=2))
    if not summary["validation"]["pass"]:
        raise SystemExit(1)

if __name__ == "__main__":
    main()
