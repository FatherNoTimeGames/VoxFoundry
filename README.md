# VoxFoundry

A planned free, local-first AI audiobook production studio for Windows. One library
will hold independent books and series, manuscripts, research, narration, production
history, and releases. The first production is **Enshrouded: A History of Embervale**;
the application will remain reusable for other projects.

**Status: Phase 0 design and research complete; awaiting user approval. There is no
application to install or run yet.** No models or application dependencies have been
installed. Do not interpret proposed commands or architecture as working features.

Core workflows will operate offline without paid APIs, subscriptions, or accounts.
The proposed stack is Python/FastAPI, React/TypeScript, SQLite, filesystem assets,
isolated interchangeable TTS workers, and FFmpeg/FFprobe. Windows installer and
GitHub Releases distribution are planned. Localhost is the default; authenticated
LAN access is a later optional feature.

## Development and usage

Use the existing checkout. For this documentation-only phase, Git and a text editor
are sufficient. Read [AGENTS.md](AGENTS.md) and [the task tracker](docs/TASKS.md) to
resume. No Python/Node installation or model download is needed to review the plan.
Verified in the current Linux cloud environment: Git repository integrity, clean
initial checkout, authenticated read access to GitHub, and availability of Python
3.12.14, Node 24.19.0, FFmpeg/FFprobe 7.1.5. These are observations, not pinned release
requirements. Windows, CUDA, speech quality, and installation have not been tested.

After Phase 0 approval, the first batch will pin a compatible toolchain and create a
small running application. Setup and usage commands will be documented when tested.
No GitHub account will be needed by end users for local production.

## Design documents

- [Requirements and non-goals](docs/REQUIREMENTS.md)
- [Architecture and data model](docs/ARCHITECTURE.md)
- [Decisions, approval questions, and audits](docs/DECISIONS.md)
- [Roadmap and release gates](docs/ROADMAP.md)
- [Tasks and next work](docs/TASKS.md)
- [Local narration engine research](docs/research/tts-engines.md)
- [Validation strategy](docs/VALIDATION.md)

Project-owned source is licensed under [Apache 2.0](LICENSE). Third-party dependencies,
models and voices retain their own terms. Default models/voices must permit commercial
audiobook production. Distribution and model downloads require separate authorization.
