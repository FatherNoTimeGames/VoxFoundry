# Authoritative tracker — revised Sites-first scope

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
2. **S0-I2** — Restore permission-review execution and review/save documentation host access (review).

No implementation task can complete its remaining checks until these external blockers
clear. Final Phase 0 deliverable **S0-08** is the requested Sites deployment prompt;
its conditional draft is not marked complete or represented as deployable evidence.

## Phase 0 — active

| ID | Phase | Priority | Status | Description | Dependencies | Acceptance criteria |
| --- | --- | --- | --- | --- | --- | --- |
| S0-I1 | 0 | P0 | review | Identify Sites interface/product | S0-01 | User/product evidence names intended builder/runtime or official docs; no deployed Site required. |
| S0-I2 | 0 | P0 | review | Recover executable research/live-test permissions | S0-01 | Automatic permission review available; requested docs host additions reviewed/saved; affected operation retried and actual result recorded. Draft save alone is insufficient. |
| S0-02 | 0 | P0 | blocked | Verify Sites/ChatGPT/auth/storage/file APIs and direct worker integration | S0-I1, S0-I2 | Primary versioned documentation plus disposable supported endpoint tests; direct support/limits, app-owned vs external chat, mobile auth, PC-off persistence and quotas explicit. |
| S0-03 | 0 | P0 | blocked | Complete local disposable audio protocol experiment | S0-I2 | Persistent/authenticated queue, outbound harness, validated upload, idempotency/leases/retries/disconnects and live HTTP/browser play/download at M tested; Windows/Android absence disclosed. Seven state-machine tests pass, live checks unrun. |
| S0-04 | 0 | P1 | blocked | Verify AI/wiki/maps/TTS/hosting primary research | S0-I2 | REFERENCES records retrieval/version/confidence/contradictions; actual map features/rights, Wiki auth/transport, TTS artifacts/hardware limits and host costs verified or concrete external blocker. Reuse earlier TTS evidence. |
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
