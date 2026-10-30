# Sites-first architecture; Windows audio planned

Status (2026-10-30): Site-only preflight, **not verified end to end**. The user
deferred the Windows audio connection until Site functionality is complete. No Site
deployed; no Windows or Android device attached. Existing
local application is preserved, not automatically adopted as the new central store.
See research/sites-worker-integration.md and VALIDATION for evidence boundaries.

## Conditional topology and alternatives

```text
Android / tablet / desktop web
   ↕ private Sites UI + supported ChatGPT tools (hosted behavior to verify)
Sites-native server routes / knowledge services / owner authorization
   ↕ documented D1 and R2 bindings (exact setup/runtime tests pending)
Persistent projects, documents, revisions, sources, atlas and exports

PLANNED AFTER SITE COMPLETION (not required or deployed now):
Windows worker → outbound authenticated jobs/uploads → private retained audio
```

Evaluate direct Sites-backed persistence/actions first. The installed Sites references
document D1/R2, ChatGPT sign-in and authenticated Site MCP tools; documentation is not
hosted runtime proof. The active Site has no external worker, queue or audio bridge
dependency. Do not add worker setup controls, service credentials or audio-job tables
to the Site foundation. See PLANNED-FEATURES.md for the deferred connection.

When the audio feature is separately resumed, a worker cannot assume access
to private platform DBs/files or the user's ChatGPT session. If direct endpoints are
unavailable, a candidate is one small HTTPS bridge with persistent metadata and private
objects, called through a supported Site integration. It needs explicit approval before
adoption/deployment and pricing review. If the Site cannot safely use it, stop and
propose the smallest mobile web + supported ChatGPT integration alternative; do not
silently switch platforms. Apps SDK is a research candidate, not proven Sites support.

Hosted state is necessary for PC-off availability. Prefer the verified platform's
supported store; otherwise evaluate one durable personal-use server (SQLite on local
persistent disk, single writer) versus managed relational DB/object store. No live
SQLite file over WAN, no ephemeral hosting disk, no direct browser DB admin keys.
Project originals/revisions/files live independently of any Windows machine. Future
uploaded audio must also remain independent of its worker. Local-first constraints
apply to future inference/cache/recovery, not central Site availability.

## Components and authority

- Site UI: phone-first project/chat/library/atlas/references/review navigation,
  bottom sheets/collapsible panels and additional desktop panels. No hover-only flows.
- Knowledge/application services: authoritative graph, revisions, permissions, canon,
  proposal/review transactions, search, session restoration and export manifests.
- AI adapter: only verified ChatGPT context/actions; app-managed conversations and
  session summaries tagged with source revisions. No private-history scraping or
  paid API assumed by subscription. Provider actions propose rather than approve.
- Integrations: wiki fetch/diff/approved publication, authorized map references/imports,
  portable archives. External content is untrusted and source-versioned.
- Planned audio transport, after Site completion: approved immutable script/config requests, device-scoped auth, leases,
  attempt history, upload validation, progress and durable completion artifacts.
- Planned worker, after Site completion: separate Python inference/FFmpeg processes and local SQLite job/cache state;
  interchangeable capabilities/engines, CPU where supported, RTX 3060 resources detected.
  Foreground harness only when audio work resumes; Windows tray/installer/update later.

Prior local Python/FastAPI/React/SQLite modules may supply domain rules and recovery
techniques. Do not restructure/delete them to pretend they are a Site. Isolated
`backend/voxfoundry/poc` uses a separate disposable database/storage/credential path.
No application-library migration is performed by that experiment.

## Central knowledge model

| Entity | Relationships and invariants |
| --- | --- |
| Project / Collection / SavedView | Source/original/hybrid type; independent permission/history/export; nested composable filters/sorts |
| Record / Document / Entity | UUID, project, kind, title, version/state; book/part/chapter/episode/manuscript/research or character/faction/location/event/object/concept |
| Relationship | Typed source/target IDs, project scope, validity/version, provenance; one authoritative record displayed in many views |
| Source / Citation | Original digest/URL, author/rights, retrieval date, game/world/version applicability, evidence spans/confidence/contradictions |
| TemporalAssertion | Era/event, uncertain date bounds/calendars, evidence and interpretation flags; no invented exact date |
| Revision / Snapshot | Immutable content/config/graph manifest; mutable draft/head with expected versions; restoration appends, originals retained |
| Conversation / ResearchSession | Application-owned turns/context/project/doc/map IDs, sync version, restored workspace; external ChatGPT histories only if supported |
| Proposal / ReviewDecision | Origin/AI model context, affected IDs/base versions, readable diff, rationale/evidence, accept/reject/revise/defer/batch audit |
| CanonPublication | Explicit approved record versions and promotion provenance; supersession/history, never automatic on autosave |
| MapVersion / Geometry / Marker | Background digest/license/dimensions/CRS, historical period, points/regions/routes, library/source links and placement confidence |
| Planned: Job / Attempt / Device | Future audio scope only; do not create these as a Site foundation prerequisite. Immutable approved requests, leases, scoped identity and durable recovery when resumed. |
| Planned: AudioArtifact / Production / Release | Future audio scope only; exact script/config/model provenance, validated bytes/timing and immutable release history when resumed. |
| WikiBinding / RemoteRevision | Repository/wiki/page/path and baseline SHA, imported provenance, approved diff, expected-head publishing and conflicts |

Separate content status (brainstorm/draft/proposed/approved/superseded/rejected/archived),
evidence classification (verified/interpretation/invention/uncertain), and production
status. A verified source assertion is not automatically approved canon. A manual map
placement is not automatically verified geography. Imported instructions cannot change
app permissions, approved canon or publishing policy.

## Consistency, sync, retrieval and review

Every save uses stable IDs and expected versions; return explicit conflicts and retain
local edits. Autosave means durable draft acknowledgment. Sync means another authorized
device sees it. Session restoration means app-managed conversations/project/doc/map/view
state resumes. Test each independently on real Android and desktop web; Windows
companion execution is deferred. PC-off Site use cannot
be implemented with a loopback-only library.

Incremental retrieval starts with scoped metadata/full-text search and follows typed
relationships/sources. Summaries record dependencies and become stale when authoritative
records change; they cannot override approved canon. Embeddings are optional, not a
paid default. Source-based projects distinguish evidence/interpretation/invention;
original projects respect canon and gameplay; hybrids preserve provenance boundaries.

All AI/atlas/wiki/classification/canon proposals enter one review system. Acceptance
checks expected versions and conflicts atomically; batch approval is limited to mutually
compatible proposals. Canon promotion requires an explicit action. Publishing a wiki
requires a separate explicit action against a re-fetched remote base. Autosave and
local approval never cause external publication.

## Planned audio job protocol and ownership (deferred)

This section preserves the future connection contract. It is excluded from current
Site preflight/completion and does not authorize adding a worker, audio bridge or
service credential. Resume only after the Site checkpoint and explicit feature review.

Approved requests pin script revision, text digest, provider/model/voice/version,
pronunciation/settings and generation purpose. Idempotency keys bind the request body.
Workers authenticate as scoped devices, poll outbound, claim finite leases, heartbeat,
and upload only to their current fenced attempt. Expired attempts cannot overwrite
newer results. Upload streams to staging with size/format/hash validation; publish
immutable bytes before committing success. Handle unknown commit outcomes by querying
status and idempotent retry; never promise exactly-once inference after every crash.
Durable cache/input fingerprints prevent avoidable duplicate work. Never omit failed
segments. Completed files remain in central storage when the worker is off.

The disposable POC implements this shape with one local owner/device and test tones,
not production OAuth, multi-tenant isolation, speech, Sites or Internet hosting. Credential
revocation/rotation/pairing, TLS, quotas/rate limits, retention, private streaming URLs
and safe cross-origin/Sites integration remain production/manual gates. Same-origin
cookies in a local browser do not prove third-party iframe/mobile cookie behavior.

## Atlas, wiki and portability

Rights-cleared uploaded maps are the independent option. Inspect the requested map
services/terms before any embed/import; user preference for Pindrop is recorded, not
an inspected feature claim. Image coordinates and background version are explicit.
Labels/markers/regions/routes are separate editable objects; AI placement is proposed
with evidence/confidence. Timeline views retain uncertain bounds and game versions.

Wiki import/publish adapter uses only documented transport/auth. Baseline/local/remote
comparison, re-fetch before commit, expected-head fast-forward checks, independent
backups and explicit per-diff publishing prevent remote overwrite. Engineering docs
stay in this repository; project wiki content is an optional integration.

Export each project to versioned JSON manifests plus Markdown and standard images/audio:
full graph, draft/canon states, sources/citations, maps/geometry, app-owned sessions,
revisions/approvals, model requirements and audio/release history. Embed resolved shared
presets/dependencies; cross-project links require explicit export policy/stubs rather
than silently copying private projects. Import/restore into a new empty store without
the original DB; verify hashes, schema, path/decompression bounds and round-trip IDs/
relationships. History is not backup. Do not hardwire essential data to a vendor UI.

## Cost and security limits

No cloud GPU or mandatory paid inference API. Local experiment has no new service fee;
network/hosting/storage/ChatGPT plan costs remain unknown until verified. Central media
adds storage/egress and must not rely on free-tier permanence. Pricing approval precedes
provider selection. Windows 10 lifecycle/dependency compatibility remains a documented
risk; target validation is required before distribution. Apache source license persists;
personal use does not clear map/model/voice/reference rights. No deployment/release is
authorized by a generated deployment prompt or this architecture draft.

## Historical Apps SDK candidate (preserved research, not an active platform change)

The installed Sites plugin is the identified target. The older candidate below is
retained for provenance only; it does not select a bridge or substitute Apps SDK for
Sites in the active Site-first plan.

OpenAI's official Apps SDK examples now verify a documented ChatGPT MCP/widget model
and explicitly require server-side production persistence. If the user identifies or
approves that product, one hosted MCP/application service sharing a durable knowledge
store, job API and private audio storage could minimize bridge components. This is not
a claim of Sites-managed DB/file access or a selected fallback. Full official docs,
account access/authentication, costs and real-device/runtime tests still gate adoption.
No browser protections were disabled and no public tunnel or server was created.
