# Validation strategy and Phase 0 evidence

Design targets below are future acceptance tests, not completed software tests.
Use targeted tests per task and a broader suite at each integration/phase exit.
Do not add trivial tests just to populate a suite. Tests must fail when meaningful
behavior or data preservation breaks. Test doubles validate contracts; real-engine,
Windows, listening and device tests remain separate.

## Planned evidence

| Layer | Required checks | Phase |
| --- | --- | --- |
| Domain/storage | UUID/scoping, cyclic hierarchy rejection, optimistic conflicts, immutable revisions/snapshots, restoration preserving later work, atomic writes/reconciliation, migrations and version refusal | 1–2 |
| UI/API/security | Multi-project create/update/trash/restore, invalid input, restart persistence, saved/conflict state, loopback Host/Origin/session checks, path escape and unsafe research rendering | 1–2 |
| Planning/providers | Repeated text and split/merge identity, relevant dictionary changes, unchanged cache reuse, capability negotiation, unsupported controls/errors and provider process death | 3 |
| Real inference | Listening corpus and producer voice approval; Windows 10/actual RTX 3060, CPU trial, offline network denial, measured memory/RTF and pinned licensing/artifacts | 3 |
| Durability | 60-minute frozen script with coverage ledger; kill worker/service at claim/write/validation/commit, expired leases, cancel/resume, OOM, truncated audio and disk-full; valid artifacts unchanged | 3 |
| Editing/audio | Source/time mapping, ranged playback, waveform cache reconstruction, non-destructive recipes, selective regeneration, loudness/true-peak/silence/clipping tests and listening | 4 |
| Export | Complete expected segment set, FFprobe and full decode, chapter bounds/order, metadata/cover, hashes and release links; intentional missing/corrupt segment must block release | 5 |
| Android | At least two named/versioned audiobook players; M4B chapters, MP3 playback, seek/resume, artwork and airplane-mode operation on documented Android version/device | 5 |
| Portability/recovery | Consistent live backup (DB+blob manifest), restore into clean location, standalone project history, ID collisions, missing models, traversal/symlink/zip-bomb/schema rejection | 6 |
| Distribution | Clean Windows x64 build/install without dev tools, download/verify/resume models only after consent, offline production, old-library migration, failed update recovery and uninstall preserving user data | 6 |
| LAN/extensions | Pair/revoke, unauthenticated requests rejected, CSRF/TLS/trust, no public bind by default; new engines/presets/mixes do not alter old production snapshots | 7 |

Fixtures use synthetic text/audio or redistributable assets; no production recordings
or model weights in Git. Free unit/integration CI must not require an API key or
GPU. Opt-in real model/GPU tests declare installation prerequisites, sizes, terms,
and test count/outcomes. Skips are not passes. Never weaken assertions to hide defects.

## Phase 0 record — 2026-10-29

- Initial repository contained only a 12-byte README; no app, tests, dependencies or
  project-level instructions. Base commit `6e6e6cdb9876c26300a5873131e748aa3850a64a`.
- `git fsck --full` passed. Read-only `git ls-remote origin refs/heads/main` matched
  the base SHA using existing platform authentication. Default command sandbox could
  not reach the proxy; the supported escalated command succeeded. No token requested.
- Runtime status reported running/connected with enforced restricted HTTP policy and
  no configured user secret/variable/identity bindings. No extra credentials needed.
- Linux x86_64; Python 3.12.14, Node 24.19.0, Git 2.52.0, FFmpeg/FFprobe 7.1.5 available.
  Availability/version inspection only; not application, encoder or compatibility tests.
- Primary GitHub documentation/source retrieval succeeded as listed in research and
  DECISIONS. Hugging Face cards and selected hosted vendor docs returned proxy 403;
  unverified conclusions remain marked. No inference/model downloads or dependencies
  installed. Research response files were kept outside the repository in `/tmp`.
- Documentation verification: relative file links resolve; task IDs unique and
  dependencies valid/acyclic; Next Up contains only unblocked review tasks; required
  documents present; `git diff --check` clean. No application tests exist or ran.
- Phase 0 architecture/task/documentation audit recorded in DECISIONS. User approval
  is pending; Windows/RTX/CPU synthesis, listening, restoration and installers are
  unrun future gates. No readiness claim for the planned application.

The documentation commit is local. No push, release, environment publication, or
model redistribution is implied. The initial onboarding environment required no
project-specific install/start script; Phase 1 will add tested setup instructions.
