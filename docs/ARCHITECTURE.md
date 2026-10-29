# Architecture

Status: complete system design proposal; no implementation. Approval gate: P0-06.
See DECISIONS for alternatives, REQUIREMENTS for scope, VALIDATION for proof gates.

## Runtime and boundaries

A modular monolith keeps application logic and persistence simple. Inference runs
outside the API process so GPU failures and incompatible model dependencies cannot
kill editing or corrupt library transactions.

```text
Desktop browser (later authenticated LAN browser)
  ↕ same-origin HTTP JSON; SSE for progress; ranged audio reads
Python FastAPI service + packaged static frontend
  ├─ application services: projects, revisions, planning, jobs, exports, backups
  ├─ domain: identity, hierarchy, snapshots, dependency rules, state transitions
  ├─ storage adapters: SQLite/SQLAlchemy + migrations; immutable file objects
  ├─ supervisor ↔ isolated provider worker (private framed JSON/pipe protocol)
  └─ processing adapter ↔ FFmpeg / FFprobe subprocesses
```

React/TypeScript/Vite provides a compiled local UI; Node is a development/build
requirement only. API schemas generate frontend types when the contract stabilizes.
UI contains no authoritative invalidation or persistence rules. FastAPI handlers
validate requests, call application services, and translate errors. Domain logic
has no web, ORM, or PyTorch dependency. Workers never write SQLite or choose library
paths; the supervisor validates their output and commits results. No Redis, Celery,
Docker, or separate database server. A single library instance lock prevents two
service processes opening the same library for writes; HTTP requests are serialized
at transactional boundaries, not across long inference operations.

Future directories: `backend/` with api/application/domain/storage/providers/processing;
`frontend/`; `tests/` with unit/integration/fixtures; `scripts/` for real build/dev tools;
`.github/workflows/` for CI/releases. Create these only when implementing relevant work.

## Local configuration and storage

Use a platform-specific per-user config path (Windows `%LOCALAPPDATA%/VoxFoundry/`).
An explicit library picker/config selects a writable local path outside the app's
installation. Multiple projects live in one selected library; multiple concurrent
library mounts are deferred. Defaults are documented and relocatable in Phase 1.

```text
<library>/
  library.sqlite3                  # mutable relational metadata
  objects/sha256/<prefix>/<digest>  # immutable manuscript, research, audio, artwork
  staging/<operation-id>/          # incomplete writes, never advertised as valid
  exports/<release-id>/            # validated deliverables, immutable once released
  logs/                            # bounded, redacted diagnostic files
<app-data>/models/<provider>/<revision>/  # shared verified models, outside library
<app-data>/workers/<provider>/<version>/  # isolated runtime environments
<backup-destination>/             # separate user-selected location, not history
```

All library references use object IDs/digests and safe relative paths, never arbitrary
client paths. Models/presets can be shared across projects; reference recordings are
project assets unless explicitly shared. Content-addressed objects deduplicate bytes;
project ownership/references still govern deletion/export. Originals are immutable.
Caches may be cleaned only if unreferenced; no automatic deletion of history/release
assets. Retention/garbage collection starts with dry-run reachability and explicit
confirmation, including staging recovery. Network/sync folders are unsupported for
live SQLite, though closed archives/backups may be copied there.

## Conceptual relational model

UUIDs assigned by the application are stable, globally unique identities; names and
positions are mutable metadata. Hashes identify bytes, never replace entity IDs.
UTC timestamps aid display/auditing; monotonic revision numbers and optimistic
concurrency tokens order changes. Foreign keys include project scope to prevent
accidental cross-project links. Exact DDL belongs to Phase 1/2 migrations.

| Entity | Relationships and invariants |
| --- | --- |
| Library / SchemaMigration | Library identity, format/schema versions; one local owner |
| Series / Project | Optional series groups independent projects; project owns history and lifecycle (active/trashed) |
| DocumentNode | Project-scoped parent, type (part/chapter/episode/manuscript/research/reference/note), stable ID and ordering; no cycles |
| Asset / Blob | Project ownership, original name/media type, SHA-256, byte length; many asset records may reference identical immutable bytes |
| DocumentRevision | Node, immutable UTF-8 text blob, parent revision, author/time/reason; drafts are mutable and separately identified |
| ProjectSnapshot | Immutable manifest: exact node tree/order, document revision IDs, metadata and settings versions; project head points at one snapshot |
| PresetVersion / ProjectOverrideVersion | Immutable shared preset and frozen resolved project settings; editing defaults never mutates historical configurations |
| VoiceProfileVersion / DictionaryVersion | Provider/voice/model identity, reference-asset digest, language/control schema; pronunciation entries and scope |
| ScriptSegment / SegmentVersion | Stable logical segment ID; version binds document revision, source spans, normalized text and context fingerprint; split/merge lineage explicit |
| NarrationPlan / PlanEntry | Frozen ordered segment versions plus effective settings; expected complete set for a production run |
| Job / JobItem / Attempt | Persistent state, lease, priority, retry/diagnostics; item targets one immutable segment/config; attempts append-only |
| AudioArtifact | Segment version, resolved config/model/runtime fingerprints, digest, media properties, validation result, producing attempt |
| EditRecipeVersion / ProductionSnapshot | Non-destructive trim/silence/gain/fade/ordering instructions referencing immutable audio and timing map |
| Export / Release | Exact production snapshot, format/settings, ordered chapter manifest, cover/metadata, FFprobe report, checksum and immutable release record |
| OperationJournal / AuditEvent | Pending filesystem/DB operation reconciliation; append-only production and restoration events |

Series organization does not merge project histories. Research sources retain URLs,
retrieval dates and attached originals when supplied; the app does not scrape them
by default. References from manuscripts to research use IDs, not file names.

## Drafts, revisions, comparisons, restoration

Autosave writes a draft with an expected version token and a visible saved indicator;
conflicts return the current version instead of overwriting. A revision command
freezes draft text into an immutable document revision and advances its head within
a transaction. Named project snapshots capture tree, manuscripts, research references,
settings and metadata together. Production always uses a frozen snapshot, never a
moving draft. Compare text diffs plus structural/settings/asset changes.

Restore previews changes and creates a new snapshot referencing earlier immutable
content. It preserves the current snapshot and later outputs; it never rewinds by
overwriting files. Trashing projects is reversible; physical purge is separate and
approval-gated. No branch/merge UI, rebase, or Git object graph. Histories belong to
the project, so standalone archives include all referenced revisions unless the user
explicitly chooses a limited release-only package with its omissions declared.

## Segmentation and selective invalidation

Segmentation is versioned, sentence/paragraph aware, bounded by provider limits, and
retains exact source offsets plus paragraph/heading IDs. Reconcile stable IDs within
a document using matching text/context; ambiguous repeated text receives new IDs.
Offsets alone cannot identify a segment after upstream edits. Split/merge creates
new segment IDs with lineage. Segment-level synchronization is guaranteed initially;
word alignment is a separate optional capability, never inferred from duration.

A synthesis key hashes a canonical, versioned record of normalized spoken text,
normalizer/segmenter version, relevant context, language, provider/API version,
model+voice digests, resolved controls, reference audio digest, effective applicable
pronunciations, requested seed and output format. Record runtime/device precision
fingerprints; reproducibility means traceability, not guaranteed identical GPU bytes.
Audio artifacts remain immutable even when two attempts share a request key.

- Editing a sentence invalidates that segment and context-dependent neighbors only.
- A pronunciation change affects segments using its entries. Include matched rule
  results, not the global dictionary timestamp, in the synthesis key.
- Voice/model/pacing changes invalidate affected profile assignments. Updating a
  shared preset offers explicit adoption; existing resolved versions stay frozen.
- Metadata or cover changes invalidate export only. Chapter reorder reuses audio
  and rebuilds timeline/export. Trim/silence/mastering changes rebuild production,
  preserving synthesis. Changing boundary context can require adjacent regeneration.

Invalidation marks derived views stale; it never deletes older valid artifacts.
Users see current, stale, missing, and failed separately. A job finishes for its
original frozen plan even if the manuscript changes; its outputs cannot silently
become the current edition. Export requires every expected segment from the selected
production snapshot, with no implicit substitution or omission.

## Durable jobs and worker contract

SQLite is the queue source of truth. Job/items transition through queued → leased /
running → validating → succeeded, with failed, cancel-requested/cancelled and retry
paths. Claim transactionally with a lease, heartbeat, bounded retries and backoff.
A crashed worker's expired lease is reconciled before requeueing. Cancellation stops
new claims, signals the worker, then terminates it after a grace period; validated
completed items survive. Resume claims unfinished work, not the entire manuscript.

Provider v1 contract: describe capabilities/limits and licenses; list local installed
models/voices; validate configuration; prepare local resources; synthesize bounded
text into a supervisor-provided staging location; emit typed progress/errors; cancel;
close. Unsupported pace/phoneme/cloning controls are reported rather than ignored.
Protocol has version, attempt ID, input fingerprint, size limits, timeout and a final
result with PCM format/sample count and digest. Treat worker output as untrusted.
No implicit downloads during prepare/synthesis. Model installation is a separate
user-approved action with manifest, download sizes, license, revision and checksums.

One inference worker on the GPU by default; no assumed VRAM capacity. Workers have
separate pinned Python environments/processes to avoid torch/dependency collisions.
CPU use is explicit and recorded; OOM offers smaller batches/CPU or retry without
silently changing voice. Transport uses private inherited pipes, not an unauthenticated
public inference port. Segment duration bounds limit lost work and memory use.

## Filesystem consistency, recovery and migrations

Write files to staging on the same volume, flush and verify length/digest/media,
then atomically rename to immutable object path before committing references in a
short SQLite transaction. A journal connects operation ID, expected digest and DB
state. A crash can leave an orphan file, never a successful reference to a partial
file. Startup reconciliation verifies interrupted operations; quarantines corrupt
objects and marks missing references, retaining diagnostics. External deletion and
disk-full must surface actionable errors. Do not hold DB locks while encoding.

Enable foreign keys, use bounded busy timeouts, WAL on supported local storage and
durable transaction settings; test Windows rename/locking/fsync behavior. Alembic
migrations are versioned, forward only, with preflight disk space and verified backup.
Newer schemas refuse to open in older apps. Upgrade failures leave a recoverable
backup; never assume a reverse migration is safe. Startup runs consistency checks
appropriate to crash state; full checks are available explicitly.

Backups use SQLite's consistent online backup mechanism plus a frozen reachability
manifest of immutable objects, verified hashes and a completion marker. A copied
live DB without WAL is not a backup. Restore into a new location, verify all objects,
schema and references, then offer explicit switch; never overwrite the only library.
Project export uses versioned manifest+portable records+referenced blobs; import
stages and validates schema, checksums, path traversal, symlinks, decompression and
size limits. Imports default to a new project, remapping IDs and recording provenance
on collision; do not merge unrelated histories. Models are excluded by default;
manifest reports required engine/model revisions and their separate installation.

## Audio production and exports

Retain original engine PCM/sample rate; processing recipes declare resampling/channel
conversion, trim, silence, gain, fades and mastering versions. Production snapshots
freeze timeline and cumulative segment/chapter offsets. Waveform caches derive from
PCM and can be rebuilt. Loudness analysis and two-pass normalization use explicit
presets/true-peak limits; avoid repeated lossy encode cycles. Quality checks flag
clipping, suspicious silence, truncated/empty output and duration anomalies; they do
not prove correct speech. Listening and optional ASR checks complement them.

FFmpeg is invoked with argument arrays, bounded output/timeouts and generated safe
manifests, never shell interpolation from manuscript metadata. Produce per-chapter
or single MP3 and chaptered AAC-in-MP4 M4B with metadata/artwork. Stage output and
FFprobe validation before marking an export/release successful. Check decodeability,
stream formats, positive duration, ordered chapters within duration, metadata/cover,
expected segment coverage and checksums. Android seek/resume/chapter behavior needs
real player tests. Defaults for loudness/bitrate are approved through listening tests,
not hard-coded as universal audiobook requirements.

## Security, distribution and evolution

Bind loopback by default, check Host/Origin, disallow permissive CORS, require a local
session bootstrap and CSRF protection for mutations, and validate Web/SSE sessions.
Use a browser-opening one-time bootstrap without persistent secrets in logs. Assets
are served by scoped IDs with range support; HTML/raw research cannot execute in the
app origin. Reject active content and unsafe filesystem names, including Windows
reserved names, junction/symlink escapes and archive traversal.

LAN (Phase 7) is explicit opt-in with device pairing, authenticated sessions, CSRF,
TLS/pinned local trust guidance, revocation, firewall guidance and restricted routes;
no public exposure/port forwarding. Android is a browser client; inference stays on
the host. No unauthenticated network access during early development.

Propose PyInstaller one-folder Python bundle + compiled web assets, then a Windows
installer (candidate Inno Setup; exact tool/license unresolved). Keep provider runtimes
and approved models separately installable, versioned and checksummed. Updates are
user-triggered downloads from GitHub Releases; signed-manifest/checksum policy must
be designed before auto-apply. Unsigned hashes alone do not authenticate an update.
No paid signing service is mandatory. Stop running workers before updating binaries;
back up before migrations; uninstall preserves libraries/models unless explicitly
chosen otherwise. A native shell (Tauri/pywebview) can follow only if browser UX proves
insufficient. Compatibility, installer license and Windows security limitations
remain release gates; Linux development is not packaging evidence.
