# YottaFlex Recruitment Workflow

A deterministic, synthetic-data recruitment workflow and validation project for the YottaFlex AI candidate challenge.

## Status

This repository is the public submission home. The complete source package is available from the project owner and should be uploaded before final submission. Do not treat this README-only initialization as a complete code submission.

## Project scope

- Requisition, hiring manager, candidate, application and skill master data
- Interview panels, interviewer availability, interviews and scorecards
- Offers, approvals and application event history
- Deterministic synthetic data generation (seed: 20261022)
- Separate ground-truth labels for intentional edge cases
- Validation of IDs, foreign keys, lifecycle rules, dates, scheduling, compensation and reproducibility

## Full-volume targets

| Entity | Target |
|---|---:|
| Requisitions | 200 |
| Candidates | 5,000 |
| Applications | 8,000 |
| Baseline interviews | 2,000 |

The generated export includes 2,003 interview rows (2,000 baseline plus labelled exception/reschedule rows), 6,000 scorecards, 24,000 rubric items, and 219 offers with approvals.

## Local setup

The complete source package contains the executable code and detailed README. After extracting it:

```bash
cd yottaflex-recruitment
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
python -m src.generator --help
python -m unittest discover -s tests -v
```

Consult the packaged README for exact generation, validation, export and reproducibility commands.

## Data provenance and AI disclosure

All generated candidate and hiring data is synthetic. No external candidate dataset or personal information is used. The full submission package includes the data dictionary, design rationale, validation results, prompt history and AI-use disclosure. Review and update the prompt history to include every prompt submitted to every AI tool before submission.

## Important

The challenge requires individual understanding and ownership. Review the source, run the tests and generator yourself, and be prepared to explain design decisions, assumptions and limitations.
