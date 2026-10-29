> Historical local-first plan archived at scope reset. Superseded by the current
> root AGENTS.md and docs/TASKS.md. Retained for evidence/history; not active instructions.

# Roadmap

Status: Phases 0–1 approved; Phase 2 manuscripts/history implemented, exit review pending. No date-based
release promises. TASKS owns individual progress; DECISIONS owns approvals. Every
phase exit is a user approval checkpoint before the next phase. Work within a phase
can proceed in coherent batches after approval. Production content is separate.

| Phase / target | Deliverables | Exit evidence |
| --- | --- | --- |
| 0 — design baseline | Repository/environment inspection; requirements/non-goals; current primary TTS research; stack alternatives; component, library/revision/recovery design; operating instructions and dependency-aware tracker | Architecture and prioritized plan documented **and user-approved**. Approved 2026-10-29. |
| 1 — 0.1 foundation preview | Backend/frontend, local startup/config, migrations, central library, multiple projects, safe CRUD, immutable asset storage, stable IDs and tests | Working local multi-project application; browser/API CRUD and restart checks; no inference required. |
| 2 — 0.2 manuscripts preview | TXT/Markdown originals/import, parts/chapters/episodes, editing/autosave, revision snapshots, comparison/restoration, script/audio identities and dictionary infrastructure | Organized manuscripts survive edits, conflicts, restart and safe restoration; snapshot provenance and original preservation verified. |
| 3 — 0.3 narration preview | Approved engine and modular providers, previews/profiles, segmentation, durable queue, cancellation/retry/resume, caching, selective regeneration, checksums, progress and recovery | Producer-approved voice and complete 60-minute generation with interruption recovery on target hardware; no missing segments; CPU/offline checks reported separately. |
| 4 — 0.4 production preview | Synchronized script/audio, segment playback/review, waveforms, timing/silence, selective edits/regeneration, non-destructive recipes, loudness and quality checks | Producer refines an episode without full regeneration; raw audio retained, export timeline reproducible. |
| 5 — 0.5 export preview | MP3, chaptered M4B, metadata, artwork, export presets, FFprobe validation, release history and Android player checks | Downloadable files decode/play offline and chapter/seek/resume tests pass in documented Android players. |
| 6 — 1.0 installable release | Reproducible Windows builds, dependencies, approved first-run model installation, backups, portable archives/import/export, CI/releases, upgrades/restoration | Fresh Windows installation without dev tools, core production offline, tested update/uninstall data preservation and independently restored backups. |
| 7 — later 1.x increments | Additional engines, narrator roles, advanced pacing/pronunciation, archival reading/dialogue, reusable presets, optional ambience, authenticated LAN and optional GitHub integration | Each feature independently tested without weakening core reliability; authenticated Android/tablet access explicitly opted in. |

A preview milestone describes a working slice, not permission to publish an unsafe
installer or uncleared model. Automated focused CI can begin in Phase 1; full
Windows packaging/release CI is Phase 6. Backup design starts now; users must be
warned before real production data is entrusted to previews without verified backups.

## First five implementation tasks after approval

P1-01–P1-05 complete/approved; P2-01–P2-04 implemented; P2-05 review pending. Original dependency order:
P1-01 toolchain/running skeleton;
P1-02 library bootstrap/migrations; P1-03 multi-project CRUD; P1-04 immutable asset
storage; P1-05 integrated persistence/restart validation. Their acceptance criteria
and dependencies are in TASKS. Do not implement all phases in one session.
