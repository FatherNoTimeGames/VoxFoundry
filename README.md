# VoxFoundry

A personal AI-assisted research, writing, worldbuilding, knowledge-library, lore-atlas
and audiobook studio. Workflow: **Research → Organize → Co-write → Review → Approve
→ Narrate → Publish**. Initial projects include Enshrouded: A History of Embervale and
original game narratives; the design remains general-purpose.

**Status: revised Phase 0, feasibility incomplete.** The preferred architecture is a
supported ChatGPT Sites experience plus an outbound Windows audio worker. No Site or
Windows companion has been deployed, the exact Sites product/API contract is not yet
identified, and no Windows/Android device is attached. Direct Sites integration and
bridge necessity remain **unverified**. No full-app platform change is approved.

Existing local project/manuscript/revision code and its prior test evidence are
preserved under backend/frontend; they are not a deployed Site or cross-device store.
The former plan is in [the historical archive](docs/archive/local-first-2026-10-29/TASKS.md).

## Available proof-of-concept work

A separate disposable experiment in `backend/voxfoundry/poc` implements a loopback UI,
persistent job queue, portable outbound worker harness, lease fencing/idempotency,
progress and validated stored WAV results. It generates a two-second **tone**, not
speech. It never reads the existing manuscript library or downloads models.

**Verified:** seven component tests for queue durability, auth, retries, duplicate/fenced
completion and worker recovery/cache reuse using a transport double. **Unrun:** actual
HTTP, subprocess/browser playback/download, Sites, Windows, Android and hosted retention.
Automatic permission review rejected execution of the live-test/research commands
because its reviewer was unavailable; no remote request or live test ran.

See [POC instructions and limits](docs/POC.md). The current environment already has the
needed Python dependencies. No new package/model installation is required for the
component tests; do not run the legacy full setup or install significant dependencies
for this Phase 0 without review.

```sh
# Repository cwd; no socket, browser, model or service dependency
.venv/bin/pytest -q tests/poc/test_queue.py tests/poc/test_worker.py
```

The pending real loopback checks are in `tests/poc/test_live.py`, covering phone/tablet/
desktop browser playback/download after the worker exits. Passing those would still
not establish actual Sites/Windows/Android integration. A foreground harness is enough
for the first Windows test; no tray application/installer is assumed to exist yet.

## Product and safety gates

- Preserve supported ChatGPT collaboration and Android-first use. Do not silently
  replace Sites with an ordinary website or paid API chatbot.
- Central projects/files must remain accessible with the PC off. Autosave, sync and
  app-session restoration need distinct tests; external ChatGPT history is not assumed.
- Canon/review approvals and wiki publication are explicit; autosave never approves or
  publishes. Personal use does not waive source, voice, map or model rights.
- Every model download requires separate exact artifacts/sizes/licenses/purposes approval.
  No new hosting costs, significant installs, external deployment or remote publication
  have been authorized.
- Independent Markdown/JSON/media project exports and restoration without the original
  database remain architectural requirements. History is not a backup.

Official documentation hosts were added to an environment configuration **draft**;
review/save settings before retrying after permission review is available. Draft saving
neither grants runtime evidence nor publishes a Site/environment/software release.

## Documentation

Resume with [AGENTS.md](AGENTS.md) and [TASKS](docs/TASKS.md). Current sources of truth:
[requirements](docs/REQUIREMENTS.md), [architecture](docs/ARCHITECTURE.md),
[decisions](docs/DECISIONS.md), [roadmap](docs/ROADMAP.md), [validation](docs/VALIDATION.md).

Research: [references](docs/research/REFERENCES.md),
[Sites/worker](docs/research/sites-worker-integration.md),
[AI integration](docs/research/ai-integration.md),
[mapping](docs/research/map-platforms.md),
[Wiki](docs/research/github-wiki.md), [costs](docs/research/costs.md), and [TTS](docs/research/tts-engines.md).
The final Phase 0 task is a [Sites deployment prompt](docs/SITES-DEPLOYMENT-PROMPT.md);
its current conditional draft is not a verified deployment recipe or deployment approval.

Project-owned source remains [Apache 2.0](LICENSE). Third-party dependencies, weights,
voices, maps and source material have independent terms. No software was pushed or
released by this scope-reset work.
