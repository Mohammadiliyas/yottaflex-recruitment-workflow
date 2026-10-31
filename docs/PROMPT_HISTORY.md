# AI Prompt and Tool-Use Record

**Project:** YottaFlex Recruitment Workflow and Synthetic Data Generator  
**AI assistant:** ChatGPT (GPT-6)  
**Other AI tools:** None, as confirmed by the candidate on 31 October 2026  
**Last updated:** 31 October 2026  
**Record status:** Consolidated project-specific record; historical completeness not independently certified

## 1. Purpose and scope

This document records the AI instructions and tool interactions used to plan, implement, troubleshoot, publish and demonstrate the YottaFlex recruitment-workflow project. It is intended for reviewer transparency and to support a technical walkthrough.

The record focuses on project-related instructions. Greetings, acknowledgements, personal conversation, learning-quiz answers and submission-form text are not included because they did not instruct the AI to develop or modify the project.

## 2. Tools and services used

| Tool or service | Purpose |
|---|---|
| ChatGPT (GPT-6) | Requirements interpretation, architecture, code generation and refinement, debugging, validation support, documentation and submission preparation |
| GitHub connector | Repository inspection and publication or updating of source code, data artifacts and documentation |
| Render connector | Creation and deployment of the read-only Flask dashboard |

The candidate confirmed that ChatGPT was the only AI tool used. GitHub and Render are recorded as connected services used through ChatGPT, not as separate generative-AI models.

## 3. Primary project brief

### 3.1 Original assignment and implementation requirements

The project brief instructed the AI assistant to create a working recruitment workflow solution covering requisitions, candidate stages, structured evaluations, interviewer calendars and offer approvals. It specified the following requirements:

- Model the core entities: Requisition, HiringManager, Candidate, Application, SkillRequirement, InterviewPanel, Availability, Interview, Scorecard, Offer and Approval.
- Generate master data before dependent records and preserve valid primary-key/foreign-key relationships.
- Use deterministic, immutable IDs and zero-padded identifiers.
- Generate baseline volumes of 200 requisitions, 5,000 candidates, 8,000 applications and 2,000 interviews.
- Generate normal workflow records first, then introduce labelled exception scenarios such as missing review evidence, interviewer conflicts, out-of-band offers, withdrawn candidates remaining scheduled and irrelevant evaluation criteria.
- Derive outcomes and metrics from source records rather than assigning them independently at random.
- Preserve application event history and retain original interview records when rescheduling.
- Export CSV, JSON, SQL and SQLite data with documentation, a data dictionary, source manifest, validation summary and checksums.
- Validate primary-key uniqueness, foreign-key integrity, lifecycle transitions, date ordering, calculations, duplicate records and exception labels.
- Use a fixed random seed and demonstrate reproducibility by regenerating the data and comparing outputs.
- Keep ground-truth anomaly labels separate from operational input data.
- Publish the source code in a public GitHub repository and provide clear setup and test instructions.

The original assignment brief and the candidate's submitted assignment documents are the authoritative sources for the requirements. The detailed entity definitions, volume targets and acceptance criteria are also reflected in the repository's README, data dictionary and design documentation.

### 3.2 Assignment documents supplied to ChatGPT

The candidate supplied these documents as project context:

- `YottaFlex AI Candidate Project Submission Guidelines.pdf`
- `YottaFlex AI Candidate Project-FAQ.pdf`

They were used to interpret the 72-hour submission window, public-repository requirement, AI transparency, prompt-history requirement and individual-work expectations. These were file attachments, not separately typed prompts.

## 4. Project-specific follow-up instructions

The following are the project-related user instructions that can be recovered from the publication and demo conversation. Wording is preserved where the original message is available.

| No. | Recorded instruction | Workstream |
|---:|---|---|
| 1 | `[@GitHub](plugin://github@openai-curated-remote)` | Request to use the connected GitHub capability |
| 2 | `[$github](app://connector_76869538009648d5b282a4bb21c3d157)` | Repository inspection/publication through GitHub |
| 3 | `unable to download zip packages` | Troubleshooting project archive retrieval |
| 4 | `unable to find or open data exports` | Troubleshooting access to generated data exports |
| 5 | `unable to download` | Further archive retrieval troubleshooting |
| 6 | `zip not found` | Troubleshooting missing local archive |
| 7 | `give the full code` | Request for the complete project source |
| 8 | `[$github](app://connector_76869538009648d5b282a4bb21c3d157) run` | GitHub-connected repository operation |
| 9 | `i wan to see the output and live demo` | Request to present project output and deploy a browser-accessible demonstration |
| 10 | `so its all set to submit` | Request for submission-readiness review |

The connector invocations above are retained as recorded. They are not represented as natural-language prompts.

## 5. AI-assisted implementation areas

ChatGPT assistance was extensive and covered the following project components:

| Component | AI-assisted activity |
|---|---|
| `src/generator.py` | SQLite schema, deterministic synthetic-data generation, relationships, exports and generation logic |
| `src/workflow.py` | Stage transitions, interview scheduling, scorecards/metrics and offer/approval rules |
| `src/validate.py` | Data-integrity and labelled-exception validation |
| `tests/test_workflow.py` | Unit-test drafting and refinement |
| `scripts/` | Data summary and reproducibility utilities |
| `docs/` | Design notes, data dictionary, validation results, README and disclosure documentation |
| `app.py` | Read-only Flask dashboard for overview metrics, applications, requisitions and anomalies |
| `requirements.txt` and Render configuration | Dashboard runtime dependencies and deployment support |

AI assistance also supported debugging issues involving dates, scheduling, data volume, scorecard normalization and validation. The candidate should distinguish AI-generated or AI-assisted work from any independent work they personally completed.

## 6. Prompt-capture limitations

This is a consolidated record of the project-specific instructions recoverable from the currently accessible project files and conversation context. It is more focused than a raw chat transcript and excludes non-project exchanges.

The complete original YottaFlex ChatGPT conversation is not available in the accessible file record, so this document **must not be described as a verified verbatim transcript of every prompt**. Before claiming exhaustive prompt history, the candidate should compare this record with the complete original YottaFlex conversation and add any missing project-development or project-operation prompts. The candidate confirmed that no other AI tool was used.

## 7. Ownership and review statement

AI assistance was extensive. This prompt record is not evidence that the candidate independently authored, reviewed or tested the generated code. The separate `docs/AI_DISCLOSURE.md` records the candidate's confirmation that no personal code review, independent code changes or personally executed tests are being claimed, and documents the project's known implementation limitations.

The candidate should be prepared to explain the data model, generator, stage-gate behavior, scheduling logic, scorecards, approval logic, validation approach, dashboard and known gaps in their own words.
