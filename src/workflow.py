from __future__ import annotations
import sqlite3
from datetime import datetime, timezone
from typing import Any

ALLOWED = {
    "APPLIED": {"SCREENING", "WITHDRAWN", "REJECTED"},
    "SCREENING": {"TECHNICAL", "WITHDRAWN", "REJECTED"},
    "TECHNICAL": {"PANEL", "WITHDRAWN", "REJECTED"},
    "PANEL": {"OFFER", "WITHDRAWN", "REJECTED"},
    "OFFER": {"HIRED", "WITHDRAWN", "REJECTED"},
}

class RuleViolation(ValueError):
    """Raised when a requested business action violates a workflow rule."""


def transition_application(conn: sqlite3.Connection, application_id: str, to_stage: str,
                            actor_id: str, reason: str, *, required_review_complete: bool) -> str:
    row = conn.execute("SELECT current_stage FROM application WHERE application_id=?", (application_id,)).fetchone()
    if not row:
        raise RuleViolation(f"Unknown application: {application_id}")
    current = row[0]
    if to_stage not in ALLOWED.get(current, set()):
        raise RuleViolation(f"Illegal transition {current} -> {to_stage}")
    if to_stage in {"TECHNICAL", "PANEL", "OFFER", "HIRED"} and not required_review_complete:
        raise RuleViolation("Required review is incomplete; stage transition blocked")
    cur = conn.execute("UPDATE application SET current_stage=?, updated_at=? WHERE application_id=?",
                       (to_stage, datetime.now(timezone.utc).isoformat(timespec="minutes"), application_id))
    conn.execute("INSERT INTO application_event(event_id,application_id,from_stage,to_stage,event_at,actor_id,reason,gate_passed,issue_type) VALUES(?,?,?,?,?,?,?,?,?)",
                 (f"EVT-MANUAL-{application_id}-{to_stage}", application_id, current, to_stage,
                  datetime.now(timezone.utc).isoformat(timespec="minutes"), actor_id, reason, 1, None))
    conn.commit()
    return to_stage


def schedule_interview(conn: sqlite3.Connection, interview_id: str, application_id: str, panel_id: str,
                       starts_at: str, ends_at: str, interview_type: str = "TECHNICAL_PANEL") -> None:
    if ends_at <= starts_at:
        raise RuleViolation("Interview end must be after start")
    app = conn.execute("SELECT current_stage FROM application WHERE application_id=?", (application_id,)).fetchone()
    if not app:
        raise RuleViolation("Unknown application")
    if app[0] in {"WITHDRAWN", "REJECTED", "HIRED"}:
        raise RuleViolation(f"Cannot schedule candidate in terminal state {app[0]}")
    members = [r[0] for r in conn.execute("SELECT interviewer_id FROM panel_interviewer WHERE panel_id=?", (panel_id,))]
    if not members:
        raise RuleViolation("Panel has no interviewers")
    for member in members:
        overlap = conn.execute("""SELECT 1 FROM interview i JOIN panel_interviewer pi ON pi.panel_id=i.panel_id
            WHERE pi.interviewer_id=? AND i.status IN ('SCHEDULED','COMPLETED')
            AND i.starts_at < ? AND i.ends_at > ? LIMIT 1""", (member, ends_at, starts_at)).fetchone()
        if overlap:
            raise RuleViolation(f"Interviewer {member} has a scheduling conflict")
        available = conn.execute("""SELECT 1 FROM availability WHERE interviewer_id=? AND status='AVAILABLE'
            AND starts_at <= ? AND ends_at >= ? LIMIT 1""", (member, starts_at, ends_at)).fetchone()
        if not available:
            raise RuleViolation(f"Interviewer {member} is not available for this time")
    conn.execute("INSERT INTO interview(interview_id,application_id,panel_id,starts_at,ends_at,interview_type,status,rescheduled_from,issue_type) VALUES(?,?,?,?,?,?,'SCHEDULED',NULL,NULL)",
                 (interview_id, application_id, panel_id, starts_at, ends_at, interview_type))
    conn.commit()


def create_offer(conn: sqlite3.Connection, offer_id: str, application_id: str, salary: int,
                 issued_on: str, expires_on: str) -> None:
    row = conn.execute("""SELECT a.current_stage,r.min_salary,r.max_salary FROM application a
        JOIN requisition r USING(req_id) WHERE a.application_id=?""", (application_id,)).fetchone()
    if not row:
        raise RuleViolation("Unknown application")
    stage, low, high = row
    if stage != "OFFER":
        raise RuleViolation("Offer requires application at OFFER stage")
    if not low <= salary <= high:
        raise RuleViolation(f"Offer salary {salary} is outside approved band {low}-{high}")
    if expires_on < issued_on:
        raise RuleViolation("Offer expiry cannot precede issue date")
    conn.execute("INSERT INTO offer(offer_id,application_id,annual_salary,currency,status,issued_on,expires_on,issue_type) VALUES(?,?,?,'INR','PENDING_APPROVAL',?,?,?,NULL)",
                 (offer_id, application_id, salary, issued_on, expires_on))
    conn.commit()


def approve_offer(conn: sqlite3.Connection, approval_id: str, offer_id: str, approver_id: str,
                  decision: str, decided_at: str, comments: str) -> None:
    row = conn.execute("""SELECT o.annual_salary,r.min_salary,r.max_salary FROM offer o
        JOIN application a USING(application_id) JOIN requisition r USING(req_id) WHERE o.offer_id=?""", (offer_id,)).fetchone()
    if not row:
        raise RuleViolation("Unknown offer")
    salary, low, high = row
    if decision == "APPROVED" and not low <= salary <= high:
        raise RuleViolation("Out-of-band offer cannot be approved")
    if decision not in {"APPROVED", "REJECTED", "PENDING"}:
        raise RuleViolation("Unsupported approval decision")
    conn.execute("INSERT INTO approval VALUES(?,?,?,?,?,?)", (approval_id, offer_id, approver_id, decision, decided_at, comments))
    new_status = "APPROVED" if decision == "APPROVED" else "REJECTED" if decision == "REJECTED" else "PENDING_APPROVAL"
    conn.execute("UPDATE offer SET status=? WHERE offer_id=?", (new_status, offer_id))
    conn.commit()


def dashboard_metrics(conn: sqlite3.Connection) -> dict[str, Any]:
    scalar = lambda q: conn.execute(q).fetchone()[0]
    stage_counts = {r[0]: r[1] for r in conn.execute("SELECT current_stage,COUNT(*) FROM application GROUP BY current_stage")}
    total_apps = scalar("SELECT COUNT(*) FROM application")
    total_interviews = scalar("SELECT COUNT(*) FROM interview WHERE status='COMPLETED'")
    score_avg = conn.execute("""SELECT AVG(si.score) FROM scorecard_item si JOIN scorecard s USING(scorecard_id)
        WHERE si.is_relevant=1 AND s.status='SUBMITTED' AND s.submitted_at IS NOT NULL""").fetchone()[0]
    offers = scalar("SELECT COUNT(*) FROM offer")
    approved = scalar("SELECT COUNT(*) FROM offer WHERE status IN ('APPROVED','ACCEPTED')")
    conflict_count = scalar("SELECT COUNT(*) FROM ground_truth WHERE issue_type='INTERVIEWER_DOUBLE_BOOKED'")
    return {
        "requisitions_open_or_approved": scalar("SELECT COUNT(*) FROM requisition WHERE status IN ('OPEN','APPROVED')"),
        "candidates": scalar("SELECT COUNT(*) FROM candidate"), "applications": total_apps,
        "applications_by_stage": stage_counts, "completed_interviews": total_interviews,
        "interview_completion_per_application": round(total_interviews / total_apps, 4) if total_apps else 0,
        "mean_relevant_score": round(score_avg, 3) if score_avg is not None else None,
        "offers": offers, "offer_approval_rate": round(approved / offers, 4) if offers else 0,
        "known_anomalies": scalar("SELECT COUNT(*) FROM ground_truth"),
        "known_interviewer_conflict_cases": conflict_count,
    }
