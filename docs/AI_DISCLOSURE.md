# AI use and contribution disclosure

**Disclosure date:** 31 October 2026  
**Project:** YottaFlex recruitment workflow and synthetic-data generator  
**Repository:** https://github.com/Mohammadiliyas/yottaflex-recruitment-workflow  
**Hosted demo:** https://yottaflex-recruitment-demo.onrender.com

## AI tools and connected services recorded for this project

| Tool/service | Recorded use |
|---|---|
| ChatGPT (GPT-6) | Used extensively to plan and draft the architecture, Python/SQLite schema, deterministic synthetic-data generator, workflow rules, validation code, unit tests, scripts, documentation and debugging changes. It also assisted with reviewing generated database outputs and preparing the dashboard. |
| GitHub connector | Used to inspect the repository and publish/update source files, the data archive and documentation. |
| Render connector | Used to create and deploy the read-only Flask dashboard from the GitHub repository. |
| Other AI tools/models | **None.** The candidate confirmed on 31 October 2026 that no AI tool other than ChatGPT was used for this assignment. |

The GitHub and Render connectors are recorded as connected services used in the workflow; they are not being represented as additional generative-AI models.

## Scope of AI assistance

AI assistance was extensive. The initial implementation and most project code and documentation were AI-drafted or AI-assisted, including:

- `src/generator.py`: synthetic data generation, schema and export logic.
- `src/workflow.py`: workflow rules, stage transitions, scheduling and offer/approval logic.
- `src/validate.py`: data-integrity and exception validation.
- `tests/test_workflow.py`: unit tests.
- `scripts/`: summary and reproducibility utilities.
- `docs/`: design, data dictionary, validation evidence, AI disclosure and prompt-history documentation.
- `app.py` and `requirements.txt`: the read-only Flask dashboard and its runtime dependencies, added after the data-generation implementation.
- Repository README and deployment support.

AI assistance was also used to debug date, scheduling, data-volume, scorecard-normalization and validation issues. The candidate should be prepared to explain and defend the implementation rather than rely on the fact that it runs.

## Candidate-authored work and personal review

The available conversation record does **not** establish exactly which code changes the candidate independently authored, which files the candidate personally reviewed in depth, or whether the candidate independently ran manual test scenarios. This disclosure therefore does not claim personal authorship, comprehensive code review, or manual testing on the candidate's behalf.

**Candidate's confirmation (31 October 2026):**

The candidate responded “no” to the questions about personal review, independent code changes and personally executed tests. Accordingly, this disclosure records:

- **Files/functions personally reviewed and understood:** None confirmed.
- **Independent code changes made by the candidate:** None confirmed.
- **Manual tests personally executed:** None confirmed. The automated checks described below are recorded project/build results, not candidate-run tests.
- **Other AI tools/models used:** None; the candidate confirmed that ChatGPT was the only AI tool used. The GitHub and Render connectors are recorded separately as connected services.

Do not copy an AI-generated explanation into these fields as evidence of personal understanding. Before a technical walkthrough, the candidate needs to personally study the generator, relational relationships, stage gates, scheduling/conflict logic, rubric scorecards, offer approvals, anomaly labels, validation and dashboard limitations.

## Automated checks and deployment evidence recorded

The repository's `docs/VALIDATION_RESULTS.md` records a full-scale run using seed `20261022` and scale `1.0`, with the requested baseline counts: 200 requisitions, 5,000 candidates, 8,000 applications and 2,000 baseline interviews. It also records 2,003 physical interview rows after labelled exception/reschedule records, 6,000 scorecards, 24,000 scorecard items and seven ground-truth labels.

That validation report records zero configured unlabelled integrity failures and identical SHA-256 manifests for 35 generated CSV, JSON, SQL and metadata files across two full-scale runs. It lists the unit-test command:

```bash
python -m unittest discover -s tests -v
```

### Assistant-side verification run — 31 October 2026

I retrieved the source and data archives from the YottaFlex Library folder and verified their Git object IDs against the files in the public repository. The five tested source files (src/generator.py, src/workflow.py, src/validate.py, tests/test_workflow.py and scripts/reproducibility_check.py) matched the corresponding blobs on main. The full data-export ZIP also matched the repository artifact blob.

The source archive was extracted to `/mnt/data/yottaflex-verify/source/yottaflex-recruitment`; the full-volume export archive was extracted to `/mnt/data/yottaflex-verify/data/yottaflex-full-data-exports`. Git blob IDs for each tested source file matched the files on GitHub `main`, and the export ZIP matched the committed GitHub artifact. The following commands were executed in the assistant's verification environment from the source directory:

```bash
python -m unittest discover -s tests -v
python -m src.validate /mnt/data/yottaflex-verify/data/yottaflex-full-data-exports/recruitment.db
python scripts/reproducibility_check.py --seed 20261022 --scale 0.02
```

Results:
- **Unit tests:** 6 passed.
- **Full-volume database validator:** pass: true; 7 ground-truth labels; zero reported primary-key duplicates, foreign-key violations, invalid date ranges, unlabelled stage-gate failures, unlabelled scheduling overlaps, offer-band violations or other configured unlabelled integrity failures.
- **Reproducibility helper at scale 0.02:** all 35 CSV, JSON, SQL and metadata outputs matched across the two generated runs.

This assistant-side run did **not** repeat the full-scale two-run reproducibility comparison; the full-scale comparison remains the previously recorded result in docs/VALIDATION_RESULTS.md. It also did not locally test the dashboard routes. Render logs from the deployment recorded successful HTTP 200 responses for /, /applications, /requisitions and /anomalies.

These are AI/assistant-run verification results, not tests personally executed by the candidate. The candidate's earlier confirmation that no personal test execution is being claimed remains unchanged.

## Data provenance and privacy

All candidate and employee records included in the project are synthetic. The project record states that no real candidate personal data or external candidate dataset was used. The ground-truth labels identify deliberately injected test cases and should not be treated as operational model input features.

## Known limitations

- The hosted Flask dashboard is read-only.
- It does not implement authentication, role-based access control, recruiter/manager permissions or create/update workflows.
- It is a synthetic-data workflow reference implementation, not a production ATS.
- Synthetic skill and score data must not be used to rank real people.
- Any further gaps discovered during the candidate's own review must be added here before submission.

## Final candidate confirmation required

This file now records the AI assistance and project evidence available from the repository and conversation context, plus the candidate's confirmation that no personal file review, independent code changes or personal test execution are being claimed. The candidate has confirmed that ChatGPT was the only AI tool used. The exact full ChatGPT prompt history still requires reconciliation because the complete original YottaFlex transcript is not available in the accessible file record. The candidate should not send the one-time final submission until they have reconciled all AI tools/sessions and completed the prompt record, and are prepared to understand and explain the submitted implementation.
