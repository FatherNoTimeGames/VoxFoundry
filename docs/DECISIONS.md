# Decisions and approval register

2026-10-29. D01–D07 and the prioritized plan are user-approved. D06 remains
provisional until packaging validation. Phase 1 is authorized; subsequent phase
exits retain their review gates. Silence never supplies approval.

## D01 — Modular Python service and responsive local web UI

Recommend FastAPI/Pydantic, SQLAlchemy 2 + Alembic, and React/TypeScript/Vite, served
as same-origin static assets in production. Separate domain/application/storage and
external inference workers. Python fits the local ML ecosystem; web UI fits desktop
and optional Android without a second client. Typed validation and explicit jobs
avoid in-process long-running inference. Dependency versions will be pinned and
compatibility-tested in P1-01, not copied from upstream moving examples.

Alternatives: Flask is smaller but needs more contract/validation assembly; Django
provides excellent CRUD/migrations/admin but brings a larger web/auth model than this
single-user library needs. PySide6 offers native dialogs/audio but adds a second UI
for Android and Qt licensing/deployment work. Tauri reduces shell footprint relative
to Electron but adds Rust/WebView2/Python-sidecar lifecycle concerns. Electron offers
mature desktop APIs but bundles Chromium/Node and increases memory/update surface.
Start with browser UI; revisit a shell if filesystem integration/UX justifies it.
React costs a JS toolchain; plain HTML/HTMX is simpler for forms but less natural for
waveform/timeline state and synchronized editing. No frontend runtime requires Node
in installed end-user application.

## D02 — SQLite plus immutable filesystem objects

One central SQLite library with independent project histories and optional series.
Use relational constraints/migrations and content-addressed local assets. PostgreSQL
is unnecessary server administration; JSON-folder-only storage complicates atomic
relations and queries; one DB per project simplifies portable copying but makes
central search/shared state and migrations harder. Central DB increases backup blast
radius: mitigate with verified independent project archives and whole-library backups.
Do not use a live SQLite DB on a network share. Keep all user data outside installer.

## D03 — Production-specific history rather than Git

Drafts + immutable document revisions + project snapshots + production/release
manifests. Restore by creating new heads; never erase newer work. Git is excellent
for code but binary audio, nontechnical workflow and app-level dependency tracking
would still require substantial additional design. Do not build branch/merge/DVCS.
GitHub remains optional integration; releases of app code and audiobook releases
are distinct concepts. History and backups solve different failure modes.

## D04 — Isolated, interchangeable local inference

A provider protocol advertises capabilities, accepts frozen bounded inputs, returns
validated staged audio and typed errors. Separate pinned environments/processes isolate
PyTorch conflicts and OOM. Durable SQLite jobs, leases and content fingerprints make
retries and selective regeneration explicit. Alternatives: in-process inference is
simpler initially but couples crashes/dependencies; Celery/Redis increases deployment
burden; network microservices add auth/ports without local product benefit.

Kokoro is initial adapter candidate, **not a production-quality verdict**. Chatterbox
original/Turbo are listening alternatives. Piper is a licensing-gated CPU option.
F5 and XTTS weights require intended-use review. No model download authorized; exact
artifact/size/license approval is a separate P3 gate. See TTS research for evidence.

## D05 — Non-destructive audio and FFmpeg subprocesses

Keep raw PCM and versioned edit/mastering recipes. Use FFmpeg/FFprobe for encoding,
metadata, chapters and validation. Direct libav bindings complicate native packaging;
a full custom DSP/codec stack duplicates mature work. Subprocess arguments and safe
manifests reduce command injection. FFmpeg binary configuration determines LGPL/GPL
obligations; no `--enable-nonfree` redistributable binary. Phase 0 host FFmpeg includes
GPL features and is not approved as the Windows redistribution build.

## D06 — Distribution plan, not yet finalized installer

Prefer PyInstaller one-folder + compiled static UI, user-selected library, independently
installed provider runtimes/models and user-triggered GitHub Release updates. One-file
bundling adds extraction/startup/antivirus friction for large ML dependencies. Nuitka
may improve selected packaging properties but adds compilation complexity; embedded
Python is transparent but requires owning interpreter/dependency layout. PyInstaller
bootloader exception is documented; dependencies retain their own licenses.

Evaluate Inno Setup versus WiX/MSIX at P6-01, including current license/use terms,
unattended build reproducibility, Windows 10, signing and update rollback. The retrieved Inno license permits commercial use with notice, origin and
modification conditions; verify the exact distributed release and retain its notices. WiX/MSIX may improve enterprise packaging but increase toolchain
and signing/deployment complexity. No installer selected solely from historical
reputation. Signing/SmartScreen trust without mandatory paid services is unresolved.

## D07 — Security and platform policy

Loopback-only, same-origin UI, Host/Origin validation and local session protection.
Authenticated LAN with explicit pairing/trust is Phase 7, not an early convenience
flag. Preserve Windows 10 target; verify a supported dependency matrix and document
OS lifecycle risks. Switching the target or requiring paid signing/hosting needs user
input. Do not silently promise current Windows 10 security support. Official lifecycle
page could not be retrieved through this environment, so exact support exceptions
must be verified before distribution.

## Approval questions and consequences

| ID | Decision requested | Recommendation / impact |
| --- | --- | --- |
| A01 | Approved 2026-10-29 | D01–D07/plan accepted; D06 provisional; Phase 1 authorized, not model downloads or distribution. |
| A02 | Apache-2.0 selected 2026-10-29 | LICENSE added for project-owned code; third-party obligations remain; no distribution authorization. |
| A03 | Which exact models/voices may be downloaded for listening tests? | Defer until P3-01 provides artifact sizes, terms and purpose. Prefer Kokoro plus Chatterbox comparison. No request for blanket permission now. |
| A04 | Resolved 2026-10-29 | Commercial and noncommercial productions required; defaults must allow commercial use; appropriate rights required for all reference voices/source material. |

Open technical validation: actual RTX 3060 variant/VRAM and driver; supported Windows
10 build/toolchain; measured narration quality/CPU RTF; packaged offline dependency
set; signing/update trust and installer terms. These do not block documentation or
Phase 1 design approval, but cannot be represented as validated capabilities.

## Primary stack references (retrieved 2026-10-29)

- [FastAPI README](https://github.com/fastapi/fastapi/blob/master/README.md): Python API framework and type-based validation.
- [SQLAlchemy](https://github.com/sqlalchemy/sqlalchemy/blob/main/README.rst), [Alembic](https://github.com/sqlalchemy/alembic/blob/main/README.rst): relational persistence and migrations.
- [SQLite upstream](https://github.com/sqlite/sqlite/blob/master/README.md): embedded storage project. Detailed crash/backup settings still require implementation-time documentation/tests.
- [Vite React TS template](https://github.com/vitejs/vite/blob/main/packages/create-vite/template-react-ts/package.json): build approach; moving versions are not project pins.
- [PySide LGPL text](https://github.com/qtproject/pyside-pyside-setup/blob/dev/LICENSES/LGPL-3.0-only.txt): one licensing path, not full Qt module clearance.
- [FFmpeg license](https://github.com/FFmpeg/FFmpeg/blob/master/LICENSE.md): optional features alter binary license.
- [PyInstaller terms](https://github.com/pyinstaller/pyinstaller/blob/develop/COPYING.txt): bootloader exception.
- [Inno Setup terms](https://github.com/jrsoftware/issrc/blob/main/license.txt): current conditions require packaging-stage review.

Qt hosted licensing page, FFmpeg hosted legal page, and Microsoft Windows 10 lifecycle
page returned proxy 403. Relevant GitHub primary license texts were used where available;
Windows lifecycle remains explicitly unverified. Architecture comparisons are engineering
judgments, not performance measurements.

## Audit and approval log

- Last audit: 2026-10-29, Phase 0 boundary, documentation commit following initial
  `6e6e6cd`. Reviewed requirements coverage, component/data boundaries, recovery,
  license/download gates, task dependencies and documentation consistency. No app tests
  exist. Approval pending; all later-phase work blocked by P0-06.
- Audit cadence: next audit after ten further development commits from the Phase 0
  documentation commit, or Phase 1 boundary, whichever comes first. Determine the
  count with `git log` at resume time.
- 2026-10-29 user approval: D01–D07 and the prioritized implementation plan approved;
  D06 provisional pending packaging validation. Phase 1 authorized autonomously through
  its established checkpoint. Project-owned source is Apache-2.0 (LICENSE).
- Clarifications: commercial AND noncommercial audiobook production are required;
  default models/voices must support commercial use and producers must hold appropriate
  rights to source material and reference voices. No model download without separate
  approval of exact artifacts, sizes, licenses and purposes. No paid services or software
  distribution authorized. Keep interchangeable providers, non-destructive editing,
  local-first operation and all existing safety constraints.
- Portability is a hard architecture requirement: each project must be independently
  exported, backed up, restored and transferred into a fresh library without the
  original library database. Archives must embed all project records/history and
  referenced assets, resolved shared presets/series context and required model manifests.
  A library-relative manifest alone cannot pass P6-02.
- Responsive Android/tablet browser access remains required; authenticated LAN is still
  Phase 7. No desktop-only API or UI assumption may prevent that future client.
- A01/A02/A04 resolved by this approval (Apache-2.0 and commercial-compatible defaults).
  A03 remains a separate future per-artifact approval; no downloads authorized.

## Phase 1 implementation and audit (2026-10-29)

- D01 baseline now implemented with Python 3.12.14, uv 0.12.23, FastAPI 0.162.0,
  SQLAlchemy 2.1.6/Alembic 1.20.1, React 19.3.1/TypeScript 7.0.2/Vite 8.3.5 and
  Node 24.19.0. Exact transitive versions are in uv.lock/frontend/package-lock.json.
  These are development pins verified on Linux, not a Windows 10 support claim.
- Chose filelock for the OS-backed single-owner library lock, platformdirs for user
  locations, and a compiled same-origin UI rather than an extra frontend dev service.
  Bounded upload is 25 MiB for the foundation; raise only with streamed resource tests.
  Session bootstrap is one-time and local; no unauthenticated library routes.
- Asset recovery conservatively retains failed staging and corrupt objects. There is
  no cleanup/purge or automatic replacement. SQLite migration backup is metadata-only;
  full independent project/library recovery remains P6-02 and is not advertised yet.
- Last audit: Phase 1 boundary, after `1deb001` and foundation implementation `9eff8e1`.
  Reviewed module boundaries, project ownership/portability invariants, immutable object
  handling, security/session limits, failure injection, dependencies and docs/tasks.
  25 local tests passed including real browser and launcher checks; Windows 10, Android
  devices, remote CI and power-loss behavior remain unrun. No models/inference packages
  or production source material downloaded. No paid services or distribution performed.
- Next audit: Phase 2 boundary or ten further development commits from the Phase 1
  audit documentation commit, whichever is earlier (count through Git log).
- Phase 1 exit: **review pending (P1-05)**. Implementation P1-01–P1-04 complete; user
  approval required before Phase 2. No new architecture choice needs a separate gate.

- Cloud environment draft saved successfully with `install_script` and `start_skill`.
  Install repeats `scripts/setup.py`; startup documents existing checkout, isolated
  library location, session/health/browser testing and phase/model/distribution gates.
  No environment snapshot has been published. Review/save in environment settings
  then publish the cloud environment to retain the snapshot; this is separate from
  application software distribution, which remains unauthorized.
