# Revised product requirements

2026-10-29 scope reset. Personal-use creative studio; NEW Phase 0 only is authorized.
Previous local-first architecture approvals do not approve the revised system. Keep
existing code/history/data; preserve independent exports and non-destructive recovery.

Workflow: Research → Organize → Co-write → Review → Approve → Narrate → Publish.

| Requirement | Outcome / acceptance | Phase |
| --- | --- | --- |
| R01 Sites-first ChatGPT collaboration | Verify actual product, supported persistence/tools/auth; never silently substitute a website/API chatbot | 0, 1, 3 |
| R02 Android-first | Compact phone navigation/editor/review/atlas; 44px targets, no hover dependence, keyboard/screen reader, phone/tablet/desktop tests | all UI |
| R03 Cross-device persistence | Site usable with PC off; autosave, sync and session restoration tested separately; conflict handling; app-owned conversations only unless official APIs permit more | 1, 3 |
| R04 Central knowledge | Projects/source/original/hybrid workflows; stable documents/entities/relationships, provenance, chronology/uncertain dates, nested tags/categories/collections/geography/status/saved filters and FTS | 2 |
| R05 Canon/Review Queue | Brainstorm/draft/proposed/approved/superseded/rejected/archived states, typed proposals/evidence/diffs, explicit promotions, safe batches/conflicts, local approval separate from publication | 2–3 |
| R06 Wiki | Optional import/index/revision/auth/conflict-safe bidirectional sync; exact remote changes separately approved | 4 |
| R07 Atlas | Rights-cleared maps, touch navigation, editable markers/layers/regions/routes/periods/views, linked library/sources/scripts, confidence and placement provenance | 5 |
| R08 Windows worker | Outbound authenticated jobs, durable local state, interchangeable approved engines, segmentation/voices/pronunciation, retry/cancel/resume/cache/selective regeneration, progress/upload | 0, 6, 8 |
| R09 Audio | Non-destructive review/mastering, raw retention, MP3/chaptered M4B, artwork/metadata/validation, mobile play/download independent of worker | 0, 7–8 |
| R10 Ownership | Independent round-trip project archives in Markdown/JSON/standard media, all history/approvals/maps/sources/relationships/audio; no original library DB or proprietary-only access required | 2, 8 |
| R11 Costs/rights/security | No mandatory paid AI API/cloud GPU/subscription; costs and significant downloads approved; appropriate source/reference/map/model rights; no unsupported session automation | all |
| R12 Deployment prompt | Final Phase 0 deliverable: copy-ready Sites deployment prompt grounded in verified capabilities and cost/auth/storage decisions; conditional draft is not deployment proof/authority | 0 |

The Site/knowledge store must operate while the worker/PC is off; mandatory offline-only
central storage is superseded. Local inference/recovery remains local. Hosting/storage
costs and account limits are unresolved. Personal use supersedes the commercial-product
goal, not license obligations; Apache-2.0 source grant remains unchanged. Model downloads
still need separate exact artifacts/sizes/licenses/purposes approval.

Phase 0 must attempt the actual Site → persistent job → Windows worker → uploaded audio
→ Android play/download → worker-off availability loop. Implement/test available parts;
record all unavailable parts as unverified, never replace them with mocks and claim full
success. No full app, atlas, AI workspace, remote wiki publishing or installer is authorized
now. The Windows companion needed for the initial proof can be a small portable harness;
a tray/installer is not a prerequisite for protocol tests.
