# Full-scale verification results

**Generator:** `src.generator`  
**Seed:** `20261022`  
**Scale:** `1.0`  
**Provenance:** Synthetic records only; no external candidate/employee source used.

## Requested baseline volume

| Entity | Required baseline | Generated baseline | Result |
|---|---:|---:|---|
| Requisition | 200 | 200 | PASS |
| Candidate | 5,000 | 5,000 | PASS |
| Application | 8,000 | 8,000 | PASS |
| Interview | 2,000 | 2,000 | PASS |

The physical interview table contains 2,003 rows after appending two labelled negative-scenario interviews and one rescheduled interview record. The 2,000 baseline interview records are counted separately in `baseline_counts`.

## Additional generated records

| Table | Rows |
|---|---:|
| HiringManager | 100 |
| SkillRequirement | 1,010 |
| CandidateSkill | 37,540 |
| InterviewPanel | 200 |
| PanelInterviewer | 600 |
| Availability | 68,800 |
| Interview (including labelled cases) | 2,003 |
| Scorecard | 6,000 |
| ScorecardItem | 24,000 |
| Offer | 219 |
| Approval | 219 |
| ApplicationEvent | 17,782 |
| Ground-truth labels | 7 |

## Operational metrics from the generated database

| Metric | Value |
|---|---:|
| Requisitions open or approved | 200 |
| Candidates | 5,000 |
| Applications | 8,000 |
| Completed interviews | 1,999 |
| Completed interviews / applications | 0.2499 |
| Mean submitted relevant rubric score | 3.501 / 5 |
| Offers | 219 |
| Offer approval rate | 0.9954 |

The completed-interview metric is 1,999 because the source interview history retains one original interview in `RESCHEDULED` state; the replacement is preserved as a separate linked row.

## Ground-truth exception coverage

1. `MISSING_REQUIRED_REVIEW` — application advances to technical without passing the required review gate.
2. `INTERVIEWER_DOUBLE_BOOKED` — deliberately overlapping panel booking.
3. `OFFER_EXCEEDS_BAND` — offer salary above requisition maximum; approval remains pending.
4. `WITHDRAWN_CANDIDATE_SCHEDULED` — a withdrawn application still has a scheduled interview.
5. `IRRELEVANT_EVALUATION_CRITERION` — an unrelated rubric item is explicitly marked irrelevant.
6. `INCOMPLETE_SCORECARD` — reviewer rubric is incomplete and remains a draft.
7. `RESCHEDULED_INTERVIEW` — new interview references original interview; original record is retained.

Ground truth is exported separately from operational CSV/JSON files and must not be used as an input feature set for anomaly detection.

## Integrity validation

The full-volume validator passed with zero counts for:

- Primary-key duplicates and foreign-key violations.
- Invalid date ranges and invalid interview duration.
- Application ID / parent ID mismatches and current-stage / latest-event mismatches.
- Invalid lifecycle transitions and unlabelled failed gates.
- Panel/requisition mismatches, unavailable panel bookings, and unlabelled interviewer overlaps.
- Scorecard aggregate reconciliation errors and unlabelled incomplete/irrelevant scorecards.
- Offer compensation-band violations and approval/status mismatches.
- Missing ground-truth target rows and unlabelled issue records.

## Reproducibility

Two independent full-scale runs using seed `20261022` and scale `1.0` produced identical SHA-256 manifests for all generated CSV, JSON, SQL, and metadata files (35 files compared, excluding the SQLite binary and checksum file itself). Baseline counts matched between both runs, and both validation summaries passed.

The SQLite binary is excluded from the checksum comparison because the portable SQL dump and CSV/JSON exports are the reproducibility evidence; the database is independently recreated by the same seed and generator.

## Commands used

```bash
python -m src.generator --output data/full --seed 20261022 --scale 1.0
python -m src.validate data/full/recruitment.db
python -m unittest discover -s tests -v
python scripts/reproducibility_check.py --seed 20261022 --scale 0.02
```

The full-scale repeat was run independently twice and its two generated folders were compared file-by-file; the commands above include the reusable small-scale reproducibility helper. The full-scale comparison results are summarized in this file.

## Repository-matched assistant verification — 31 October 2026

The source and export ZIPs were retrieved from the project Library folder and checked against the public GitHub repository. Git blob IDs matched for the tested source files and the full export archive at the time of verification. This ties the following checks to the source and dataset artifacts committed to the repository.

The source ZIP was extracted to `/mnt/data/yottaflex-verify/source/yottaflex-recruitment`; the full-volume export ZIP was extracted to `/mnt/data/yottaflex-verify/data/yottaflex-full-data-exports`. Git blob IDs for the five test/source files matched the corresponding files on GitHub `main`, and the export ZIP matched the committed GitHub artifact. Commands executed from that source directory:

```bash
python -m unittest discover -s tests -v
python -m src.validate /mnt/data/yottaflex-verify/data/yottaflex-full-data-exports/recruitment.db
python scripts/reproducibility_check.py --seed 20261022 --scale 0.02
```

Observed results:

| Check | Result |
|---|---|
| Unit test suite | 6 passed |
| Validator on committed full-volume SQLite export | pass: true; 7 ground-truth labels; zero reported configured unlabelled integrity failures |
| Reproducibility helper, seed 20261022, scale 0.02 | All 35 generated CSV, JSON, SQL and metadata files identical across both runs |

The small-scale reproducibility check above is a fresh assistant-side run. The earlier full-scale two-run comparison remains the result documented in the Reproducibility section; it was not repeated on 31 October.

The dashboard code (app.py) was not covered by the local unit-test run. Render service logs recorded successful HTTP 200 responses for /, /applications, /requisitions and /anomalies after deployment.

**Attribution:** these commands were run by the AI assistant in its verification environment. They were not run personally by the candidate. This section must not be represented as candidate-executed testing.

## Final repository recheck — 1 November 2026

The source and data archives were freshly retrieved from the project Library and compared against the current public GitHub `main` branch. Git blob IDs matched for `src/generator.py`, `src/workflow.py`, `src/validate.py`, `tests/test_workflow.py`, `scripts/reproducibility_check.py`, and `artifacts/yottaflex-full-data-exports.zip`.

Fresh commands executed against those exact repository-matched files:

```bash
python -m unittest discover -s tests -v
python -m src.validate /mnt/data/yottaflex-final-check/data/yottaflex-full-data-exports/recruitment.db
python scripts/reproducibility_check.py --seed 20261022 --scale 0.02
```

Fresh results:

- Unit tests: **6 passed**.
- Full-volume database validation: **pass: true**, seven labelled ground-truth cases, and zero configured unlabelled integrity failures.
- Small-scale reproducibility smoke test (seed `20261022`, scale `0.02`): **all 35 CSV, JSON, SQL and metadata outputs matched** across the two runs.

Attribution: the checks above were run by the AI assistant on 1 November 2026, not personally by the candidate. The small-scale reproducibility run does not replace the separately recorded prior full-scale repeat-generation result.
