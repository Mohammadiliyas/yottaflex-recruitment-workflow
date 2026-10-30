from __future__ import annotations
import argparse, json, sqlite3
from pathlib import Path
try:
    from .generator import validate
except ImportError:
    from generator import validate


def main() -> None:
    p = argparse.ArgumentParser(description="Validate recruitment database integrity")
    p.add_argument("database", type=Path, nargs="?", default=Path("data/generated/recruitment.db"))
    args = p.parse_args()
    conn = sqlite3.connect(args.database)
    result = validate(conn)
    # Additional domain checks: event gate failures remain explicit labelled cases.
    result["ungrounded_gate_failures"] = conn.execute("SELECT COUNT(*) FROM application_event e LEFT JOIN ground_truth g ON g.entity_id=e.event_id WHERE e.gate_passed=0 AND g.anomaly_id IS NULL").fetchone()[0]
    result["unlabelled_withdrawn_schedules"] = conn.execute("""SELECT COUNT(*) FROM interview i JOIN application a USING(application_id)
      WHERE a.current_stage='WITHDRAWN' AND i.issue_type IS NULL""").fetchone()[0]
    result["unlabelled_irrelevant_scorecards"] = conn.execute("SELECT COUNT(*) FROM scorecard_item WHERE is_relevant=0 AND scorecard_item_id NOT IN (SELECT entity_id FROM ground_truth)").fetchone()[0]
    result["unlabelled_incomplete_scorecards"] = conn.execute("SELECT COUNT(*) FROM scorecard WHERE (status='DRAFT' OR submitted_at IS NULL) AND scorecard_id NOT IN (SELECT entity_id FROM ground_truth WHERE issue_type='INCOMPLETE_SCORECARD')").fetchone()[0]
    result["pass"] = result["pass"] and result["ungrounded_gate_failures"] == 0 and result["unlabelled_withdrawn_schedules"] == 0 and result["unlabelled_irrelevant_scorecards"] == 0 and result["unlabelled_incomplete_scorecards"] == 0
    print(json.dumps(result, indent=2))
    conn.close()
    if not result["pass"]:
        raise SystemExit(1)

if __name__ == "__main__": main()
