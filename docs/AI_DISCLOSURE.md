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
| Other AI tools/models | **Not confirmed by the available project record.** The candidate must list every additional tool/model used, or state “None” only after checking all relevant sessions. |

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
- **Other AI tools/models or AI sessions used:** Not answered; this remains unconfirmed and must not be interpreted as “None.”

Do not copy an AI-generated explanation into these fields as evidence of personal understanding. Before a technical walkthrough, the candidate needs to personally study the generator, relational relationships, stage gates, scheduling/conflict logic, rubric scorecards, offer approvals, anomaly labels, validation and dashboard limitations.

## Automated checks and deployment evidence recorded

The repository's `docs/VALIDATION_RESULTS.md` records a full-scale run using seed `20261022` and scale `1.0`, with the requested baseline counts: 200 requisitions, 5,000 candidates, 8,000 applications and 2,000 baseline interviews. It also records 2,003 physical interview rows after labelled exception/reschedule records, 6,000 scorecards, 24,000 scorecard items and seven ground-truth labels.

That validation report records zero configured unlabelled integrity failures and identical SHA-256 manifests for 35 generated CSV, JSON, SQL and metadata files across two full-scale runs. It lists the unit-test command:

```bash
python -m unittest discover -s tests -v
```

The project build record also reports six unit tests passing and a validator pass. These are **recorded project/build results**, not a statement that the candidate personally ran those checks. They were not rerun as part of this documentation update.

The Render deployment was reported live, and service logs recorded successful HTTP 200 responses for the dashboard and its application, requisition and anomaly endpoints. This is deployment evidence, not proof that the app is a production ATS.

## Data provenance and privacy

All candidate and employee records included in the project are synthetic. The project record states that no real candidate personal data or external candidate dataset was used. The ground-truth labels identify deliberately injected test cases and should not be treated as operational model input features.

## Known limitations

- The hosted Flask dashboard is read-only.
- It does not implement authentication, role-based access control, recruiter/manager permissions or create/update workflows.
- It is a synthetic-data workflow reference implementation, not a production ATS.
- Synthetic skill and score data must not be used to rank real people.
- Any further gaps discovered during the candidate's own review must be added here before submission.

## Final candidate confirmation required

This file now records the AI assistance and project evidence available from the repository and conversation context, plus the candidate's confirmation that no personal file review, independent code changes or personal test execution are being claimed. The other-AI-tools question remains unanswered, and the prompt history remains incomplete. The candidate should not send the one-time final submission until they have reconciled all AI tools/sessions and completed the prompt record, and are prepared to understand and explain the submitted implementation.
