# Demonstration video script — local synthetic workflow

Prepared 12 October 2026 for I01.13; Fredrick, solo review. This is a script,
not a recorded rehearsal, qualifying video or submission. No domain is
available; recording the local Ubuntu browser requires no remote access.

## Evidence and timing constraint

The [verified Chrome runs](runs/I01.13-browser-verification.md) reached review
in **234.38 s for 500 kg** and **246.07 s for 1,000 kg**. These are measured
UI progress-to-review times, excluding introduction, human review and approval.
They are actual local Qwen/borrowed-MCP runs on synthetic records. Cold/warm
classification was not measured. The earlier 147.214 s HTTP result used a
different measurement boundary and is not a browser/video timing promise.

Both browser runs exceed the planned under-three-minute video requirement
before review. A qualifying recording is currently blocked by latency and an
unverified presentation of actual tool calls from the recorded run. Rehearse
and measure any authorized improvement, or obtain official format clarification.
Do not cut, accelerate, splice or replace live execution with replay to claim
an unedited qualifying run. Existing screenshots/traces can support a clearly
labelled evidence walkthrough; that walkthrough does not satisfy the live-run
requirement. No new optimization is implemented by this preparation.

## Before recording

Follow the [Ubuntu operations guide](../infra/LOCAL_OPERATIONS.md). Use one
operator, one workflow and one API worker. Sign in before starting capture;
keep the token file, terminal history, browser developer tools/request headers,
private config and desktop notifications off screen. The visible identity is
`test:local-demo-officer`: a local test identity, not practitioner validation.
Keep the synthetic banner visible. Use a fresh attempt and retain its workflow
ID and actual wall-clock start/end times. Do not use an already approved draft
as if the agent has just created it.

For the new recorded run, confirm a credential-free view of actual tool names,
inputs, outputs and timestamps is available. The verified UI shows progress,
comparison and provenance; live tool-event visibility in a video has not been
verified. A previous trace must be labelled with its original run ID and cannot
stand in for new execution. Do not expose bearer headers while solving this gap.

## Spoken script and screen actions

| Segment | Screen action | Narration |
|---|---|---|
| Introduction, planned 0:00–0:20 | Show local URL, synthetic banner and 500 kg request. | “SokoSignal is an Agriculture market comparison and internal review prototype. These maize prices, costs, markets and capacity are invented. A partner office and practitioner workflow remain unconfirmed.” |
| Start, planned 0:20–0:30 | Start a new 500 kg comparison. Show RUNNING and workflow ID; start wall-clock measurement. | “The local Qwen model uses borrowed Fetch to retrieve our public synthetic fixture and selects our own market search, comparison and private-draft tools. Software calculates the totals; the model cannot approve the draft.” |
| Actual execution, variable duration | Keep the unedited run and visible timer. Show sanitized actual tool events if available. | “The workflow is still running. Previously measured browser times to review were 234.38 and 246.07 seconds; this run's time will be recorded separately.” |
| Review, planned 30–40 s after pending | Show comparison, source, snapshot hash and retrieval provenance. | “For this 500 kg fixture, Market A has gross KES 20,000, transport KES 2,000 and net KES 18,000. Market B has higher gross, KES 22,500, but transport KES 8,000 leaves net KES 14,500. Market A leads by KES 3,500. Loss, handling and fees are explicitly zero assumptions. These are scenario totals, not live market advice.” |
| Decision, planned 15–20 s | Show exact pending draft ID/version/hash; approve internal review and show outcome. | “This local test officer approves this exact draft version. The server records the decision and resumes the workflow to approved internal review. No advisory is delivered.” |
| Limitations, planned 10–15 s | Show completed status and measured elapsed time. | “Two browser workflows verified approval and rejection. Eight diverse model evaluations, independent review, practitioner feedback and fresh-clone reproduction are still missing. This application remains local.” |

The planned speaking/action durations are estimates, not measured rehearsal
results. With the observed 500 kg latency, this full script exceeds three
minutes. Rejection and refresh can be demonstrated separately using the verified
1,000 kg case; do not add a second model workflow to a claimed short recording.

## Failure and recording acceptance

If the run fails, show its failure code, keep the recording/evidence and mark
that attempt failed. Correct the cause before a separately identified new
attempt. On completion record actual duration, workflow ID, tool evidence,
quantity, outcome and source revision. Check the entire recording for secrets,
real tool execution, exact-hash human review and uninterrupted wall time.
Upload/public access, video URL and duration verification remain unperformed.


## Optional temporary remote presentation

The [protected Quick Tunnel](../infra/QUICK_TUNNEL.md) was subsequently launched
for one owner-authorized, automatically bounded test. See the execution handoff
for actual start/expiry and phone access results; setup is not a video rehearsal. Initial access is limited to the owner's supplied email; it is not a
public judge link. Complete email PIN and dedicated synthetic test-officer login
off-camera before capture. Say: “This is a temporary protected preview from the
same Ubuntu machine. The URL changes when the connector restarts, and its
availability is not guaranteed.” For a local recording, keep using loopback.

Record a new remote run's elapsed time separately if later authorized; the
existing 234.38/246.07 s measurements remain local Chrome evidence. A tunnel
is not a measured speed improvement. Authentication/setup and human review
cannot be silently removed from claimed end-to-end timings. Keep OTP inboxes,
cookies, bearer tokens and tunnel diagnostics off screen. A completed recording
must still meet the qualifying unedited duration/tool-visibility requirements.


The one-hour check's local API/model run reached pending review in **249.488 s**
for 500 kg; [actual record](../evals/results/I01.13-one-hour-local-workflow.json).
This is loopback request-to-review time with polling, not phone/browser latency.
Its actual three own calls and borrowed retrieval are in the
[sanitized trace](../evals/results/I01.13-one-hour-local-trace.jsonl). Any replay
of that trace in a video must retain the original run label and not represent
new live execution. An initial phone “Bad request” was followed by owner-confirmed email
verification and officer sign-in. No remote model run or stored officer
decision was verified. The connector expired at 16:04:44 EAT; this URL
is no longer a presentation option.
