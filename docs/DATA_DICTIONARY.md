# Data dictionary

Conventions: `TEXT` IDs are immutable primary keys; timestamps use ISO-8601 UTC; date-only fields use `YYYY-MM-DD`; money is integer INR per annum unless stated otherwise. Synthetic email addresses use the reserved `example.test` domain. `required` means NOT NULL. The generator applies the listed domain rules and SQLite applies PK/FK/check/unique constraints.

## HiringManager

| Field | Type | Req? | Allowed values / units | Unique | Validation |
|---|---|---:|---|---:|---|
| manager_id | TEXT | Yes | `HM-0001`... | PK | Immutable manager identifier |
| full_name | TEXT | Yes | Synthetic display name | No | Non-empty |
| email | TEXT | Yes | `managerNNNNNN@example.test` | Yes | Unique synthetic email |
| department | TEXT | Yes | Engineering, Data, Product, Operations, IT | No | Controlled list |
| created_at | TEXT | Yes | ISO-8601 | No | Valid timestamp |

## Requisition

| Field | Type | Req? | Allowed values / units | Unique | Validation |
|---|---|---:|---|---:|---|
| req_id | TEXT | Yes | `REQ-2026-000001` | PK | Immutable; counter zero-padded |
| manager_id | TEXT | Yes | HiringManager ID | No | FK to HiringManager |
| title | TEXT | Yes | Role title | No | Non-empty |
| department | TEXT | Yes | Controlled department | No | Non-empty |
| location | TEXT | Yes | Hyderabad, Bengaluru, Pune, Remote, Chennai | No | Controlled list |
| employment_type | TEXT | Yes | FULL_TIME, CONTRACT, INTERN | No | Enum |
| status | TEXT | Yes | APPROVED, OPEN, ON_HOLD, CLOSED, CANCELLED | No | Enum; generated baseline APPROVED |
| openings | INTEGER | Yes | Positions | No | > 0 |
| min_salary / max_salary | INTEGER | Yes | INR/year | No | min >= 0; max >= min |
| currency | TEXT | Yes | INR | No | ISO-like currency code; currently INR only |
| opened_on / closes_on | TEXT | Yes | Date | No | closes_on >= opened_on |
| created_at | TEXT | Yes | ISO-8601 timestamp | No | Valid timestamp |

## Candidate

| Field | Type | Req? | Allowed values / units | Unique | Validation |
|---|---|---:|---|---:|---|
| candidate_id | TEXT | Yes | `CAND-000001` | PK | Immutable zero-padded ID |
| full_name | TEXT | Yes | Synthetic name | No | Non-empty |
| email | TEXT | Yes | `candidateNNNNNN@example.test` | Yes | Unique |
| experience_years | REAL | Yes | Years | No | >= 0 |
| location | TEXT | Yes | Controlled location | No | Non-empty |
| education | TEXT | Yes | B.Tech, B.E., MCA, M.Sc, B.Sc, Diploma | No | Controlled list |
| profile_created_at | TEXT | Yes | Date | No | ISO date |

## Application

| Field | Type | Req? | Allowed values / units | Unique | Validation |
|---|---|---:|---|---:|---|
| application_id | TEXT | Yes | `APP-<candidate-id>-<req-id>` | PK | Exactly embeds parent IDs |
| candidate_id | TEXT | Yes | Candidate ID | No | FK Candidate |
| req_id | TEXT | Yes | Requisition ID | No | FK Requisition |
| current_stage | TEXT | Yes | APPLIED, SCREENING, TECHNICAL, PANEL, OFFER, HIRED, WITHDRAWN, REJECTED | No | Must obey transition lifecycle |
| applied_on / updated_at | TEXT | Yes | Date / timestamp | No | Updated >= applied date |
| source | TEXT | Yes | CAREERS_SITE, REFERRAL, LINKEDIN, JOB_BOARD | No | Enum |
| issue_type | TEXT | No | Exception code | No | Set only for explicit anomaly cases |
| Pair constraint | — | — | candidate_id + req_id | Unique | One application per candidate/requisition pair |

## SkillRequirement

| Field | Type | Req? | Allowed values / units | Unique | Validation |
|---|---|---:|---|---:|---|
| skill_requirement_id | TEXT | Yes | `SR-000001-01` | PK | Immutable generated ID |
| req_id | TEXT | Yes | Requisition ID | No | FK Requisition |
| skill_name | TEXT | Yes | Canonical role skill | No | Unique per req + skill |
| required_level | INTEGER | Yes | 1–5 proficiency | No | Inclusive bounds |
| is_mandatory | INTEGER | Yes | 0 or 1 | No | Boolean encoding |
| weight | REAL | Yes | Relative weight | No | > 0 |

## CandidateSkill (supporting bridge)

| Field | Type | Req? | Allowed values / units | Unique | Validation |
|---|---|---:|---|---:|---|
| candidate_id | TEXT | Yes | Candidate ID | Composite PK | FK Candidate |
| skill_name | TEXT | Yes | Canonical skill | Composite PK | One per candidate/skill |
| proficiency | INTEGER | Yes | 1–5 | No | Inclusive bounds |

## InterviewPanel

| Field | Type | Req? | Allowed values / units | Unique | Validation |
|---|---|---:|---|---:|---|
| panel_id | TEXT | Yes | `PANEL-000001` | PK | Immutable |
| req_id | TEXT | Yes | Requisition ID | No | FK Requisition |
| panel_name | TEXT | Yes | Display name | No | Non-empty |
| panel_type | TEXT | Yes | TECHNICAL, CULTURE, FINAL | No | Enum |

## PanelInterviewer (bridge)

| Field | Type | Req? | Allowed values / units | Unique | Validation |
|---|---|---:|---|---:|---|
| panel_id | TEXT | Yes | Panel ID | Composite PK | FK Panel |
| interviewer_id | TEXT | Yes | HiringManager ID | Composite PK | FK HiringManager |
| role_on_panel | TEXT | Yes | TECH_LEAD, PEER, HR, IT_OPERATIONS | No | Controlled role |

## Availability

| Field | Type | Req? | Allowed values / units | Unique | Validation |
|---|---|---:|---|---:|---|
| availability_id | TEXT | Yes | `AVL-...` | PK | Immutable generated ID |
| interviewer_id | TEXT | Yes | HiringManager ID | No | FK HiringManager |
| starts_at / ends_at | TEXT | Yes | ISO-8601 timestamps | No | ends_at > starts_at |
| status | TEXT | Yes | AVAILABLE, BLOCKED | No | Enum |

## Interview

| Field | Type | Req? | Allowed values / units | Unique | Validation |
|---|---|---:|---|---:|---|
| interview_id | TEXT | Yes | `INT-2026-000001` | PK | Immutable; anomaly suffixes only for labelled test cases |
| application_id | TEXT | Yes | Application ID | No | FK Application |
| panel_id | TEXT | Yes | Panel ID | No | FK InterviewPanel |
| starts_at / ends_at | TEXT | Yes | ISO-8601 timestamps | No | ends_at > starts_at; no interviewer overlap in normal records |
| interview_type | TEXT | Yes | TECHNICAL_PANEL | No | Current generator enum |
| status | TEXT | Yes | SCHEDULED, COMPLETED, CANCELLED, RESCHEDULED | No | Enum |
| rescheduled_from | TEXT | No | Interview ID | No | Self-FK to original interview |
| issue_type | TEXT | No | Exception code | No | Explicit anomaly label only |

## Scorecard

| Field | Type | Req? | Allowed values / units | Unique | Validation |
|---|---|---:|---|---:|---|
| scorecard_id | TEXT | Yes | `SCORE-<interview-id>-<reviewer-id>` | PK | Exactly follows requested nomenclature |
| interview_id | TEXT | Yes | Interview ID | No | FK Interview |
| reviewer_id | TEXT | Yes | HiringManager ID | No | FK HiringManager |
| overall_score | REAL | No | Mean score, 1–5 | No | Derived from submitted relevant rubric items |
| status | TEXT | Yes | DRAFT, SUBMITTED | No | DRAFT cannot be used as a completed evaluation |
| comments | TEXT | Yes | Text | No | Non-empty reviewer summary |
| submitted_at | TEXT | No | ISO timestamp | No | Required for SUBMITTED records |
| issue_type | TEXT | No | Exception code | No | E.g. INCOMPLETE_SCORECARD |
| Unique pair | — | — | interview_id + reviewer_id | Unique | One scorecard per reviewer/interview |

## ScorecardItem (rubric detail)

| Field | Type | Req? | Allowed values / units | Unique | Validation |
|---|---|---:|---|---:|---|
| scorecard_item_id | TEXT | Yes | `SCITEM-...` | PK | Immutable item ID |
| scorecard_id | TEXT | Yes | Scorecard ID | No | FK Scorecard |
| criterion | TEXT | Yes | Problem Solving, Technical Depth, Communication, Role Knowledge; labelled anomaly criteria separately | No | Must be role-relevant to contribute |
| score | INTEGER | Yes | 1–5 | No | Inclusive bounds |
| comments | TEXT | Yes | Text | No | Non-empty assessment notes |
| is_relevant | INTEGER | Yes | 0 or 1 | No | Irrelevant criteria excluded from metrics |
| issue_type | TEXT | No | Exception code | No | E.g. IRRELEVANT_EVALUATION_CRITERION; matched to ground truth |
| Unique pair | — | — | scorecard_id + criterion | Unique | No duplicate rubric item per scorecard |

## Offer

| Field | Type | Req? | Allowed values / units | Unique | Validation |
|---|---|---:|---|---:|---|
| offer_id | TEXT | Yes | `OFF-2026-000001` | PK | Immutable; anomaly-only IDs labelled |
| application_id | TEXT | Yes | Application ID | No | FK Application |
| annual_salary | INTEGER | Yes | INR/year | No | > 0 and within linked requisition band for approval |
| currency | TEXT | Yes | INR | No | Current currency |
| status | TEXT | Yes | DRAFT, PENDING_APPROVAL, APPROVED, REJECTED, ACCEPTED, DECLINED | No | Enum |
| issued_on / expires_on | TEXT | Yes | Date | No | expires_on >= issued_on |
| issue_type | TEXT | No | Exception code | No | Out-of-band exception explicitly marked |

## Approval

| Field | Type | Req? | Allowed values / units | Unique | Validation |
|---|---|---:|---|---:|---|
| approval_id | TEXT | Yes | `APR-000001` | PK | Immutable |
| offer_id | TEXT | Yes | Offer ID | No | FK Offer |
| approver_id | TEXT | Yes | HiringManager ID | No | FK HiringManager |
| decision | TEXT | Yes | APPROVED, REJECTED, PENDING | No | Out-of-band offers cannot be approved |
| decided_at | TEXT | Yes | ISO timestamp | No | Valid timestamp |
| comments | TEXT | Yes | Text | No | Audit rationale |

## ApplicationEvent (append-only history)

| Field | Type | Req? | Allowed values / units | Unique | Validation |
|---|---|---:|---|---:|---|
| event_id | TEXT | Yes | `EVT-...` | PK | Immutable event ID |
| application_id | TEXT | Yes | Application ID | No | FK Application |
| from_stage | TEXT | No | Lifecycle stage | No | Null only for initial submission |
| to_stage | TEXT | Yes | Lifecycle stage | No | Enum |
| event_at | TEXT | Yes | ISO timestamp | No | Chronological event history |
| actor_id | TEXT | Yes | User ID or SYSTEM | No | Actor recorded; user ID resolution is a production extension |
| reason | TEXT | Yes | Text | No | Decision rationale |
| gate_passed | INTEGER | Yes | 0 or 1 | No | 0 must be labelled as exception |
| issue_type | TEXT | No | Exception code | No | Match separate ground truth for injected cases |

## GroundTruth (evaluation only)

| Field | Type | Req? | Allowed values / units | Unique | Validation |
|---|---|---:|---|---:|---|
| anomaly_id | TEXT | Yes | `GT-001`... | PK | Unique label ID |
| entity_type | TEXT | Yes | Table/entity name | No | Identifies the labelled record type |
| entity_id | TEXT | Yes | Operational record ID | No | Exact join target; intentionally kept outside input exports |
| issue_type | TEXT | Yes | Named anomaly class | No | Documented label |
| expected_decision | TEXT | Yes | Rule response | No | Expected action such as block/reschedule/exclude/escalate |
| description | TEXT | Yes | Text | No | Explanation of ground-truth rule |

## Cardinality summary

- HiringManager 1:N Requisition; HiringManager 1:N Availability; HiringManager N:M InterviewPanel via PanelInterviewer; HiringManager 1:N Scorecard as reviewer; HiringManager 1:N Approval as approver.
- Requisition 1:N Application; Requisition 1:N SkillRequirement; Requisition 1:N InterviewPanel.
- Candidate 1:N Application; Candidate N:M skill via CandidateSkill.
- Application 1:N ApplicationEvent; Application 1:N Interview (reschedules retained as separate interview records); Application 1:N Offer (supports revised offers).
- InterviewPanel 1:N Interview; Interview 1:N Scorecard; Scorecard 1:N ScorecardItem; Interview 0..1 -> 1 original Interview via rescheduled_from.
- Offer 1:N Approval (approval history); GroundTruth 1:N labels a record in a separate evaluation dataset. Optional links include `rescheduled_from`, `from_stage`, `submitted_at`, `issue_type`.

Effective dating uses requisition `opened_on`/`closes_on`, availability intervals, and event/interview timestamps. This compact assignment schema does not add bitemporal version columns to every master record; production-grade effective-dated history is a stated extension.
