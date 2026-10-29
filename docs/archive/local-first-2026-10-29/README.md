> Historical local-first plan archived at scope reset. Superseded by the current
> root AGENTS.md and docs/TASKS.md. Retained for evidence/history; not active instructions.

# VoxFoundry

A free, local-first AI audiobook production studio for commercial and noncommercial
productions. The first production is **Enshrouded: A History of Embervale**; the core
remains reusable for other projects.

**Status: Phase 2 manuscripts and history implemented; phase-exit review pending.**
This development preview manages projects/series, original assets, manuscript hierarchy,
autosaved text, immutable revisions, comparisons, safe restoration, project snapshots
and pronunciation presets. There is no installed narration engine, audio editor,
audiobook exporter, standalone project archive/backup UI, installer or updater yet.
Keep originals and independent backups; history does not replace them.


Core workflows require no account, paid API, subscription, Docker or cloud service.
The compiled responsive UI and local Python service run without Internet access after
explicit development dependency installation. Android/tablet browser support remains
an architectural requirement; authenticated LAN access arrives in Phase 7. This
preview binds only to loopback.

## Development setup

Use the existing checkout; do not create a worktree unless explicitly requested.
Tested on Linux x86_64 with Python **3.12.14**, Node **24.19.0**, npm **11.9.0**, and
uv **0.12.23**. Python/Node versions are recorded in `.python-version`/`.node-version`;
Python and npm dependencies are exactly pinned with transitive lockfiles. Install
these tools through their official distribution channels, then from the repository:

```sh
python scripts/setup.py
```

This executes `uv sync --locked`, `npm ci --prefix frontend`, and
`npm run build --prefix frontend`. Re-running refreshes dependencies and the compiled
UI without changing locks or user libraries. No AI models are installed. The frontend
is served by the backend; no separate Vite development server or permissive CORS is
needed. Node is not used at application runtime. Cloud sandboxes with read-only home
caches can set `UV_CACHE_DIR=/tmp/voxfoundry-uv` before setup.

## Run locally

Choose an **absolute local library path outside the checkout/installation**:

```sh
# Linux example
uv run --locked voxfoundry --library /home/you/VoxFoundryLibrary
```

```powershell
# Windows PowerShell example (not yet verified on Windows)
uv run --locked voxfoundry --library "$env:LOCALAPPDATA\VoxFoundry\Library"
```

The launcher opens your browser with a one-time session bootstrap, removes the token
from browser history, and does not log it. Existing tabs reconnect within the same
browser session; after a server restart use the newly opened launcher tab. Stop with
Ctrl+C. Libraries and assets remain on disk. Reopen with the same library path to
continue. A second process opening the same library is rejected.

For a headless service use `--no-browser` (public health check only until an authenticated
session is established through a launcher). Choose `--port` to change the default
8765. `/api/health` is the only unauthenticated health capability; library/project/
asset access requires a session, and writes require same-origin CSRF protection.
The launcher token must never be pasted into logs, issues or chat.

Location precedence: `--library`, then `VOXFOUNDRY_LIBRARY`, then a non-secret
`{"library": "/absolute/path"}` in `config.json` under the platform user config
folder (`%LOCALAPPDATA%\VoxFoundry` on Windows; platformdirs' user config directory
on Linux), then the platform user-data `VoxFoundry/Library` default. No path picker
is implemented yet. Live SQLite libraries must reside on a local disk, not a network
share or a live sync folder. Close the service before manually moving a complete
library directory, preserve the original, then select the new absolute path.

## Use projects and original assets

Create a project, select it, edit its name/description, optionally create and assign
a series, then save. Updates carry a version token; a conflict preserves your local
input and asks you to reload rather than overwriting another edit. Unsaved-change
prompts protect switching away. Trash is reversible and retains assets; no permanent
delete operation exists.

Store original assets (25 MiB per file in Phase 1). The app copies and hashes bytes,
deduplicates storage, and keeps independent project references. Downloads are inert
attachments; HTML/research is never rendered as executable app content. Interrupted
imports retain partial staging with visible diagnostics. Retry by uploading the
original again after addressing disk/permission problems. Missing/corrupt objects
are flagged and downloads fail rather than delivering unverified bytes. Do not
manually modify object files. No automatic cleanup/purge is performed.

## Manuscripts, revisions and snapshots

Select a project and expand **Add or import document**. Create parts, chapters,
episodes, manuscripts, research, references or notes. Import `.txt`, `.md` or
`.markdown` as UTF-8 (optional BOM) or BOM-marked UTF-16. The original bytes remain
an asset; editable text normalizes line endings to LF. Invalid encodings, binary
control characters and oversized inputs produce errors without changing originals.
The preview limits text to 1 MiB/2000 paragraphs per document, 1000 total nodes per
project, and 8 MiB of active text for project snapshot/comparison operations.

The tree has stable identities. **Structure and research references** changes titles,
parents, ordering and source links; cycles and links to other projects are rejected.
Structure changes require **Save structure**. Text autosaves after a short idle period;
watch **Draft saved locally** before leaving. Concurrent saves are serialized. A stale
tab retains its local text and stops autosaving after a conflict. Copy that text,
resolve against the current version and reload deliberately; never assume a failed
save succeeded. **Save draft now** retries; switching projects is blocked while a draft
or structure edit needs attention. Closing the page prompts for unsaved changes.

**Freeze revision** creates immutable history of the saved text. Compare a selected
revision to the current saved draft, then explicitly restore it. Restoration first
preserves any newer saved text and appends a new revision; it never rewrites the
selected historical revision. Unchanged text reuses its existing immutable revision.
Markdown is edited as inert text, not rendered as executable HTML.

**Project snapshots** freezes current drafts, tree/order, research links, metadata,
resolved settings and asset references under a name. Preview restoration before
confirming it. Stale previews are rejected if another edit occurred. Restoring creates
a **Before snapshot restore** snapshot of later saved work, appends restored revisions
and a new snapshot, and hides later nodes from the active tree. Those nodes and their
revisions remain reachable through history. Newer asset originals remain available;
no restore operation purges them. Missing/corrupt referenced objects stop the operation.

**Pronunciation dictionary and presets** supports case-sensitive literal terms with
whole-project/document scopes. Document rules override project rules, which override
a selected shared preset version. Replacements do not cascade or modify manuscript
text. Preview a **frozen** script to inspect spoken replacements; no speech is generated.
New shared preset versions do not alter projects pinned to earlier versions. Settings
changes retain version history and snapshots capture resolved values. Language/pace
intentions are stored in the configuration API; actual engine control support is Phase 3.

Snapshots still depend on this library's immutable objects. Independent project
archives/backup/transfer into a fresh library without the original DB remain required
Phase 6 capabilities. No AI model downloads are authorized by using this preview.

## Verify

After setup:

```sh
uv run --locked ruff check backend tests scripts
uv run --locked ruff format --check backend tests scripts
npm run format:check --prefix frontend
npm run build --prefix frontend
uv run --locked pytest -q -o faulthandler_timeout=30
```

Browser tests require Chromium: the suite uses an existing `chromium` executable or
Playwright's browser install. If absent, run `uv run --locked playwright install
--with-deps chromium` explicitly (a browser download, not an AI model). CI defines
Linux and Windows jobs; it has not been run remotely in this session. Current local
result: **42 passed**, no skips; real compiled-UI/restart tests included. One upstream
Starlette warning deprecates its httpx test adapter; assertions still execute. Windows
10, GPU, Android devices, installers, backups and speech quality are **not verified**.
See [validation evidence](VALIDATION.md) for limits and failure-injection coverage.

## Documentation and license

Start with [AGENTS.md](OPERATING-INSTRUCTIONS.md) and [TASKS](TASKS.md) when resuming development.
Authoritative specifications: [requirements](REQUIREMENTS.md),
[architecture](ARCHITECTURE.md), [decisions/approvals](DECISIONS.md),
[roadmap](ROADMAP.md), and [TTS research](../../research/tts-engines.md).

Project-owned source is [Apache 2.0](../../../LICENSE). Dependencies, models and voices retain
separate terms. Default models/voices must permit commercial production; producers
must hold appropriate source-material/reference-voice rights. Every AI model download
requires separate approval of exact artifacts, sizes, licenses and purposes. Paid
services and software distribution are not authorized by the Phase 1 approval.
