# YottaFlex AI — Recruitment Workflow & Synthetic Data Generator

A reproducible recruitment workflow reference implementation covering requisitions, synthetic candidate profiles and applications, stage gates, interviewer availability, conflict-aware scheduling, rubric scorecards, compensation-band offers, approvals, audit events and labelled exceptions.

> **Data notice:** All candidate and employee records are synthetic. The separate ground_truth table/file set contains known edge-case labels and must not be joined into model input features for anomaly detection.

## What is implemented

- Relational SQLite model for recruitment master, transaction and event entities.
- Deterministic data generation with fixed seed 20261022; CSV, JSON, SQL and SQLite exports.
- Business rules for stage transitions, review gates, interviewer availability/conflicts, terminal states, salary bands and approvals.
- Explicit labelled exception examples and a separate ground-truth register.
- Data validation, unit tests and reproducibility utilities.
- A read-only Flask dashboard for viewing KPIs, applications, requisitions and labelled anomalies.

## Browser dashboard demo

**Live demo:** https://yottaflex-recruitment-demo.onrender.com

The dashboard includes:
- Overview KPIs and application pipeline counts
- Searchable application records and stage filters
- Requisition list with role, location, openings and salary bands
- A register of the seven intentionally labelled workflow edge cases

The web app reads the committed SQLite export from artifacts/yottaflex-full-data-exports.zip. At startup it extracts the database to a temporary directory unless YOTTAFLEX_DB points to an existing database file.

**Demo limitation:** this is a read-only visualization over synthetic records. It does not provide authentication, recruiter/manager role permissions, create/update operations or a production ATS workflow.

## Requirements and local setup

- Python 3.10 or newer.
- Python dependencies are listed in requirements.txt (Flask and Gunicorn for the dashboard).

```bash
python -m venv .venv
# Windows PowerShell: .venv\Scripts\Activate.ps1
# macOS/Linux: source .venv/bin/activate
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
```

To run the dashboard locally, extract artifacts/yottaflex-full-data-exports.zip into data/full, then run:

```bash
python app.py
```

Open http://127.0.0.1:5000.

To regenerate the full dataset from source:

```bash
python -m src.generator --output data/full --seed 20261022 --scale 1.0
python -m src.validate data/full/recruitment.db
```

For a faster smoke-test dataset use --scale 0.1. See the source code and docs/VALIDATION_RESULTS.md for detailed entity counts, validation results and reproducibility evidence.

## Full-volume data exports

The repository includes artifacts/yottaflex-full-data-exports.zip, containing CSV and JSON table exports, a SQLite database, SQL dump, manifest, validation summary and checksums. Extract the archive to inspect individual datasets. Keep ground_truth separate from operational model features.

## Project structure

```text
app.py                 read-only Flask dashboard
src/
  generator.py         deterministic synthetic data + schema + exports + validation
  workflow.py          stage, scheduling and offer/approval rules + metrics
  validate.py          command-line integrity and exception validation
scripts/
  reproducibility_check.py
  summarize.py
tests/
  test_workflow.py
docs/
  DATA_DICTIONARY.md
  DESIGN.md
  AI_DISCLOSURE.md
  PROMPT_HISTORY.md
  VALIDATION_RESULTS.md
artifacts/
  yottaflex-full-data-exports.zip
```

## Design decisions and limitations

1. SQLite and Python keep generation and validation easy to reproduce locally.
2. State snapshots and application event history are separate so transitions remain traceable.
3. Baseline records are generated before labelled edge cases are injected.
4. The validator separates expected labelled exceptions from unlabelled integrity failures.
5. Scheduling checks interviewer panel membership, availability and overlapping intervals.

**Implementation caveats:** `transition_application()` takes `required_review_complete` as a caller-supplied Boolean; it does not query persisted review evidence before allowing a stage transition. `schedule_interview()` checks availability and conflicts but does not confirm that the panel belongs to the application's requisition. `approve_offer()` changes an offer to `APPROVED` after a single approved decision; it does not enforce two distinct role-based approvals (for example, hiring manager and HR partner). These are known gaps between the intended policy and the current implementation.

The project demonstrates synthetic workflow data and business rules, not a production multi-user ATS. Synthetic skill and score data are for workflow testing only and must not be used to rank real people. Authentication, system-administrator controls and complete role-based permissions are not implemented.

## Submission checklist

- [x] Public, dedicated GitHub repository with source, tests, documentation and full data ZIP.
- [x] Full-volume generator output and validation evidence included.
- [x] Six unit tests pass.
- [x] Hosted read-only dashboard deployed.
- [ ] Candidate has personally reviewed and understood the implementation.
- [ ] Prompt history includes every prompt submitted to every AI tool/session.
- [x] AI assistance, personal-review status and candidate test-execution status are disclosed in `docs/AI_DISCLOSURE.md`.
- [ ] Candidate has checked for secrets, real personal data and unauthorized proprietary content.
- [ ] Candidate has verified the assignment deadline and submission method, and submitted the repository link from the required recruitment email address.

YottaFlex's assignment materials specify a 72-hour window, a public repository, prompt history and a walkthrough of assumptions, decisions, trade-offs, tests and limitations. The FAQ states that individual work is required, a hosted demo/automated tests are not mandatory, and incomplete requirements must be explicitly disclosed. Review the original PDFs and confirm the applicable deadline and delivery channel.

See docs/AI_DISCLOSURE.md, docs/PROMPT_HISTORY.md and docs/VALIDATION_RESULTS.md before submission.
