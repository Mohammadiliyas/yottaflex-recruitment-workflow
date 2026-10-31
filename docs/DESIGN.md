# Design notes

## Workflow

1. Create manager masters.
2. Create approved requisitions and their weighted skill requirements; create a panel per requisition and interviewer membership.
3. Create candidate profiles and synthetic candidate skills.
4. Create applications with deterministic candidate/requisition IDs. Fit is derived from weighted candidate skill proficiency against mandatory role criteria. Stage outcomes use explicit thresholds on that fit ratio and candidate experience; they are not independently random labels.
5. Create interviewer availability windows, then schedule panels using overlap and availability checks.
6. Record one Scorecard per reviewer/interview using the requested `SCORE-<interview-id>-<reviewer-id>` ID, with normalized ScorecardItem rubric rows. Aggregations exclude incomplete scorecards and explicitly irrelevant criteria.
7. Generate in-band offers only for applications with interview evidence at OFFER stage; persist approval decisions.
8. Append application events and preserve original interviews when rescheduled.
9. Inject named edge cases after the clean baseline; publish ground truth separately.

## Application lifecycle

`APPLIED -> SCREENING -> TECHNICAL -> PANEL -> OFFER -> HIRED`

At any non-terminal stage, `WITHDRAWN` or `REJECTED` may be reached. Forward moves are sequential. A required review is intended to be complete before advancing into technical/panel/offer/hired stages. **Implementation caveat:** `transition_application()` currently trusts its caller-supplied `required_review_complete` Boolean and does not independently inspect persisted review evidence. `WITHDRAWN`, `REJECTED` and `HIRED` are terminal.

## Scheduling policy

Each panel has three synthetic interviewers. A proposed time interval must fit all panel members' availability and must not overlap an existing scheduled/completed interview involving any of those interviewers. Different panels may run concurrently when they have no interviewer in common. Intervals are half-open for comparison (`start < other_end` and `end > other_start`); adjacent sessions are allowed. Deliberate anomaly rows carry an issue label and are excluded from normal-operation expectations. **Implementation caveat:** `schedule_interview()` does not currently verify that the selected panel's requisition matches the application requisition; the full-data validator checks generated records, but the runtime helper should add this check.

## Offer policy

Offer salary must satisfy `requisition.min_salary <= offer.annual_salary <= requisition.max_salary`. An approval cannot approve an out-of-band amount. Such offers are retained only as labelled exception records to exercise the exception path. **Implementation caveat:** `approve_offer()` currently marks the offer `APPROVED` after one approved decision and does not enforce the two distinct role-based approvals described in the intended policy.

## Metrics

- Application funnel by current stage.
- Completed interviews / total applications.
- Mean submitted relevant score (`is_relevant=1`).
- Offer approval rate (`APPROVED` or `ACCEPTED` / all offers).
- Known exception count by issue type.

These are operational diagnostics over synthetic data, not candidate quality claims.

## Traceability and ground truth

`application_event` records source and target stage, timestamp, actor, reason, gate result and issue type. Interview rescheduling retains the original interview and sets `rescheduled_from` on the new one. `ground_truth` is a separate table in SQLite and separate CSV/JSON files for testing only; exclude it from any model input dataset.


## Actor responsibilities and boundaries

- **Employee/candidate:** represented by Candidate and Application; may enter the pipeline or withdraw. The synthetic generator does not model candidate login credentials or a self-service portal. Weighted mandatory-skill fit below 0.34 remains APPLIED, 0.34–0.60 enters SCREENING, 0.60–0.90 enters TECHNICAL, and high fit progresses to TECHNICAL/PANEL/OFFER according to experience (under 3 years: TECHNICAL; 3–under 7: PANEL; 7 or more: OFFER).
- **Hiring manager:** represented by HiringManager and the requisition owner; also supplies panel interviewers and offer approvers.
- **HR partner:** may be assigned to panels through `PanelInterviewer.role_on_panel = HR` and participates in structured evaluation/coordination.
- **IT/operations partner:** may be assigned to operational panels through `role_on_panel = IT_OPERATIONS`; the current model does not create a separate IT ticketing workflow.
- **System administrator/system:** generated events use `SYSTEM` as actor where the generator is the actor. A real user/role/permission administration interface is not implemented.

The project demonstrates workflow data and rules rather than a full RBAC product. Do not describe it as a complete production ATS or claim that per-role access controls are implemented.
