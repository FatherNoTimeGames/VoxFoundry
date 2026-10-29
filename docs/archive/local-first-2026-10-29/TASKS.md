> Historical local-first plan archived at scope reset. Superseded by the current
> root AGENTS.md and docs/TASKS.md. Retained for evidence/history; not active instructions.

# Authoritative task tracker

Updated 2026-10-29. Status vocabulary: `todo`, `in-progress`, `blocked`, `review`,
`done`. Priorities: P0 critical/gate; P1 required; P2 enhancement. Dependencies require
`done`, including explicit user gates. Phases 0–1 are approved; Phase 2 implementation
is complete pending P2-05 review. Phases 3 onward remain blocked.
Approval never follows from silence. Update status as dependencies clear. IDs persist.

## Next Up (unblocked; maximum five)

1. **P2-05** — Review manuscript/history validation and approve Phase 2 exit (review).

After approval, P3-01 is next: recheck commercial-use licenses and prepare exact model
artifact sizes/purposes for separate approval **before** downloading anything. No speech
engine/weights or paid/distribution authority is implied. Windows/Android-device checks
remain unverified; standalone project transfer/backup remains a required P6-02 gate.

## Active and planned work

Every row specifies phase, priority, status, description, dependencies and acceptance.
Phase-exit tasks require a user approval record in DECISIONS as well as test evidence.
Acceptance criteria reference VALIDATION for the required test scenarios, not a claim
those tests have run. An engine/model approval covers exact artifacts, not a family.

| ID | Phase | Priority | Status | Description | Dependencies | Acceptance criteria |
| --- | --- | --- | --- | --- | --- | --- |
| P2-05 | 2 | P0 | review | Validate manuscript phase and approval | P2-04 | Import/edit/conflict/restart/snapshot/restore scenarios pass; user approves Phase 2 exit. |
| P3-01 | 3 | P0 | blocked | Exact model/license/download approval and listening trial | P2-05 | Artifact sizes/revisions/checksums/terms/purpose and voice-reference rights reviewed; explicit approval before downloads; documented blinded listening/hardware results; chosen baseline or actionable blocker, no invented winner. |
| P3-02 | 3 | P1 | blocked | Provider protocol, isolated runtime, previews/profiles | P3-01 | Versioned capabilities/errors/cancel contract; fake provider tests and approved real provider previews; unsupported controls visible; exact runtime/model/voice provenance; CPU/Windows results recorded. |
| P3-03 | 3 | P0 | blocked | Segmentation, cache and dependency planning | P3-02 | Frozen narration plans, stable reconciliation incl. repeated text/split/merge; canonical fingerprints; only affected segments invalidate; stale artifacts preserved. |
| P3-04 | 3 | P0 | blocked | Persistent queue, leases and recovery UI | P3-03 | Progress, retry/backoff/cancel/resume, worker timeout/OOM/crash/disk-full handling; verified staged audio; lease recovery; no duplicate success or silent skipped segments. |
| P3-05 | 3 | P0 | blocked | 60-minute narration recovery and phase approval | P3-04 | Approved real engine completes frozen 60-minute script on target Windows/3060 with forced worker/service interruptions, cache reuse, coverage/checksums/offline proof; CPU trial distinct; user approves Phase 3 exit. |
| P4-01 | 4 | P1 | blocked | Segment playback, script navigation and waveforms | P3-05 | Ranged playback and source/timing map agree; waveform cache rebuilds; segment selection/review keyboard usable; stale status visible. |
| P4-02 | 4 | P1 | blocked | Non-destructive timing, silence and selective editing | P4-01 | Versioned recipes/production snapshots, trims/silence/fades/order; local regeneration only; undo/history and raw audio preserved. |
| P4-03 | 4 | P1 | blocked | Mastering and quality checks | P4-02 | Two-pass normalization/true-peak checks with recorded settings; silence/clipping/truncation flags; repeat render references immutable inputs; listening review. |
| P4-04 | 4 | P0 | blocked | Validate production workflow and phase approval | P4-03 | Representative episode refined without full regeneration; timeline/PCM/history checks and UI review pass; user approves Phase 4 exit. |
| P5-01 | 5 | P1 | blocked | Export presets, MP3 and M4B | P4-04 | Metadata/artwork/chapter timeline from exact production; staged outputs, explicit failure and missing-segment prevention; native AAC path/license checked. |
| P5-02 | 5 | P0 | blocked | Export validation and immutable release history | P5-01 | FFprobe/decode/coverage/checksum tests, ordered chapters and expected metadata/artwork; failed exports never released; reproducible provenance and release retention. |
| P5-03 | 5 | P0 | blocked | Android offline compatibility and phase approval | P5-02 | Two documented Android audiobook players tested for offline load/play/seek/chapters/resume; defects tracked; user approves Phase 5 exit. |
| P6-01 | 6 | P0 | blocked | Finalize packaging/license/update trust design | P5-03, P0-07 | Installer/toolchain/license BOM settled, FFmpeg/phonemizer/model rights cleared, Windows 10 support matrix and free signing/trust limitations documented; user approval for consequential tradeoffs/costs. |
| P6-02 | 6 | P0 | blocked | Backups, standalone project archives and restoration | P6-01 | Consistent DB+blob backup, checksummed versioned project archive, new-location restore/import with collision remapping and traversal/bomb/schema rejection; history and resolved shared dependencies complete; restore/transfer into fresh library without original DB; models declared separately. |
| P6-03 | 6 | P1 | blocked | Reproducible Windows builds and model installer | P6-02 | Clean Windows build manifest and pinned tools/artifacts; installer without dev tools; approved first-run sizes/licenses/offline import; interrupted install recovery; third-party notices. |
| P6-04 | 6 | P0 | blocked | Release CI, updates and data-preservation tests | P6-03 | Build reproducibility comparison, release artifacts/checksums and trust path; explicitly authorized GitHub publication only; migration backup/restore and failed-update/uninstall preservation tested. |
| P6-05 | 6 | P0 | blocked | Fresh-install/offline acceptance and 1.0 approval | P6-04 | Windows 10 end-to-end production without dev tools/account/network after explicit model install; independently restored library; upgrade failure recovery; user approves Phase 6 exit before publication. |
| P7-01 | 7 | P2 | blocked | Additional engines and narrator roles | P6-05 | Each engine passes license/download/listening gates; roles/archival reading/dialogue frozen per segment; provider parity tests preserve existing projects. |
| P7-02 | 7 | P2 | blocked | Advanced pronunciation/pacing, presets and optional ambience | P7-01 | Scoped phoneme/control adapters, reusable versioned presets and non-destructive mix recipes; changed dependencies selectively invalidate; rights and quality checked. |
| P7-03 | 7 | P1 | blocked | Authenticated opt-in LAN / Android tablet control | P6-05 | Pairing, session revocation/CSRF/TLS trust, firewall guidance and scoped media access; unauthorized requests fail; localhost/offline workflow unchanged; device tests. |
| P7-04 | 7 | P2 | blocked | Optional GitHub project integration | P6-05 | Explicit scoped authentication, previewed artifact selection, no secrets/audio/model upload by default; retry/conflict behavior; offline operation never requires GitHub. |
| P7-05 | 7 | P0 | blocked | Advanced capabilities regression and phase approval | P7-02, P7-03, P7-04 | Restore/import, upgrades, original offline workflow and target-device regressions pass; feature limitations documented; user approves Phase 7 exit. |

## Completed task archive

Acceptance evidence below distinguishes documentation approval from tested foundation
behavior. Phase 0 documentation: `379a502`; approvals/license: `1deb001`; foundation
implementation: `9eff8e1`; Phase 1 audit: this documentation commit (see Git log). Original base:
`6e6e6cd`. Phase 2 implementation: `77a2165`. Phase 1 approved by Continue;
Phase 2 exit approval remains pending.

| ID | Phase | Priority | Status | Description | Dependencies | Acceptance and evidence |
| --- | --- | --- | --- | --- | --- | --- |
| P0-01 | 0 | P0 | done | Inspect repository/environment | none | README-only clean initial tree; no manifests/agent instructions; Git fsck and GitHub main read verified; Linux tools recorded in README. |
| P0-02 | 0 | P0 | done | Research engines/current primary sources | P0-01 | Kokoro/Chatterbox/F5/Piper plus XTTS/CosyVoice compared with controls/hardware/license/maintenance limits; sources and unverified model cards explicit in research file; no models downloaded. |
| P0-03 | 0 | P0 | done | Define requirements and evaluate stack | P0-01, P0-02 | REQUIREMENTS and DECISIONS cover offline/Windows constraints, non-goals, meaningful framework/storage/packaging alternatives and approval questions. |
| P0-04 | 0 | P0 | done | Design complete library/production system | P0-03 | ARCHITECTURE covers identities, relationships, immutable history, dependency invalidation, workers/jobs, crash recovery, backup/archives, audio/export, security and distribution. |
| P0-05 | 0 | P0 | done | Establish operating docs, roadmap/tracker and audit | P0-04 | AGENTS/README/ROADMAP/TASKS/VALIDATION and minimal ignore rules committed; local links, task IDs/dependencies, whitespace checked; phase-boundary audit recorded. |
| P0-06 | 0 | P0 | done | Approve architecture/prioritized plan (A01) | P0-01…P0-05 | Explicit user approval of D01–D07/plan recorded in DECISIONS; D06 provisional; no download/paid/distribution authority. |
| P0-07 | 0 | P1 | done | Select source license (A02) | P0-03 | User chose Apache-2.0; full LICENSE committed in 1deb001, README updated; third-party terms remain separate. |
| P1-01 | 1 | P0 | done | Pin toolchain and running local skeleton | P0-06 | Pinned Python/Node dependencies and locks; compiled same-origin React UI/FastAPI launcher; repeatable setup, CI definition, health and session/origin/CSRF tests pass locally. Remote CI unrun. |
| P1-02 | 1 | P0 | done | Library location/config/bootstrap and migrations | P1-01 | Central UUID library, two Alembic migrations, config/location rules, FK/WAL/durable settings, cross-process lock, reopen/version refusal and verified migration backup tests pass. |
| P1-03 | 1 | P1 | done | Safe multiple-project CRUD and series | P1-02 | Real UI/API multi-project CRUD/series, optimistic conflict incl. concurrent edits, reversible trash/restore and project isolation verified. |
| P1-04 | 1 | P0 | done | Immutable asset store and staged-write recovery | P1-03 | Streamed immutable asset imports, hash dedup/project references, journal reconciliation, partial/fsync/disk-full/crash/corrupt/missing/no-overwrite/concurrent upload tests pass. |
| P1-05 | 1 | P0 | done | Validate foundation and phase approval | P1-04 | 25 Phase 1 tests and local browser/restart workflow passed; Windows gate disclosed. User Continue approved phase exit; see DECISIONS. |
| P2-01 | 2 | P1 | done | Hierarchy and TXT/Markdown import | P1-05 | Typed hierarchy/import UI/API with cycle and project-scope constraints, ordering/references; original UTF-8/UTF-16 bytes retained; binary/encoding/size validation tested. |
| P2-02 | 2 | P0 | done | Editor drafts, autosave and revisions | P2-01 | Serialized conflict-safe autosave and visible saved state, immutable revision objects/DB triggers, snapshots freezing tree/revisions/settings/assets; browser in-flight typing and restart tests pass. |
| P2-03 | 2 | P0 | done | Compare and safe restore | P2-02 | Text and structural/settings/metadata/asset previews; stale previews rejected; restoring appends history and preserves later drafts/nodes/originals; corrupt-reference rollback tests pass. |
| P2-04 | 2 | P1 | done | Script identities and dictionary infrastructure | P2-03 | Version-1 paragraph IDs/offsets/lineage with conservative duplicate handling; immutable shared presets and versioned scoped overrides; literal pronunciation resolution/applicable fingerprints tested; no inference. |
