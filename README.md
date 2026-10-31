# VoxFoundry

A personal AI-assisted research, writing, worldbuilding, knowledge-library and
lore-atlas studio, with audiobook production planned for a later stage. Initial
projects include Enshrouded: A History of Embervale and original game narratives;
the design remains general-purpose.

**Current priority (2026-10-30): get the Site working and complete first.** The user
removed the Windows audio connection from current work and listed it as a planned
feature. Site sign-in, persistent projects/documents, writing/library/search, sources,
review/canon, supported ChatGPT tools, atlas and portable exports take priority.
Enabled Wiki integration retains explicit approval for remote writes.

The Site must work independently of a Windows companion or a powered-on PC. No
worker pairing, service credential, narration queue, model, FFmpeg or test-tone
playback is required for Site preflight or completion. Real Android Site usability
remains required; Android audio playback/download is part of the deferred feature.

**Status:** no Site is deployed or declared complete. Sites documentation establishes
D1/R2, ChatGPT sign-in and authenticated MCP support; actual hosted behavior, exact
binding/migration setup, costs and real Android use still require verification.
The active preflight and feature order are in [TASKS](docs/TASKS.md) and
[ROADMAP](docs/ROADMAP.md). The scope change does not authorize paid resources,
model downloads, significant installs, public release or unsupported AI APIs.

The first active [Site foundation](sites/studio/README.md) is now implemented locally:
projects/documents, manual version-checked saves, revision history, non-destructive
archive and project JSON export. **19 foundation component tests and ESM validation
passed.** Real sign-in, hosted D1, browser interaction and actual Android remain
unverified; this is not a live Site. The binding format is now confirmed; migration/
lifecycle packaging and account-specific cost applicability remain gates.

## Planned Windows audio connection

[Planned features](docs/PLANNED-FEATURES.md) preserves the Windows job/auth/upload,
local inference/FFmpeg, narration, editing and audiobook export goals for after
Site completion. Existing source and evidence remain available:

- [Direct Sites transport experiment](sites/phase0/README.md): 25 original component
  tests independently reproduced; 29 reviewed component tests passed after fixes.
- [Local transport experiment](docs/POC.md): older component/live-test evidence is
  retained with its original limits.

Neither experiment is the active Site entrypoint. Component test passes do not
prove hosted authentication/D1/R2, Windows execution or actual Android behavior.
Existing `backend`/`frontend` application code, libraries and Git history are preserved;
none is automatically adopted as the hosted Site or migrated by this scope change.

## Documentation

Start with [AGENTS.md](AGENTS.md) and [TASKS](docs/TASKS.md). Current sources of truth:
[requirements](docs/REQUIREMENTS.md), [architecture](docs/ARCHITECTURE.md),
[decisions](docs/DECISIONS.md), [roadmap](docs/ROADMAP.md), [validation](docs/VALIDATION.md),
[planned features](docs/PLANNED-FEATURES.md) and the conditional
[Site foundation prompt](docs/SITES-DEPLOYMENT-PROMPT.md).

Research and historical plans remain in `docs/research` and `docs/archive`. Originals,
revisions, provenance, explicit canon/review decisions and independent Markdown/JSON/
media export and restoration remain requirements. History is not a backup.

Project-owned source remains [Apache 2.0](LICENSE). Third-party dependencies, maps,
references, model weights and voices have independent rights and license terms.
