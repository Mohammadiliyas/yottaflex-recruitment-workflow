# AI assistance disclosure

## AI tools and services used in this project

- **ChatGPT (GPT-6):** used extensively to plan and draft the project architecture, Python/SQLite schema, deterministic synthetic-data generator, workflow rules, validation code, unit tests, scripts, documentation and debugging changes. ChatGPT also helped inspect the generated database and validate the packaged output.
- **ChatGPT GitHub connector:** used to inspect and update the public repository, commit the source and data archive, and update project documentation.
- **Render connector:** used to create and deploy the read-only Flask dashboard from the GitHub repository.
- **Other AI tools used by the candidate:** the candidate must list every additional tool/model used, or state “None” only if that is accurate.

## AI-assisted work

The initial implementation and most of the code/documentation were AI-drafted. This includes src/generator.py, src/workflow.py, src/validate.py, tests/test_workflow.py, scripts, README, data dictionary, design notes and prompt-history content. AI assistance was also used for debugging date, scheduling, data-volume, scorecard-normalization and validation issues.

The read-only Flask web dashboard in app.py, its dependency declarations in requirements.txt, and the deployment configuration were added with AI assistance after the original data-generation project. The dashboard displays synthetic records; it is not a production ATS and does not implement authentication, role-based access control or data mutation.

All included candidate and employee records are synthetic. No real candidate personal data or external candidate dataset is used.

## Repository and deployment status

- Public repository: https://github.com/Mohammadiliyas/yottaflex-recruitment-workflow
- Source code, tests, documentation and the full synthetic export archive are committed to the main branch.
- Read-only browser demo: https://yottaflex-recruitment-demo.onrender.com
- Render reported a successful deployment. The homepage returned HTTP 200 in the service logs.

## Automated verification performed

The following checks were performed in the build environment for the packaged full-volume database:

- Full-volume data contains 200 requisitions, 5,000 candidates, 8,000 applications and 2,000 baseline interviews. The physical interview table contains 2,003 rows after labelled exception and reschedule records are added.
- The six unit tests were rerun and passed.
- The validator was rerun against the SQLite database extracted from the committed data archive. It returned pass: true, zero foreign-key violations, zero duplicate primary keys, zero configured unlabelled integrity failures, and seven ground-truth labels.
- The dashboard's overview metrics and SQL queries for the application, requisition and anomaly pages were checked against the packaged SQLite schema/data.
- The existing docs/VALIDATION_RESULTS.md records the earlier full-scale two-run reproducibility comparison across 35 generated CSV, JSON, SQL and metadata files. That full two-run comparison was not rerun as part of this final dashboard deployment check.

These are automated checks, not proof of personal candidate review or ownership.

## Candidate review and completion required before submission

This AI disclosure cannot claim that the candidate has personally read, understood, modified or manually validated the code. The candidate must complete the following accurately before submitting:

| Required disclosure | Candidate must complete |
|---|---|
| Files and functions personally reviewed | [List exact paths and what you understood] |
| Personal code changes | [Describe only changes you personally made] |
| Manual tests personally performed | [List commands/scenarios actually run by you and the results] |
| Other AI tools and sessions | [List all tools/models and prompts, or state “None” only if true] |
| Prompt-history completeness | [Compare PROMPT_HISTORY.md with all relevant ChatGPT conversations and other AI sessions; add every missing prompt] |
| Known gaps accepted for submission | [List remaining issues honestly] |

Do not claim personal review, manual execution, authorship, or an exhaustive prompt history unless those statements are true. The prompt-history file currently contains the original assignment prompt and a partial record of later project interactions; it is not guaranteed to include every prompt from prior chats or other AI tools.

YottaFlex's FAQ requires individual ownership and disclosure of all AI prompts. Review the actual assignment instructions and deadline, ensure all required prompts are recorded, personally understand the implementation, and disclose any incomplete requirements.
