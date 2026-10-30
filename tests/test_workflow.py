import sqlite3
import tempfile
import unittest
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from generator import SCHEMA, generate
from workflow import RuleViolation, transition_application, create_offer, approve_offer, schedule_interview

class WorkflowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.out = Path(cls.tmp.name) / "data"
        generate(cls.out, seed=20261022, scale=0.01)
        cls.db = cls.out / "recruitment.db"

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def connect(self):
        c = sqlite3.connect(self.db)
        c.execute("PRAGMA foreign_keys=ON")
        first = c.execute("SELECT application_id FROM application ORDER BY application_id LIMIT 1").fetchone()[0]
        c.execute("UPDATE application SET current_stage='SCREENING' WHERE application_id=?", (first,))
        c.commit()
        return c

    def test_generator_contains_expected_full_entity_model(self):
        c = self.connect()
        tables = {r[0] for r in c.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        self.assertTrue({"requisition", "candidate", "application", "interview", "scorecard", "scorecard_item", "offer", "approval", "application_event", "ground_truth"}.issubset(tables))
        self.assertEqual(c.execute("PRAGMA foreign_key_check").fetchall(), [])
        c.close()

    def test_block_invalid_transition_without_review(self):
        c = self.connect()
        app_id = c.execute("SELECT application_id FROM application WHERE current_stage='SCREENING' LIMIT 1").fetchone()[0]
        with self.assertRaises(RuleViolation):
            transition_application(c, app_id, "TECHNICAL", "HM-0001", "advance", required_review_complete=False)
        c.close()

    def test_allow_transition_when_gate_is_complete(self):
        c = self.connect()
        app_id = c.execute("SELECT application_id FROM application WHERE current_stage='SCREENING' LIMIT 1").fetchone()[0]
        self.assertEqual(transition_application(c, app_id, "TECHNICAL", "HM-0001", "review passed", required_review_complete=True), "TECHNICAL")
        c.close()

    def test_out_of_band_offer_is_rejected(self):
        c = self.connect()
        row = c.execute("SELECT a.application_id,r.max_salary FROM application a JOIN requisition r USING(req_id) WHERE a.current_stage='OFFER' LIMIT 1").fetchone()
        if row:
            with self.assertRaises(RuleViolation):
                create_offer(c, "OFF-TEST-OUT", row[0], row[1] + 1, "2026-08-01", "2026-08-15")
        c.close()

    def test_approval_rejects_out_of_band_offer(self):
        c = self.connect()
        row = c.execute("SELECT offer_id FROM offer WHERE issue_type='OFFER_EXCEEDS_BAND' LIMIT 1").fetchone()
        if row:
            with self.assertRaises(RuleViolation):
                approve_offer(c, "APR-TEST-OUT", row[0], "HM-0001", "APPROVED", "2026-08-01", "approve")
        c.close()

    def test_withdrawn_candidate_cannot_be_scheduled(self):
        c = self.connect()
        row = c.execute("SELECT a.application_id,p.panel_id FROM application a JOIN interview_panel p USING(req_id) WHERE a.current_stage='WITHDRAWN' LIMIT 1").fetchone()
        if row:
            with self.assertRaises(RuleViolation):
                schedule_interview(c, "INT-TEST-WD", row[0], row[1], "2026-08-01T10:00+00:00", "2026-08-01T11:00+00:00")
        c.close()

if __name__ == "__main__":
    unittest.main()
