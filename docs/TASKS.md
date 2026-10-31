# Authoritative tracker — revised Sites-first scope

## Active scope — Site first, Windows audio planned (2026-10-30)

The user's latest direction supersedes the older audio-first gates below. Finish
Site functionality before resuming the Windows audio connection. Preserve all task
IDs, source and evidence; **deferred** means removed from the current critical path,
not completed. [Planned feature and resume criteria](PLANNED-FEATURES.md).

### Next Up (active; maximum five)

1. **S0-02** — Generate/review initial migrations using the supported Drizzle tools
   after dependency approval, obtain the lifecycle helper, then verify hosted acceptance
   after authorization. Binding and migration-sidecar copy contracts are resolved;
   sign-in/storage/MCP documentation is recorded. Worker access is deferred.
2. **S0-D1** — Confirm intended-account limits/allowances and the approved hosting
   budget against the dated public terms before resource creation. No audio bridge is needed
   in the active design.
3. **S0-07** — Produce the Site-only feasibility/architecture checkpoint with honest
   runtime/auth/persistence/mobile evidence. No Windows audio round trip is required.
4. **S0-08 / S0-09** — Finalize the Site foundation prompt and review the Site-only
   preflight. Existing deployment/spend restrictions continue to apply.
5. **S1-01** — Validate the prepared owner/project/document foundation and Android-first
   navigation/editor on private Sites after preflight; complete the remaining slice gaps.

Foundation preparation update (2026-10-30): `sites/studio` contains the isolated,
dependency-free local Site slice; **19 component tests and ESM validation pass**.
S1-01 remains incomplete pending private hosted auth/D1 and real mobile verification.
This is safe local preparation, not completion of S0-09 or a live phase exit.
Manual saves are implemented; S1-02 autosave/durable draft/session restoration is
not complete. No R2 upload, MCP tools, Wiki, atlas or audio capability was added.
Next work is migration generation/review, supported lifecycle tooling and the
account cost/configuration gate before provisioning; then validate this concrete slice
on private Sites and real Android. See [foundation evidence](VALIDATION.md#site-foundation-local-slice--2026-10-30).

Contract review update (2026-10-31): sign-in/storage/MCP documentation and current
public hosting terms have now been accessed. [Contract checkpoint](research/sites-platform-contract.md)
records exact evidence and access limits; [costs](research/costs.md) records dated
public terms. **S0-02 is blocked only for the remaining exact binding/migration and
live acceptance work**, not because Sites identity/storage/MCP are undocumented.
Required lifecycle/parser/starter assets are not available in this executor or the
attempted skill-resource paths. Do not repeat guesses or create a resource to probe.
S0-D1 has public-rate evidence; intended account applicability/budget remains pending.
The newer pinned public-source follow-up below supersedes migration-copy unknowns.

Binding follow-up (2026-10-31): the official Manage a site subpage resolved the
manifest format; added `sites/studio/.openai/hosting.json` without a project ID and
verified its build copy and fail-closed bundled server. This removes that specific
blocker. Supported migration generation/discovery/packaging, lifecycle tooling and
hosted acceptance remain unverified. No generator/framework packages were installed.

Migration packaging follow-up (2026-10-31): read OpenAI's public `openai/sites` source
at `7eb9d4b9cf93ad7e64aebc8a5ca70e29ec2cfb94`. The production plugin confirms the
`drizzle/**` → `dist/.openai/drizzle/**` copy and stale-metadata replacement contract.
Adapted the native build without installing Vite. **Four local contract checks passed**
against the original official production hook; **19 foundation tests rerun, all passed**;
ESM build passed. These fixtures prove file copying only, not valid migration history.
The generator pins are `drizzle-kit@0.31.10` / `drizzle-orm@0.45.2`; neither is installed.
Next requires separate dependency approval, then actual generation/schema review and
local application checks. Lifecycle helper, account/budget and hosted/mobile gates stay open.

### Active dependency changes

| ID | Status | Current scope / dependencies |
| --- | --- | --- |
| S0-I1 | done | Intended product identified as the installed OpenAI Sites plugin; this does not prove runtime integration. |
| S0-I2 | deferred | Corrected legacy audio live-test reruns are preserved, but do not block Site work. |
| S0-I3 | done | Current Sites identity/storage/MCP and primary product/cost documentation accessed; missing executor assets and later map/Wiki sources are separate gates. Old access failures remain historical. |
| S0-02 | blocked | Binding, identity/storage/MCP and pinned migration-sidecar copy contracts documented; local copy checks pass. Generated/reviewed migration history, lifecycle helper and live acceptance remain pending. |
| S0-03 | deferred | Existing audio transport experiments/tests preserved; no new audio implementation required now. |
| S0-04 | review | Site/ChatGPT, enabled Wiki/maps, rights and hosting research; TTS/model/worker research deferred. |
| S0-D1 | review | Site hosting/cost decision; depends on S0-02 and relevant S0-04 findings. |
| S0-05 | review | Architecture revised for Site-only operation and planned audio; remains a design, not hosted verification. |
| S0-06 | deferred | Actual Site → Windows → audio → Android proof moves to the planned audio feature; no Site-phase dependency. |
| S0-07 | blocked | Site-only evidence checkpoint; depends on S0-02, S0-04, S0-05 and S0-D1; excludes S0-03 and S0-06. |
| S0-08 | blocked | Site foundation deployment prompt; depends on S0-07; no worker/audio acceptance requirements. |
| S0-09 | blocked | Site-only preflight review; depends on S0-08. Deferred audio is not a failed Site exit gate. |
| S1-01–S5-03 | planned | Site foundation, writing/library, AI/review, enabled Wiki and atlas; preserve existing feature IDs and evidence-based exits. |
| S5-04 | planned | Site completion checkpoint after active Site slices: sign-in, project/document CRUD, saves/sync/conflicts, library/search/sources, revisions/export/restore, supported ChatGPT tools/review, atlas and enabled Wiki. Private access, costs and real Android usability verified; PC/worker not required. |
| S6-01–S8-04 | deferred | Narration, audio editing/export, Windows companion/distribution and audio-specific reliability. Resume after S5-04 and explicit scope/cost/model review. General Site backups, access control and restore stay required in phases 1–5. |

No Site is deployed or declared complete; the prepared foundation source is local only.
Hosted identity/D1/R2/ChatGPT and actual Android Site use remain unverified. Desktop
web testing remains relevant; Windows companion execution is not a current Site gate.
No worker credentials, pairing, queue schema or tone player are required in the
active Site. Existing audio prototypes remain unshipped research.

## Historical checkpoints and superseded tracker

The following records retain the prior scope, task IDs and test history. Their old
Next Up lists, audio prerequisites and Phase 0 exit wording are superseded by the
active scope above; do not restart the worker/audio proof to unblock Site work.

## Recovery review checkpoint — 2026-10-30

Recovered the exact checksum-verified three-chunk patch on a separate branch based
on `9a0c8213719d626c84658105e8febcb4f6cdca3c`. Original source provenance:
`e5b1ea245bd12ae5c0de28e1438013557f72f948`; local patch-import commit:
`48deb9c10026008433be08bc292ad639bff96a1a`. Prior branch/work preserved.
See [actual recovery evidence](VALIDATION.md#recovered-patch-and-independent-review--2026-10-30).

- **S0-03, component portion only:** independently reproduced 16 JS/SQL + 9 Python
  passes before edits. Reviewed and fixed request-ID type coercion and insecure
  existing POSIX worker-cache permissions. Final checks: **19 JS/SQL + 10 Python
  passed**, 0 failed, 0 skipped; ESM build passed. The new POSIX-specific test is
  intentionally skipped when run on Windows; its NTFS ACL gate remains manual.
- **S0-02 / S0-06:** hosted Site/D1/R2/private dispatch, actual Windows and actual
  Android remain unverified; no task is upgraded to hosted end-to-end completion.
- **S0-07 / S0-08 / S0-09:** still incomplete; no Phase 0 exit or full-app work.
- User authorized only committing/publishing the separate review branch, never a
  merge/main update, force push, deployment, paid resources, models or significant
  dependency installs. Git transport remains unavailable; use supported GitHub
  operations and verify the published head/tree before claiming branch publication.

Current Next Up remains the five direct-Sites gates in the continuation section
below: account cost/budget, exact binding/migration configuration, private disposable
runtime verification after those gates, Windows/Android checks, evidence/exit review.

## Direct Sites continuation (2026-10-29)

User authorized the smallest direct-Sites Phase 0 proof only, preserving the pinned
`9a0c8213719d626c84658105e8febcb4f6cdca3c` work. See
[implementation, exact sources, costs and manual gates](../sites/phase0/README.md).
The historical tracker below is preserved; these notes supersede its claims that
Sites tools/documentation are unavailable in this conversation.

- **S0-I1:** Intended product identified as the installed OpenAI Sites plugin. Its
  storage, identity/service-access, MCP and Worker ESM references were accessed.
  A published runtime/build version is not supplied; runtime proof remains pending.
- **S0-02:** Partial documentation evidence now supports D1/R2, authenticated MCP and
  Site service ingress. Scoped/revocable device auth is implemented separately.
  No private dispatch or hosted binding/API test; task remains incomplete.
- **S0-03:** New isolated `sites/phase0` component tests pass (16 JS/SQL + 9 Python).
  Original POC remains untouched; its old live suite was not rerun. Tests do not prove
  actual cloud persistence, Windows, Android or hosted HTTP integration.
- **S0-D1 / S0-06:** No external bridge adopted. No Site/resource provisioned or
  deployed. Account pricing/budget and exact ESM binding/migration configuration
  remain gates before hosting. Actual Windows/Android steps are documented and unrun.
- **S0-07 / S0-08 / S0-09:** No end-to-end pass, final deployable prompt or Phase 0 exit.

Current Next Up (maximum five):
1. Establish Sites account pricing/allowances and an approved bounded budget.
2. Verify exact D1/R2 binding and migration integration for the dependency-free Worker.
3. After those gates, deploy one private disposable Site and test service ingress plus
   independent worker identity. Do not generate/rotate a bypass token without the
   explicitly requested native operation.
4. Run the supplied Windows and real Android matrix, including PC-off playback.
5. Record evidence and remaining failures before any Phase 0 exit decision.

2026-10-29. New phase/task IDs use **S**. Old P tasks/acceptance history are retained
unchanged in [the historical tracker](archive/local-first-2026-10-29/TASKS.md) and Git;
they do not establish any Site, Windows worker or Android integration. Full new product
implementation is blocked until revised Phase 0 feasibility and architecture approval.

Statuses: todo/in-progress/blocked/review/done. Priorities P0 gate, P1 required, P2
optional. Dependencies require done; external evidence/approvals are explicit tasks.
Mobile criterion **M**: phone 360–390px first, tablet ~820px, desktop ~1440px; 44px targets,
compact readable layout, touch/no-hover, keyboard/screen-reader access and durable
saved/conflict state. Real Android verification is distinct from browser emulation.

## Next Up (unblocked input/recovery tasks; maximum five)

1. **S0-I1** — Identify the intended Sites product and official contract (review).
2. **S0-I2** — Unblock corrected local test re-verification (review).
3. **S0-I3** — Review/save official documentation host additions (review).

Local experiment completion requires execution access only; platform identification
and documentation access independently gate the Sites/hosting research. Final Phase 0 deliverable **S0-08** is the requested Sites deployment prompt;
its conditional draft is not marked complete or represented as deployable evidence.

## Phase 0 — active

| ID | Phase | Priority | Status | Description | Dependencies | Acceptance criteria |
| --- | --- | --- | --- | --- | --- | --- |
| S0-I1 | 0 | P0 | review | Identify Sites interface/product | S0-01 | User/product evidence names intended builder/runtime or official docs; no deployed Site required. |
| S0-I2 | 0 | P0 | review | Recover executable research/live-test permissions | S0-01 | Initial live tests and primary reads executed; later review timeouts/capacity prevented corrected live reruns. Complete supported execution of post-fix verification; no bypass. |
| S0-I3 | 0 | P0 | review | Enable official documentation destinations | S0-01 | Review/save requested host additions and verify actual runtime access; draft persistence alone is insufficient. Package-manager GitHub sources may be read under existing presets. |
| S0-02 | 0 | P0 | blocked | Verify Sites/ChatGPT/auth/storage/file APIs and direct worker integration | S0-I1, S0-I2, S0-I3 | Primary versioned documentation plus disposable supported endpoint tests; direct support/limits, app-owned vs external chat, mobile auth, PC-off persistence and quotas explicit. |
| S0-03 | 0 | P0 | blocked | Complete local disposable audio protocol experiment | S0-I2 | Persistent/authenticated queue, outbound harness, validated upload, idempotency/leases/retries/disconnects and live HTTP/browser play/download at M tested; Windows/Android absence disclosed. Seven component tests pass; initial live run 7 passed/5 fixture failures; corrections awaiting rerun. Linux worker uploads observed; no final playback/download pass. |
| S0-04 | 0 | P1 | blocked | Verify AI/wiki/maps/TTS/hosting primary research | S0-I2, S0-I3 | REFERENCES records retrieval/version/confidence/contradictions; actual map features/rights, Wiki auth/transport, TTS artifacts/hardware limits and host costs verified or concrete external blocker. OpenAI example README, Wiki Git docs and Leaflet license now read; full platform/map/auth/cost checks remain. Reuse earlier TTS evidence. |
| S0-D1 | 0 | P0 | blocked | Approve any bridge/fallback and hosting/cost decision | S0-02, S0-04, S0-05 | Evidence determines direct route first; exact smallest bridge/fallback/costs presented; explicit approval before platform change, paid deployment or exposure. If direct works, record bridge unnecessary. |
| S0-06 | 0 | P0 | blocked | Actual Site → Windows → Site → Android proof | S0-02, S0-03, S0-D1 | Deployed disposable Site approved passage reaches Windows harness, audio upload/status survives disconnection/retry; real Android plays/seeks/downloads/opens offline; file accessible with PC off; auth and retention/costs tested. No emulation substitute. |
| S0-07 | 0 | P0 | blocked | Feasibility evidence and architecture checkpoint report | S0-02, S0-03, S0-04, S0-05, S0-06 | Report actual proof, support/limits, costs/security, unresolved decisions and recommended topology; no full-success claim with unrun gates. Partial blocker report is not exit completion. |
| S0-08 | 0 | P1 | blocked | Deliver final Sites deployment prompt (user-requested final deliverable) | S0-07 | Copy-ready platform-specific prompt covers verified persistence/ChatGPT integration, owner/device auth, queue/files, Android M, costs, secrets, tests/rollback and placeholders; no invented APIs or implicit deployment approval. Conditional draft exists in SITES-DEPLOYMENT-PROMPT. |
| S0-09 | 0 | P0 | blocked | Approve revised Phase 0 exit | S0-08 | User approves evidence-backed architecture and prioritized plan, with actual required integration results; scope/model/cost/distribution exceptions recorded. |

## Later phases — dependency-aware plan (not authorized)

| ID | Phase | Priority | Status | Description | Dependencies | Acceptance criteria |
| --- | --- | --- | --- | --- | --- | --- |
| S1-01 | 1 | P0 | blocked | Supported Site project/auth/storage foundation | S0-09 | Authorized project CRUD, persistent central store, PC-off availability, permission isolation and M workflow on actual Android/Windows. |
| S1-02 | 1 | P0 | blocked | Autosave, sync and session restoration | S1-01 | Separate durable-save, second-device visibility and app-session restoration tests; no silent concurrent overwrite; app-owned conversations only; M editing/navigation. |
| S1-03 | 1 | P0 | blocked | Foundation exit review | S1-02 | Mobile workspace acceptance evidence and explicit user phase approval. |
| S2-01 | 2 | P1 | blocked | Unified graph, sources, search and organization | S1-03 | Documents/entities/relationships, provenance/uncertain chronology, project types, states, nested tags/filters/collections/FTS; approved content separate from inferred/AI; M. |
| S2-02 | 2 | P0 | blocked | Revisions and independent portable exports | S2-01 | Original retention, immutable comparisons/restore; Markdown/JSON/media archive includes graph, sources, maps, approvals, sessions/audio as present; fresh-store round-trip without original DB; M controls. |
| S2-03 | 2 | P0 | blocked | Library exit review | S2-02 | Interconnected library, access/sync/conflict/export/restore tests and user approval. |
| S3-01 | 3 | P0 | blocked | Verified unified ChatGPT workspace | S2-03 | Supported context/actions, app sessions, incremental authorized FTS/relationship retrieval, stale-summary handling, source/original/hybrid co-writing; account/usage limits documented; M on real devices. |
| S3-02 | 3 | P0 | blocked | Central Review Queue and canon promotion | S3-01 | Typed evidence-backed proposals across records/maps/wiki/scripts, readable diffs, accept/reject/revise/defer/conflict-safe batches; autosave never approves/publishes; M. |
| S3-03 | 3 | P0 | blocked | AI/review exit | S3-02 | Real supported ChatGPT collaboration and review/canon tests on Android/Windows; user approval. |
| S4-01 | 4 | P1 | blocked | Wiki read/auth/index/provenance | S3-03 | Intended wiki initialized/read using supported minimum-scope auth, pinned remote versions/source preservation and M browsing/search; revoked access handled. |
| S4-02 | 4 | P0 | blocked | Bidirectional wiki proposals/publishing | S4-01 | Baseline/local/remote conflicts, explicit per-diff remote approval, re-fetch/expected head, no force push, read-after-write and backup restore; M review. |
| S4-03 | 4 | P0 | blocked | Wiki exit | S4-02 | Disposable authorized remote tests and explicit phase approval. |
| S5-01 | 5 | P1 | blocked | Uploaded maps and touch-linked atlas | S4-03 | Rights-cleared background/version/CRS, pan/pinch/tap/keyboard marker details, layers/search/filter/library links; confidence/source/placement states; M. |
| S5-02 | 5 | P1 | blocked | Regions/routes/timelines/views and authorized imports | S5-01 | Editable geometries independent of background, historical/uncertain filters, saved views, map/library/script links; AI placement stays proposed; external terms verified before imports; M. |
| S5-03 | 5 | P0 | blocked | Atlas exit | S5-02 | Real Android/tablet touch and portable geometry round-trip evidence; user approval. |
| S6-01 | 6 | P0 | blocked | Exact model approval and listening/hardware trial | S5-03 | Artifacts/sizes/licenses/purposes separately approved before downloads; rights-cleared voices, RTX variant/CPU measurements, blind documentary quality/consistency review. |
| S6-02 | 6 | P0 | blocked | Modular worker narration pipeline | S6-01 | Provider capabilities, pinned text/settings, segmentation/voices, local/central durable jobs, cancel/retry/resume/cache/selective regeneration, validated uploads and progress; M controls. |
| S6-03 | 6 | P0 | blocked | 60-minute recovery and phase review | S6-02 | Actual Windows/3060 manuscript completes with forced disconnects/crashes and complete segment ledger; no duplicate committed results/missing audio; user approval. |
| S7-01 | 7 | P1 | blocked | Synchronized non-destructive audio editing | S6-03 | Segment/script playback/waveforms, timing/silence/gain recipes and selective regen; originals/history preserved; M comfortable review. |
| S7-02 | 7 | P1 | blocked | Mastering and MP3/M4B releases | S7-01 | Metadata/artwork/chapters/presets, loudness/peak checks, FFprobe/full decode/coverage validation, immutable release history; real Android playback/download/offline/seek. |
| S7-03 | 7 | P0 | blocked | Export exit | S7-02 | Finished portable audiobook compatibility and user approval. |
| S8-01 | 8 | P0 | blocked | Production remote-device reliability | S7-03 | Scoped pairing/revocation/TLS/quotas/monitoring, durable private streaming/downloads, expired credentials/URLs/worker-off recovery; M production controls. |
| S8-02 | 8 | P1 | blocked | Windows tray/install/update/release pipeline | S8-01 | Windows 10 dependency/licensing matrix, reproducible build, restart/recovery, installer/update/uninstall data preservation; actual publication only separately approved. |
| S8-03 | 8 | P0 | blocked | Full backups/upgrade/ownership recovery | S8-02 | Independent project/full-store restore, migrations/failed upgrades, all app/worker assets and approved records preserved; M recovery controls. |
| S8-04 | 8 | P0 | blocked | Distribution/remote-production exit | S8-03 | Real-device full workflow without dev environment, costs documented, user approval before release. |
| S9-01 | 9 | P2 | blocked | Additional providers, roles, maps and sound design | S8-04 | Each feature separately justified/approved for rights/costs/downloads; existing histories and cache invalidation remain reliable; M where visible. |
| S9-02 | 9 | P2 | blocked | Visualization/geographic reasoning/Android-native exploration | S9-01 | Evidence/version-aware geography, useful relationship UI, optional device inference with measured limits; no paid service assumed; M. |
| S9-03 | 9 | P0 | blocked | Advanced regression and phase review | S9-02 | Portability/sync/review/core production regression evidence and user approval. |

## Completed revised-scope work

| ID | Phase | Priority | Status | Description | Dependencies | Acceptance and evidence |
| --- | --- | --- | --- | --- | --- | --- |
| S0-01 | 0 | P0 | done | Inspect/reconcile scope and available environment | none | Clean base 8bf7cd9; no Sites tool, Site/Windows app/deployed device supplied; user clarifications recorded; previous docs/source/history preserved. |
| S0-05 | 0 | P1 | done | Document conditional unified architecture and plan | S0-01 | ARCHITECTURE/REQUIREMENTS cover knowledge/AI/canon/review/wiki/atlas/exports and worker boundaries; direct/bridge/fallback gates and revised roadmap explicit. This is design completeness, not feasibility approval. |

Continuation history: S0-I2 briefly recovered for the initial live run and primary
source reads, then was reopened because fixed-test reruns were blocked by later
review deadlines/capacity. Test failures are recorded separately from review failures.
