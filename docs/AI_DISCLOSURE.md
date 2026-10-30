# AI assistance disclosure

## AI tools used in this build session

- **ChatGPT (GPT-6):** used to draft the project architecture, Python/SQLite schema, deterministic synthetic-data generator, business-rule functions, unit tests, documentation, and debugging changes. It also executed generation, validation, unit-test, and reproducibility commands in the build environment.
- **ChatGPT GitHub connector:** invoked to inspect the connected GitHub account and test repository publication. The connector did not expose a repository-creation action; a write attempt against the planned repository name returned `404 Not Found`. No repository or commit has been created by this session.
- **Other AI tools:** [add every other tool/model you used, or state “None” only if accurate].

## AI-assisted work

The initial implementation and most code/documentation in this repository were AI-drafted. That includes `src/generator.py`, `src/workflow.py`, `src/validate.py`, `tests/test_workflow.py`, scripts, the README, data dictionary, design notes, and prompt-history file. AI assistance was also used to debug date, scheduling, data-volume, scorecard-normalization, and validation issues. The generated records are synthetic and contain no external candidate data.

## Automated verification performed in the build environment

- Full-volume generation with seed `20261022` produced 200 requisitions, 5,000 candidates, 8,000 applications and 2,000 baseline interviews.
- The database validator reported no primary-key duplicates, foreign-key violations, invalid lifecycle transitions, unlabelled interviewer conflicts, invalid offer-band values, broken ground-truth references, or other configured validation failures.
- Six unit tests passed.
- Two independent full-volume runs at scale `1.0` produced identical CSV, JSON, SQL, and metadata outputs across 35 files; baseline counts matched and both validation summaries passed.

## Required candidate review before submission

This build session cannot claim that the candidate has personally read, understood, modified, or manually validated the code. Before submitting, personally review at least the generator, workflow rules, tests, and data dictionary; run the commands in the README on your own machine; inspect the ground-truth anomalies; and replace this section with an accurate account of what you personally reviewed, changed, and verified.

| Required disclosure | Candidate must complete |
|---|---|
| Personally reviewed files and functions | [list exact paths and what you understood] |
| Personal code changes | [describe the changes you personally made] |
| Manual tests and results | [commands and manual scenarios you actually performed] |
| Other AI tools and prompts | [add all tools and prompts; reconcile with PROMPT_HISTORY.md] |
| Known gaps accepted for submission | [list remaining issues honestly] |

Do not claim personal review, manual execution, authorship, or absence of other AI prompts unless those statements are true. YottaFlex's FAQ requires individual ownership and all AI prompts, and allows incomplete requirements only when limitations and next steps are disclosed.
