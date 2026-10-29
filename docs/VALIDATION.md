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

## Phase 1 record — 2026-10-29

- `python scripts/setup.py` reproduced locked Python dependencies and npm install,
  then compiled the TS/React frontend. Repeated execution retained locks and user data.
- TypeScript check + Vite production build passed. Ruff lint and formatting passed;
  frontend Prettier check passed; `npm audit` reported zero vulnerabilities. This audit
  is a point-in-time npm result, not a universal dependency security guarantee.
- **25 tests passed, 0 failed, 0 skipped on Linux**: API CRUD/series/scoping, stale and
  concurrent edits, trash/restore, malformed IDs/input, one-time/invalid bootstrap,
  origin/host/CSRF/session checks incl. Unicode input, upload bounds with/without
  Content-Length, inert attachments and filename handling, dedup, missing/corrupt
  objects, staged/published crash recovery, disk-full/fsync injection, idempotent
  reconciliation, concurrent imports, migration preservation and integrity-checked
  pre-upgrade backup, schema refusal, config precedence, symlink defenses and a
  second-process library lock.
- Real Chromium exercised the compiled UI against a live local server: two independent
  projects, saved description, upload/download with exact byte comparison, project
  isolation, trash/restore, complete service restart, persistence and a 390×844 layout
  without horizontal overflow. No external page requests or browser JS errors observed.
  A separate subprocess test ran the documented headless CLI, checked health/static UI,
  terminated it and verified no launcher token appeared in logs.
- Browser testing found/fixed a description-label selector issue and asset-list clearing
  after same-project save. Request-limit testing found/fixed a chunked-upload error
  status. Multipart normalizes browser Windows paths to basenames; direct domain tests
  reject such paths, and API tests confirm normalized names never become storage paths.
- One upstream Starlette deprecation warns about its httpx test adapter. It is not
  suppressed and does not skip/fail assertions. Future adapter migration can follow
  upstream guidance; no production dependency on httpx was introduced.
- CI defines Ubuntu/Windows jobs with pinned tool versions, full checks and Chromium;
  it has not been pushed or remotely executed. No Windows runner is attached here.
  Windows 10 locks, filesystem durability, browser launch, native wheel compatibility
  and installation are explicitly **unverified**, as are real Android/tablet devices.
- No speech synthesis, backups/project archives, installer, software publication, paid
  services or model downloads occurred. Full independent project transfer/recovery is
  still a required later acceptance gate. Phase 1 is submitted for user exit review;
  Phase 2 is blocked pending that approval.

Cloud configuration: `install_script` and `start_skill` draft persistence confirmed.
The equivalent install script and startup/health/browser workflow were executed here.
Saving did not execute them, publish a snapshot, or validate restoration in a fresh
cloud task. No application release was created.
