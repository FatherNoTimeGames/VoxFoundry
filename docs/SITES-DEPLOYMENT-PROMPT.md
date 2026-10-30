# Site foundation prompt — conditional preflight

Updated 2026-10-30 for the user's direction: complete Site functionality first;
Windows audio is a planned feature. This replaces the earlier audio-transport
preflight. Preserved prototypes and their validation remain in the repository.
S0-08 remains conditional until Site-only S0-07 evidence is available. This file
neither deploys a Site nor approves costs, a public launch or model downloads.

```text
Build VoxFoundry's private Site foundation as the first slice of the Site-first plan.

Read AGENTS.md and the active scope in docs/TASKS.md, then REQUIREMENTS, ARCHITECTURE,
ROADMAP, VALIDATION and PLANNED-FEATURES. Preserve existing application/library data,
source, history and the deferred audio prototypes. Follow the Sites plugin workflow.

Verify the installed Sites runtime and current supported owner sign-in, D1 records,
R2 private files, migrations, authenticated MCP tools and account cost/limit contract.
Use only verified binding/migration configuration and the real registered Site ID.
Keep owner access private and verify permissions on every data operation. No browser
DB/admin credentials or assumed access to external ChatGPT conversation history.
No mandatory paid AI API or claim that a ChatGPT subscription supplies API credits.

Before provisioning or introducing charges, report actual account pricing, allowances,
quotas, retention and backup/restore limits and the approved budget. If these remain
unknown, complete safe local preparation and report the precise hosting blocker.
Do not deploy or change audience without the authorization that applies to that step.

Verified configuration to complete before publication:
- Sites product/runtime and source references: {{verified contract}}
- Site ID/audience: {{real ID; owner-private}}
- D1/R2 bindings and migration workflow: {{verified configuration}}
- Hosting/storage/retention/quotas/costs/budget: {{verified values and approval}}
- Owner sign-in and per-record authorization: {{supported identity contract}}

First working slice: Android-first navigation, owner sign-in, project/document CRUD,
editor, acknowledged durable saves and reload recovery. Use stable IDs and expected
versions; show conflicts and preserve unsaved edits. Add only the files/storage needed
for this slice. Keep the existing local app separate; do not migrate its library by
accident or use localStorage as the cross-device authority.

Then complete scoped Site features in the documented order: writing/library/search,
linked records and sources, revisions and independently restorable exports, supported
ChatGPT context/tools and proposal/review/canon workflows, enabled Wiki integration
and the lore atlas. AI output/autosave never approves canon or publishes a Wiki.
External Wiki writes require explicit reviewed changes and authorization. Inspect
map/provider terms before imports; use rights-cleared uploaded maps where appropriate.

Design for 360–390px phones, 44px tap targets, readable layouts, no hover dependence,
keyboard/screen-reader use, then tablet and desktop. Test actual Android sign-in,
editing/save/reopen, cross-device visibility and enabled feature interactions. Keep
browser emulation, unit checks and real-device evidence distinct. The Site must remain
usable with the Windows PC off and without any companion application.

Exclude the planned Windows audio connection from the current Site: do not add worker
pairing, service credentials, job/attempt/lease schema, tone generation, narration
controls or worker-playback acceptance gates. Do not deploy sites/phase0 as the Site
entrypoint. Preserve those experiments for the planned feature instead of deleting
or silently repurposing them. No model/voice downloads, cloud GPU or external bridge.

Test authentication/authorization, project/document persistence, retry/duplicate-save
behavior, version conflicts, refresh/session boundaries, file bounds/permissions as
applicable, export/restore and mobile interaction. Run checks appropriate to each
slice without installing significant dependencies. Report actual passes, failures,
unavailable tests and remaining feature gaps; a build or mock pass is not hosted proof.

Before declaring the Site complete, verify the active feature acceptance at S5-04,
private hosted access/storage and real Android usability, independently restorable
exports and remaining costs/limits. Do not require a Windows narration/audio loop;
resume that planned feature only after the Site checkpoint and a separate scope review.
No main merge, force push, public release, paid resources or automatic Wiki publication.
```

The Site-only preflight remains incomplete; reprioritizing the work is not evidence
of a hosted Site. Actual Windows execution, private worker dispatch and Android audio
playback/download remain unverified and deferred, rather than successful or required
for the active Site phase.
