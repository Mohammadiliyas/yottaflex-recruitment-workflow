# YottaFlex Recruitment Workflow

A deterministic synthetic-data recruitment workflow and validation project for the YottaFlex AI candidate challenge.

## Project contents

- Deterministic recruitment data generator (seed: 20261022)
- Workflow and data validation logic
- Reproducibility checks and summary scripts
- Unit tests
- Design notes, data dictionary, validation results, AI disclosure and prompt history
- CSV and JSON export files, SQL dump and SQLite database in the full data package

## Full-volume targets

| Entity | Target |
|---|---:|
| Requisitions | 200 |
| Candidates | 5,000 |
| Applications | 8,000 |
| Baseline interviews | 2,000 |

Generated outputs include 2,003 interview rows (2,000 baseline plus labelled exception/reschedule rows), 6,000 scorecards, 24,000 rubric items, and 219 offers with approvals.

## Source package layout

```text
src/
  generator.py
  validate.py
  workflow.py
scripts/
  reproducibility_check.py
  summarize.py
tests/
  test_workflow.py
docs/
  AI_DISCLOSURE.md
  DATA_DICTIONARY.md
  DESIGN.md
  PROMPT_HISTORY.md
  VALIDATION_RESULTS.md
requirements.txt
```

## Setup

Python 3.10+ is recommended.

```bash
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
python -m unittest discover -s tests -v
python -m src.generator --help
```

See the source files and documentation for generation, validation, export and reproducibility commands.

## Data and AI disclosure

All generated candidate and hiring data is synthetic. No external candidate dataset or real personal information is used. The submission documentation includes a data dictionary, design rationale, validation results, prompt history and AI-use disclosure. Review these documents and ensure the prompt history reflects all AI prompts actually used before final submission.

## Integrity note

The complete generated data exports (CSV, JSON, SQL and SQLite) are not yet committed to this repository. The full data package must be added separately or regenerated locally from the source. Review the implementation, rerun tests and generator, and be prepared to explain the design decisions, assumptions and limitations.
