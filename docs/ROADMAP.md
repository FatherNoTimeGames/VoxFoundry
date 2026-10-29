# Revised roadmap — personal Sites-first studio

Status: NEW Phase 0 only. Old local-first phases/history are archived; no new full-app
architecture is approved. Exact task status/dependencies are in TASKS. No date promises.
All user-facing features require phone-first acceptance, then tablet/desktop, with
real Android checks for playback/download and major interaction/device gates.

| Phase | Deliverables | Exit |
| --- | --- | --- |
| 0 Feasibility/architecture/POC | Verify Sites/ChatGPT/worker APIs, auth/storage/costs, TTS/wiki/maps; unified data/review/atlas/export design; smallest available audio transport test; actual Site/Windows/Android gates; **final Sites deployment prompt** | Approved architecture supported by actual integration evidence; unknown parts explicitly remain gates |
| 1 Sites foundation | Supported project/auth/persistence, Android-first navigation/editor shell, autosave/sync/session restoration with PC off | Usable cross-device mobile workspace |
| 2 Knowledge library | Documents/entities/relationships/provenance, source/original/hybrid workflows, canon states, FTS/nested organization, revisions and portable exports | Interconnected knowledge with independent round-trip recovery |
| 3 Unified AI workspace | Verified ChatGPT context/tools, incremental retrieval, app sessions, research/co-writing and central Review Queue | Practical AI collaboration on Android/Windows without unsupported session assumptions |
| 4 GitHub Wiki | Authenticated import/index/provenance, external-change detection/diffs/conflicts and explicitly approved publishing | Reliable bidirectional sync without remote overwrite |
| 5 Lore Atlas | Rights-cleared maps, touch pan/zoom, markers/layers/search/library links/regions/routes/periods/views; authorized imports/AI proposals | Interconnected mobile lore atlas, not game progress tracker |
| 6 Narration | Separately approved engines/artifacts, profiles/segmentation, durable jobs/retries/cache/selective regeneration and recovery | Complete validated 60-minute manuscript |
| 7 Audio editing/export | Script/audio review, waveform/non-destructive edits/mastering, MP3/M4B, metadata/artwork/mobile playback/validation | Finished portable audiobooks |
| 8 Worker distribution/remote reliability | Production device auth/monitoring/streaming, Windows tray/install/update, full backups/CI/releases and preservation tests | Reliable mobile-controlled Windows production; distribution only separately authorized |
| 9 Advanced capabilities | Optional providers/roles, map generation/geographic reasoning, sound design/visualization and Android-native exploration | Each approved feature preserves the core workflow/rights/costs |

Dependency clarification: basic authenticated remote job/file transport must be proven
in Phase 0 and available before Phase 6 generation; Phase 8 hardens/packages it rather
than postponing this prerequisite. Portable project exports begin in Phase 2 so user
ownership does not wait for distribution. Paid API substitution, significant downloads,
hosted deployment and platform fallback remain separate consequential decisions.

The end-of-Phase-0 deployment-prompt deliverable precedes the phase-exit approval.
It must reference the verified platform/integration, secrets/storage setup, limits,
manual device checks and rollback; copying it does not authorize costs or deployment.
