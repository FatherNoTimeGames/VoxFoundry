# Supported ChatGPT collaboration — feasibility gates

Status: exact Sites product/runtime integration **unverified**. Official Apps SDK
example documentation (REFERENCES O3) is now read; full docs (O1) remain blocked by
proxy CONNECT 403. No ChatGPT runtime, deployed Site or app-managed chat service is
attached. Documentation evidence is distinct from a working connected app.

## Verified official example documentation

The OpenAI examples README describes MCP tool listing/calls and structured results
with widget resources, streaming HTTP/SSE transports, and example `window.openai`
helpers (`setWidgetState`, `callTool`, display/follow-up/external helpers). It includes
authenticated-server examples and says to enable developer mode/add a connector to
test in ChatGPT. Those account/UI details and runtime calls have not been tested here.

Crucially, its shopping-cart example says production state must be persisted server-side.
Widget/session state alone does not establish durable cross-device projects or supply
hosted storage. The README describes deploying your own MCP server; it does not verify
that the user's intended Sites product supplies database/file APIs or free hosting.
No local tunnel, public service, browser security change or SDK installation was performed.

If explicitly selected after verification, a candidate supported ChatGPT app could use
one hosted MCP/application service sharing knowledge/queue/private files with a scoped
outbound worker API. This remains a candidate, not an approved replacement for Sites.
Full authentication, Android behavior, plan/usage costs and persistent file APIs need
full official docs and actual account/device tests.

## What must be verified

- Identify the exact Sites product, supported runtime and account availability.
- Determine how ChatGPT receives permission-filtered app context and calls tools/actions;
  verify persistent app sessions, Android/Windows support and usage/rate restrictions.
- Check whether supported app actions can reach private knowledge/job/file services;
  evaluate sandbox/CSP/origin/file streaming limits and user authentication.
- Distinguish ChatGPT subscription usage, app hosting and paid inference API billing.
  Do not assume Plus supplies API credits or account conversations are queryable.
- Verify app-managed conversation/session persistence separately from ChatGPT history.
  Never automate browser sessions, export cookies, or scrape private chat transcripts.

## Proposed unified workspace contract (not implemented)

One project-aware session spans research, co-writing, worldbuilding, library/timeline
exploration, geography, canon checks, wiki proposals and narration preparation. Session
context identifies project, active document/revision, approved canon version, selected
map/version/region, sources and project instructions. Project instructions cannot
escalate permissions, auto-approve canon or publish remotely.

AI actions produce typed proposals with affected IDs/expected revisions, readable diff,
rationale, evidence/provenance and uncertainty. All writes go to the shared Review Queue;
approved canon changes require explicit user action. Autosaved text remains draft.
Local approval and wiki publication are distinct actions with separately checked tokens.

Retrieve incrementally: scoped metadata/IDs → full-text search → related records and
source passages → authoritative records when contradictions appear. Use FTS first;
semantic retrieval is optional and needs justification, not a paid embedding default.
Cache summaries with source revision hashes; stale summaries cannot override canon.
Keep verified facts, interpretations and inventions explicit in source/original/hybrid
projects. Finish the active concept before adding unrelated AI suggestions.

## Cross-device semantics

Autosave confirms server revision durability. Synchronization makes that revision
available on another authorized device with conflict checks. Session restoration
reopens the project, active documents, app-managed conversation, atlas view and review
state. These are separate acceptance checks; browser sessionStorage or a local SQLite
file cannot establish all three. Raw provider ChatGPT conversations must never be
claimed restorable unless an official supported API was actually verified.

If Sites cannot provide this contract, stop and present the limitation and smallest
supported alternative for approval. A paid API chatbot or standalone local editor is
not an equivalent automatic replacement for the requested collaboration experience.
