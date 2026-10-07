# Requirements-to-evidence map

| ID | Requirement | Owner | Tasks | Evidence at release |
|---|---|---|---|---|
| C01 | Agriculture market-access theme and named office/workflow | B | P07,P09,P10 | Agreed scope, practitioner notes, description |
| C02 | Own MCP server with at least 3 different tools and useful action | A | I06,I07,I08 | Tool catalogue, real calls, persisted pending draft |
| C03 | Borrowed MCP server and rationale | A | I01,I09 | Upstream source/version/licence, actual trace, README rationale |
| C04 | Open-source orchestration | A | I01,I10 | Dependency lock and actual LangGraph execution |
| C05 | Complete task on open-weights model | A/B | I01,I10,I20 | Model identity/digest, full real run and eval evidence |
| C06 | Logged actions and human gate | A/B | I05,I11,I12,I16,I19 | Tool audit, authenticated reviewer, approval/rejection/bypass/restart checks |
| C07 | New work during official period | Both | P02,I00,R11 | Dated official window evidence and honest Git history |
| C08 | Public runnable OSI-licensed repository | Both | P05,R00,R01,R03,R08 | Licence, source, clean public link, fresh-clone run |
| C09 | One-command setup | A/B | R00,R01,R03 | Actual `make demo` run on stated prerequisites |
| C10 | Public unedited demo under 3 minutes with tools visible | B/A | R05,R06,R08 | Video URL, measured duration and shown run ID |
| C11 | Approximately 300-word description | B/A | R04 | Final text naming theme/institution/workflow |
| C12 | One-page ARCHITECTURE.md | A/B | R04 | Final concise diagram/agent/built-versus-borrowed rationale |
| C13 | EVALS.md: 8+ tasks, outcomes, one unresolved failure and next step | B/A | I17,I18,I20,R04 | Honest committed report and traces |
| C14 | English submission | Both | R04,R08 | Reviewer-confirmed docs/video explanation |
| C15 | Data consent and sources; no forbidden household data | B/A | P08,P09,I02,I19,R02 | Source register/rights, permitted public and labelled synthetic inputs |
| C16 | No unsupported claims or unapproved household action | Both | I11,I12,I19,R08 | Backend invariants and demo/claim review |
| C17 | Deadline and post-deadline freeze | Both | P02,R09,R10,R11 | Cutoff timestamp, receipt, final SHA, no later submitted-repo commits |
| C18 | Explain code and handle live change | Both | R07,R12 | Ten-minute walkthrough rehearsal and independent modification exercise |

C01–C18 are a traceability decomposition of researched requirements; some combine multiple published statements. Engineering choices such as SQLite, exact test repetition count and a 24-hour buffer are proposed team standards, not organizer rules. Reconcile any new official wording before implementation.
