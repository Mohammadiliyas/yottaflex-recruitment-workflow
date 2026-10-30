# AI prompt history

This file records the prompts available from this project-building session. The YottaFlex FAQ asks candidates to include **all prompts submitted to every AI tool**. This log cannot prove what was entered in other tools or previous sessions. Add those verbatim before submission. AI responses are optional under the FAQ.

## ChatGPT — GPT-6 — 30 October 2026

### Prompt 1 — assignment specification (content reproduced; Markdown/line wrapping normalized)

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
>
> [GitHub connector was explicitly invoked in this conversation.]

### Prompt 2 — submission documents supplied as context

Attached the YottaFlex AI Candidate Project Submission Guidelines PDF and Candidate Project FAQ PDF for this task. (Attachments are source material rather than a separately typed natural-language prompt.)

### Prompt 3 — GitHub connector action

`[@GitHub](plugin://github@openai-curated-remote)` — request to use the connected GitHub capability for the project.

## Other AI tools / sessions

| Date/time + timezone | AI tool/model | Exact prompt(s) | Files/code affected | What you personally reviewed or changed |
|---|---|---|---|---|
| [add every other tool/session, or write “None” only if true] | | | | |

Keep original wording wherever possible. If a tool cannot export its prompts, document that limitation and retain a reasonable contemporaneous record as the FAQ permits. Do not state that no other prompts were used unless you can verify it.
