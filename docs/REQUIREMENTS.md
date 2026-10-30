# Revised product requirements

2026-10-30 priority update: finish the personal creative-studio Site first. The
Windows audio connection is a planned future feature, outside current acceptance.
Site-only preflight and evidence-based feature checkpoints remain in TASKS.
Previous local-first architecture approvals do not approve the revised system. Keep
existing code/history/data; preserve independent exports and non-destructive recovery.

Current Site workflow: Research → Organize → Co-write → Review → Approve; enabled
Wiki publication remains an explicitly approved action. Narrate/audio production is
planned after Site completion. The long-term studio workflow remains preserved.

| Requirement | Outcome / acceptance | Phase |
| --- | --- | --- |
| R01 Sites-first ChatGPT collaboration | Verify actual product, supported persistence/tools/auth; never silently substitute a website/API chatbot | 0, 1, 3 |
| R02 Android-first | Compact phone navigation/editor/review/atlas; 44px targets, no hover dependence, keyboard/screen reader, phone/tablet/desktop tests | all UI |
| R03 Cross-device persistence | Site usable with PC off; autosave, sync and session restoration tested separately; conflict handling; app-owned conversations only unless official APIs permit more | 1, 3 |
| R04 Central knowledge | Projects/source/original/hybrid workflows; stable documents/entities/relationships, provenance, chronology/uncertain dates, nested tags/categories/collections/geography/status/saved filters and FTS | 2 |
| R05 Canon/Review Queue | Brainstorm/draft/proposed/approved/superseded/rejected/archived states, typed proposals/evidence/diffs, explicit promotions, safe batches/conflicts, local approval separate from publication | 2–3 |
| R06 Wiki | Optional import/index/revision/auth/conflict-safe bidirectional sync; exact remote changes separately approved | 4 |
| R07 Atlas | Rights-cleared maps, touch navigation, editable markers/layers/regions/routes/periods/views, linked library/sources/scripts, confidence and placement provenance | 5 |
| R08 Windows worker — planned | Deferred: outbound authenticated jobs, durable local state, approved engines, segmentation/voices/pronunciation, retry/cancel/resume/cache/selective regeneration, progress/upload. Not required for Site preflight or completion. | after Site completion; 6, 8 |
| R09 Audio — planned | Deferred: narration review/mastering, raw retention, MP3/chaptered M4B, artwork/metadata/validation, mobile play/download independent of worker. No audio transport or playback gate in active Site work. | after Site completion; 7–8 |
| R10 Ownership | Independent round-trip project archives in Markdown/JSON/standard media, all history/approvals/maps/sources/relationships/audio; no original library DB or proprietary-only access required | 2, 8 |
| R11 Costs/rights/security | No mandatory paid AI API/cloud GPU/subscription; costs and significant downloads approved; appropriate source/reference/map/model rights; no unsupported session automation | all |
| R12 Deployment prompt | Final Phase 0 deliverable: copy-ready Sites deployment prompt grounded in verified capabilities and cost/auth/storage decisions; conditional draft is not deployment proof/authority | 0 |

The Site/knowledge store must operate without a worker or a powered-on PC; mandatory
offline-only central storage is superseded. Future local inference/recovery remains
local and is not provisioned now. Hosting/storage
costs and account limits are unresolved. Personal use supersedes the commercial-product
goal, not license obligations; Apache-2.0 source grant remains unchanged. Model downloads
still need separate exact artifacts/sizes/licenses/purposes approval.

Site-only Phase 0 evaluates the actual Sites identity, storage, supported ChatGPT tools,
hosting configuration and costs. It no longer requires a job/worker/audio loop. Then
complete Site functionality in scoped slices: owner/project/document foundation;
durable editing/sync; knowledge/library/search/sources; revisions/exports; supported AI
tools/review/canon; enabled Wiki and the atlas. Verify the active feature set and real
Android Site usability at S5-04 before resuming the planned audio feature. Mock or
component passes do not establish hosted persistence or real-device operation.
Preserve the previous audio experiments without using them as the Site entrypoint.
No public release, paid resources, model downloads, remote Wiki writes or platform
substitution are authorized by reprioritizing this work.
