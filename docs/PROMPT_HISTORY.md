# AI prompt history

**Project:** YottaFlex recruitment workflow and synthetic-data generator  
**Last updated:** 31 October 2026  
**Status:** Known prompt record; **not certified complete**

The YottaFlex FAQ requests the prompts submitted to every AI tool. This file preserves the assignment/build prompt text and the user messages visible in the project-publication conversation. It does not provide access to every message in older conversations or to sessions in other AI products. Do not describe this log as exhaustive until you compare it against the original chats and every AI tool you used.

## AI tools and connected services identified

- **ChatGPT (GPT-6):** extensive project planning, implementation, debugging, documentation and submission-preparation assistance.
- **GitHub connector:** repository inspection and file publication/updates.
- **Render connector:** dashboard deployment.

Other AI tools/models are not confirmed by the available record. Add their exact prompts and model/tool names below if used. Do not write “None” unless you have checked.

## ChatGPT — GPT-6 — 30 October 2026

### Prompt 1 — assignment/build specification

The following is the assignment/build specification preserved in the project record. Markdown/line wrapping has been normalized; the wording is retained as recorded.

> ## Problem statement
>
> Read it carefully. Your build should cover every point below.
>
> Business Context / Problem Track requisitions, candidate stages, structured evaluation, interviewer calendars and offer approvals. Objective and Scope Build a working solution for this end-to-end workflow: Track requisitions, candidate stages, structured evaluation, interviewer calendars and offer approvals. The solution should expose key decisions and exceptions, preserve traceability, and produce measurable outputs. Medium complexity means multiple related entities, conditional rules, at least one exception path and meaningful evaluation metrics. Primary Actors / Systems Employee/candidate, manager, HR partner, IT/operations partner and system administrator
>
> Business Workflow and Rules
> 1. Generate/reference master data first: Requisition, HiringManager, Candidate, Application, SkillRequirement.
> 2. Generate dependent transaction/event records using valid parent IDs.
> 3. Apply business logic: Create approved requisitions and role criteria; generate synthetic candidate profiles and applications; define stage transition rules; generate interviewer calendars; schedule panels without conflicts; collect rubric-based scorecards; create offers within approved compensation bands.
> 4. Persist state changes as explicit records/events where relevant; do not overwrite history.
> 5. Generate outcomes and ground-truth labels from documented rules, not independent random assignment.
>
> Entities and Relationships
> Core entities: Requisition, HiringManager, Candidate, Application, SkillRequirement, InterviewPanel, Availability, Interview, Scorecard, Offer, Approval. Define a primary key for every entity and foreign keys for every relationship. Document cardinality (1:1, 1:N, N:M), optional relationships, effective dates and lifecycle states. Use bridge tables for many-to-many relationships; retain event history for state changes; validate all joins. For deliberate anomaly cases, keep an issue_type/ground_truth label rather than silently corrupting unrelated rows.
>
> ID / Nomenclature Conventions
> REQ-2026-000001; CAND-000001; APP-<candidate-id>-<req-id>; INT-2026-000001; SCORE-<interview-id>-<reviewer-id>; OFF-2026-000001. Keep counters zero-padded, IDs immutable, and referenced IDs exactly consistent across files.
>
> Synthetic Data Generation Instructions (Granular)
> Step 1 — Write a data dictionary for: Requisition, HiringManager, Candidate, Application, SkillRequirement, InterviewPanel, Availability, Interview, Scorecard, Offer, Approval. For each field specify type, required/optional, allowed values, units, uniqueness and validation rule.
> Step 2 — Create parent/master tables first, then child and event tables. Apply this domain-specific generation logic: Create approved requisitions and role criteria; generate synthetic candidate profiles and applications; define stage transition rules; generate interviewer calendars; schedule panels without conflicts; collect rubric-based scorecards; create offers within approved compensation bands.
> Step 3 — Apply deterministic IDs and naming: REQ-2026-000001; CAND-000001; APP-<candidate-id>-<req-id>; INT-2026-000001; SCORE-<interview-id>-<reviewer-id>; OFF-2026-000001. Keep counters zero-padded, IDs immutable, and referenced IDs exactly consistent across files.
> Step 4 — Generate the baseline volume: Generate 200 requisitions, 5,000 candidates, 8,000 applications and 2,000 interviews. Include withdrawals, rescheduling, conflicting interviewers and incomplete scorecards. Use a fixed seed (e.g. 20261022) and parameterize scale so starter and full datasets use the same generator.
> Step 5 — Generate valid baseline records first, then inject labelled edge cases: Candidate moves forward without required review; interviewer double-booked; offer exceeds band; withdrawn candidate remains scheduled; evaluation includes irrelevant criteria.
> Step 6 — Calculate derived values (totals, balances, scores, statuses and dates) from source records rather than generating them independently.
> Step 7 — Produce a separate ground_truth.csv/json for known anomalies, expected decisions or labels; never leak it into input features.
> Step 8 — Run validation: primary-key uniqueness, foreign-key integrity, allowed enums, date ordering, arithmetic reconciliation, lifecycle transitions and duplicate checks.
> Step 9 — Export CSV/JSON/SQL seed data plus README, schema/data dictionary, generator command, fixed seed, source manifest and validation summary.
> Step 10 — Regenerate twice with the same seed and compare row counts/checksums to demonstrate reproducibility.
>
> Suggested Volume and Coverage Generate 200 requisitions, 5,000 candidates, 8,000 applications and 2,000 interviews. Include withdrawals, rescheduling, conflicting interviewers and incomplete scorecards.
>
> Required Edge Cases / Negative Scenarios Candidate moves forward without required review; interviewer double-booked; offer exceeds band; withdrawn candidate remains scheduled; evaluation includes irrelevant criteria.
>
> Validation Rules / Acceptance Criteria Scheduling conflicts are prevented; stage gates are enforced; scorecards are structured; offer approvals and history are auditable.
>
> Evaluation Focus for Generated Data Review: (a) realistic distributions and meaningful variation; (b) consistent IDs and valid joins; (c) dependency/lifecycle consistency across entities; (d) correct derived values and reconciliation; (e) normal, boundary, failure and exception coverage; (f) separate ground truth; (g) fixed-seed reproducibility, documentation and lawful provenance.
>
> Public Data Guidance / Lawful Use External data is optional. If used, record source URL, dataset/version, retrieval date, license/terms, attribution, transformations and fields discarded. Use only data you are legally permitted to access and redistribute; do not bypass access controls or collect confidential/personal information. If licensing or suitability is unclear, use synthetic data and cite public reference data only for schema inspiration.
>
> **Before you submit, make sure you have**
> - Pushed your code to a public GitHub repository
> - Added a README explaining how to run it
> - Included any tests the problem asks for

### Prompt 2 — assignment reference documents

The candidate supplied the following source documents in the project conversation for review:

- `YottaFlex AI Candidate Project Submission Guidelines.pdf`
- `YottaFlex AI Candidate Project-FAQ.pdf`

These are attachments/context supplied to ChatGPT, not separately typed prompts.

### Prompt 3 — GitHub connector invocation

`[@GitHub](plugin://github@openai-curated-remote)`

The connector was invoked to use the connected GitHub capability for the project.

## Follow-up prompts — publication, deployment and submission-preparation conversation — 31 October 2026

The following exact user messages are visible in the project-publication conversation. Connector invocations are recorded as invocations rather than translated into natural-language instructions.

1. `[$github](app://connector_76869538009648d5b282a4bb21c3d157)`
2. `unable to download zip packages`
3. `unable to find or open data exports`
4. `unable to download`
5. `[$github](app://connector_76869538009648d5b282a4bb21c3d157)`
6. `okay`
7. `zip not found`
8. `give the full code`
9. `[$github](app://connector_76869538009648d5b282a4bb21c3d157) run`
10. `i wan to see the output and live demo`
11. `so its all set to submit`

The conversation also included the following one-time submission form text, supplied by the candidate:

> Submit your work
>
> You can submit once, so check everything before you do.
>
> GitHub repository URL*
>
> The repository must be public so we can review it.
>
> Your submission is final once sent.

The latest follow-up request concerning these disclosure files was:

12. `finish them`

## Earlier-session prompts not fully recoverable from this record

An account-level conversation summary exposes a fragment from an earlier conversation:

- `make a complete app using this information using all the` — visible fragment only; the original message is truncated in the available summary.
- `yeah do it` — visible in that same summarized conversation.

These fragments are not a substitute for the original message history and are not represented as a complete or verbatim list. Retrieve the full earlier conversation and add every relevant user prompt and AI-tool invocation, including any prompt embedded in an attachment or sent to another AI service.

## Other AI tools / sessions — candidate must reconcile

| Date/time + timezone | Tool and exact model | Exact prompt(s) | Work/files affected |
|---|---|---|---|
| [Add each additional AI session, or write “None” only after verifying.] | | | |

## Completeness and submission note

This is a consolidated record of the prompt text and message fragments presently available to the project record. **It is not an exhaustive prompt history.** The candidate must compare it with the complete earlier ChatGPT conversation(s), inspect any prompts supplied as text/file attachments, and review every other AI tool/session used. Add the missing prompts verbatim and preserve the exact tool/model names. Do not claim the history is complete until that reconciliation is finished.
