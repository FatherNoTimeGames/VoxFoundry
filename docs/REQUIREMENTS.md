# Product requirements

Status: approved baseline, 2026-10-29. Clarifications recorded in DECISIONS.

## Mission and scope

VoxFoundry is a local audiobook production studio, not a game-specific tool or a
hosted speech service. The first production, Enshrouded: A History of Embervale,
exercises reusable documentary narration, fantasy names, research references, and
chapter organization. Content and voice-reference rights remain the producer's
responsibility; no game assets or manuscript are included in this repository.

| ID | Required outcome | Delivery phase |
| --- | --- | --- |
| R01 | Central library of independent books/series with parts, chapters, episodes, research, references, notes, and assets | 1–2 |
| R02 | Autosave, immutable revisions, comparisons, snapshots, safe restoration, independent project history and releases without Git | 2 |
| R03 | Interchangeable local TTS, voices/profiles, pronunciation, pace, project overrides, shared models/presets | 3, extended 7 |
| R04 | Durable queues, retry/cancel/resume, selective regeneration, caching, provenance and visible errors; 60-minute recovery validation | 3 |
| R05 | Script/audio navigation, segment playback/waveforms, timing, silence, non-destructive edits, mastering | 4 |
| R06 | MP3 and chaptered M4B, metadata/artwork, export validation and immutable release history | 5 |
| R07 | Independent backups/restoration, portable project archives/import/export, optional GitHub integration | 6, integration 7 |
| R08 | Responsive desktop browser UI; optional authenticated Android/tablet LAN control | 1, LAN 7 |
| R09 | Windows installer, model installation, updates through GitHub Releases preserving data | 6 |
| R10 | Offline core with no subscription, paid API, account, hosted infrastructure, mandatory Docker, or telemetry | all |

## Quality constraints

- Narration quality outranks peak throughput. Listening approval precedes production
  engine selection. Quality includes correct words, stable narrator, natural phrasing,
  pronunciation, and consistent chapter transitions; speed alone cannot pass.
- Windows 10 x64 target; actual supported Windows build, Python/PyTorch/CUDA/driver
  combination must be validated. Windows 10 lifecycle/security and modern dependency
  support are risks, not reasons to silently raise the OS minimum. RTX 3060 variants
  differ: detect available VRAM rather than assume 12 GB. CPU fallback must be honest
  about feasibility and speed; no runtime model downloads without consent.
- Preserve originals and referenced outputs. Crash recovery must reconcile metadata
  and files without treating partial output as valid. Disk-full is a first-class error.
- Libraries reside outside install directories and are relocatable. Single local
  service owns SQLite writes. No shared SQLite file over a LAN/network filesystem.
- Database/schema/archives/provider contracts are versioned. Upgrades back up first;
  incompatible versions refuse safely. No destructive automatic downgrade.
- No silent missing segments, changed seeds/settings, substituted voices, or automatic
  loss of source material. Explicit stale/failed/missing state and export blockers.
- Offline operations must not fetch remote fonts/scripts/models, require sign-in,
  activate licenses, or contact telemetry. Optional updates/downloads require action.
- UI must preserve unsaved work, show actionable job errors, be keyboard usable,
  and adapt to small screens. Local API must defend against browser-origin attacks.

## Non-goals for the first release

No model training/fine-tuning, LLM manuscript writing, automated web research,
commercial cloud narration, real-time voice chat, multi-user collaboration, full DAW,
Git replacement, arbitrary plugin code from project archives, cloud sync, remote
Internet access, or mandatory native desktop shell. Revision history is a linear
production history with named snapshots, not branching/merging Git semantics.
Ambience, dialogue casting, advanced pacing, LAN, and GitHub integration follow the
reliable single-narrator offline workflow. Linux cloud checks aid development; they
do not establish Windows distribution readiness.

## Approved clarifications (2026-10-29)

Commercial and noncommercial productions are supported goals. Default models/voices
must permit commercial use; producers need rights to manuscripts, assets and reference
voices. Every AI model download requires separate approval of exact artifacts, sizes,
licenses and purposes. Project export/backup/restore/transfer must be self-contained
and work without the original library DB, including resolved shared dependencies.
Responsive Android/tablet browser access is required; authenticated LAN remains Phase 7.
