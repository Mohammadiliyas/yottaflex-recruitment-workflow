# YottaFlex AI — Recruitment Workflow & Synthetic Data Generator

A reproducible, locally runnable reference implementation for end-to-end recruitment operations: approved requisitions, candidate profiles and applications, stage gates, interviewer availability, conflict-aware panel scheduling, rubric scorecards, compensation-band offers, approvals, audit events and exception labels.

> **Data notice:** All included/generated candidate and employee records are synthetic. No external candidate dataset or personal information is used. `ground_truth.csv/json` is a separate label set and must not be joined into model features used to detect anomalies.

## What is implemented

- Relational SQLite model for HiringManager, Requisition, Candidate, Application, SkillRequirement, InterviewPanel, Availability, Interview, Scorecard, Offer and Approval, plus candidate skills, panel membership, normalized scorecard rubric items, application event history and ground truth.
- Deterministic IDs, fixed seed (`20261022`), parameterized generation and CSV + JSON + SQLite exports.
- Business rules for stage transitions, mandatory review gate, interviewer availability/conflicts, terminal candidate states, offer salary bands and approval decisions.
- Explicit exception examples: missing required review, interviewer double-booking, out-of-band offer, withdrawn candidate still scheduled, irrelevant scorecard criterion. A reschedule record points to the original interview instead of overwriting it.
- Validation checks for primary keys, foreign keys, dates, pay-band reconciliation, overlap exceptions and labelled cases.
- Metrics for funnel stages, interviews per application, relevant scorecard average and offer approval rate.

## Requirements

- Python 3.10 or newer.
- No external services, API keys or paid dependencies.

## Quick start

```bash
python -m venv .venv
# Windows PowerShell: .venv\Scripts\Activate.ps1
# macOS/Linux: source .venv/bin/activate
python -m pip install -r requirements.txt
python -m src.generator --output data/generated --seed 20261022 --scale 0.1
python -m src.validate data/generated/recruitment.db
python scripts/summarize.py data/generated/recruitment.db
python -m unittest discover -s tests -v
python scripts/reproducibility_check.py --scale 0.02
```

To generate the requested full-volume dataset:

```bash
python -m src.generator --output data/full --seed 20261022 --scale 1.0
python -m src.validate data/full/recruitment.db
```

The scale parameter applies the same generator to all master and dependent tables. Scale `1.0` targets 200 requisitions, 5,000 candidates, 8,000 applications and 2,000 interviews; scale `0.1` is a quicker smoke-test dataset. The verified full-volume run with seed `20261022` met all four targets exactly. The physical `interview` table contains 2,003 rows because it also retains two labelled exception interviews and one rescheduled interview. The full run also generated 6,000 scorecards, 24,000 rubric items and 219 offers/approvals. `validation_summary.json` reports target baseline counts separately from all physical row counts. See `docs/VALIDATION_RESULTS.md` for detailed counts, metrics, exception coverage, and two-run full-scale checksum comparison.

## Project structure

```text
src/
  generator.py       deterministic synthetic data + schema + exports + validation
  workflow.py        stage, scheduling and offer/approval rules + metrics
  validate.py        command-line integrity and exception validation
 tests/
  test_workflow.py   core rule and data-model tests
 docs/
  DATA_DICTIONARY.md field definitions and relationships
  DESIGN.md          assumptions, lifecycle, metrics and limitations
  AI_DISCLOSURE.md   AI-use disclosure and prompt-history procedure
  PROMPT_HISTORY.md  prompts recorded for this project
  VALIDATION_RESULTS.md full-scale test and reproducibility evidence
 data/               generated outputs (not committed by default)
```

## Data exports

The generator writes one `.csv` and one `.json` per operational table, plus `recruitment.db`, a portable `recruitment.sql` seed dump, `manifest.json`, `validation_summary.json`, `checksums.sha256`, and the separate `ground_truth.csv/json`. Do not put `ground_truth` into operational model features. Do not commit large full-volume exports unless specifically requested; generator and smaller smoke-test evidence are sufficient to reproduce them.

## Reproducibility

Run the same command twice into separate folders. Compare row counts and SHA-256 checksums of CSV/JSON/SQL outputs and metadata. `scripts/reproducibility_check.py` automates this. The seed controls random choices; output ordering is deterministic.

## Key design decisions

1. SQLite + Python standard library keeps the project fully local and easy to audit.
2. Source records and event records are separated. State snapshots are convenient for reads; application transitions are also appended to `application_event`.
3. Anomalies are injected only after baseline records are valid and are explicitly labelled via `issue_type` and `ground_truth`.
4. A validator distinguishes expected, labelled exception records from unlabelled data-integrity failures.
5. Scheduling uses interviewer panel membership, availability windows and overlapping interval checks before an operational booking is inserted.

## Known limitations to review

- The generator creates a relational data and rules-engine demonstration, not a production ATS or multi-user web interface.
- At non-full scales, interview counts scale with the eligible candidate pool; inspect `baseline_counts` in `validation_summary.json`.
- Synthetic scoring and skill profiles are designed for workflow testing, not hiring decisions. Do not use them to rank real people.
- A manager table represents both hiring managers and interviewers to keep the exercise compact. Candidate, manager, HR and IT/operations responsibilities are represented in workflow relationships and panel roles; actual authentication, system-admin controls and full role-based permissions are not implemented.
- This is a local data generator and business-rules engine, not a hosted ATS web UI or multi-user service. Review the code, run the tests, inspect the generated outputs and update the AI disclosure with the tools/prompts you used before submission.

## Submission checklist

- [ ] Repository is public and is a dedicated project repository.
- [ ] README setup/run instructions verified on a clean environment.
- [x] Full-volume generator run and validation completed in the build workspace.
- [x] Six unit tests pass.
- [x] Full-scale fixed-seed repeat and 35-file checksum comparison pass.
- [ ] Create the dedicated public GitHub repository and push this source package.
- [ ] Candidate completes personal code review and final AI disclosure.
- [ ] Prompt history includes every prompt submitted to every AI tool used.
- [ ] AI disclosure truthfully describes what was AI-assisted and what you personally reviewed/changed/validated.
- [ ] No secrets, real candidate details or unauthorized proprietary content committed.
- [ ] Final repository link is submitted from the same recruitment email address used in the process.

See `docs/AI_DISCLOSURE.md` and `docs/PROMPT_HISTORY.md`. YottaFlex's attached submission guideline specifies a 72-hour window, public repository, prompt history, and a walkthrough of assumptions, decisions, trade-offs, tests and limitations. Its FAQ says individual work is required, hosted demo/automated tests are not mandatory, and incomplete requirements must be explicitly disclosed.
