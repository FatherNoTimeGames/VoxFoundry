# VoxFoundry Site foundation

Status: **local implementation prepared; not registered, deployed or verified in a
browser or on real Android**. This is the active Site-first source. `../phase0` and
the local Python audio experiment remain separate, deferred research.

## Working slice implemented in source

- Private-owner server authorization using Sites-supplied identity, plus same-origin
  checks for writes. Top-level platform sign-in/sign-out links; no custom OAuth or
  browser session automation. All data routes fail closed without owner/storage setup.
- Projects: create, list/open, rename/describe and non-destructive archive.
- Documents: create/open, manual save with expected versions, immutable revisions,
  conflict responses, read-only archived records and revision-history display.
- Transactional replay receipts: repeating the same normalized operation/request ID
  returns its original result, even after later edits. Different payloads cannot
  reuse a request ID. Writes/revisions/receipts commit in one D1 batch.
- Project JSON snapshot export includes archived documents and all revisions within
  the export budget. No owner identity, internal replay receipts or credentials are
  exported. Oversized exports fail explicitly without silently dropping history.
- Mobile layouts, labelled form/editor controls, keyboard Save shortcut, unsaved-edit
  leave warnings, retained editor text on conflicts, draft download and explicit
  confirmation before replacing it with the latest saved version.

These features are **implemented and component-tested**, not proven on hosted Sites.
No sample records, fake successful saves, device credentials or narration controls.
No audio-proof code is imported. No significant dependency installation is needed.

## Runtime and source layout

`worker/index.js` uses the native Worker `fetch(request, env)` shape and Web APIs.
`worker/ui.js` contains essential HTML/CSS/browser JS; all requests stay same-origin.
`schema.sql` describes a new isolated D1 database. `scripts/build.mjs` syntax-checks
the browser script, bundles the UI into the Worker and checks the single ESM entrypoint.
No SQL schema changes occur during requests. Do not apply this schema to the existing
manuscript or audio-proof databases or seed it with a source snapshot of user data.

The server expects `env.DB` and a server-side `OWNER_USER_ID` matching the owner's
Site-scoped ChatGPT user ID. `/api/identity` exposes only the signed-in caller's own
ID for setup. An external identity-less service credential cannot authorize data
routes. Header injection/stripping and the private boundary must be verified on Sites.
Tests deliberately inject identity headers; this is not an authentication proof.

No R2 binding is needed for this text-only slice; leave it unused. File upload/private
file access, authenticated MCP tools, library-wide search, autosave/session restoration,
Wiki, atlas and full export/import restoration are subsequent slices. The current
export is a versioned project snapshot, not a proven independent restore capability.

## Existing-runtime checks

From this directory with Node 24 (no npm install):

```sh
node --test --test-isolation=none tests/foundation.test.mjs
node scripts/build.mjs
```

Executed on 2026-10-30: **19 tests passed, 0 failed, 0 skipped**; build/parse validation
passed. Tests execute actual SQLite SQL through a local D1-shaped adapter. A file-backed
test closes and reopens SQLite, then verifies saved content, revisions and replay
receipts. It is not a restarted cloud D1 or independent device.

Checks cover owner/origin authorization, cross-owner record/history/export denial,
atomic duplicate creation, payload-bound receipts, expected-version conflicts,
concurrent saves, full rollback on injected database failure, unknown commit outcome
recovery, original/revision retention, archive rules, Unicode/body/type/size bounds,
project cap, authorized export shape/budget, local durable reopen, and UI/script/CSP
structure. Static HTML/JS checks do not prove accessibility or browser interaction.

## Hosting gates and costs

Nothing has been provisioned or deployed. The accessed Sites references document D1/R2
and schema migrations but do not supply the exact ESM hosting binding/migration
configuration needed here or account-specific pricing. The lifecycle helper named by
the skill is not materialized in this executor; attempting to read that helper through
the skill provider failed. Do not fabricate its path, a manifest schema or a project ID.
The supported template README was accessible and confirms top-level sign-in and
separate local/hosted migration behavior. References are in the validation ledger.

Before registering/provisioning: verify actual Sites request/CPU, database read/write/
storage, retention/backup and any file/transfer allowances, rates and an approved
budget. Existing ChatGPT/Codex account usage remains governed by that plan. No new
hosting service charge has been introduced by this source-only work. There is no
mandatory inference API, GPU, paid library or downloaded model in this slice.

Application limits: 50 projects and 500 documents per owner, including archived
records; 120-character project titles, 180-character document titles, 1,000-character
descriptions and 50,000-character documents; request bodies up to 256 KiB. Single-file
exports have a 2 MiB SQL-estimated raw-text/row budget (encoded JSON can be larger).
Failed/duplicate requests can still consume hosted usage. Revisions and command
receipts are retained; these limits are **not a billing cap**. Production paging,
retention/backup policy, upload bounds and scalable exports need later review.

After the cost/configuration gate, use the real Sites lifecycle to register once,
persist the returned ID, bind a fresh D1 as `DB`, apply schema through the supported
migration mechanism and configure `OWNER_USER_ID`. Keep the Site owner-private.
Package the exact verified source/commit with the Sites source workflow. A deployment
must never silently attach this schema to an existing user library.

`dist/server/index.js` is build output only. It is deliberately **not a deployable
archive** without real identity, verified hosting bindings and migrations. No
`.openai/hosting.json` with guessed fields or IDs is provided. The sign-in routes
`/signin-with-chatgpt`, `/signout-with-chatgpt` and `/callback` remain platform-owned.

## Manual browser / actual Android checks (unrun)

Only after an approved private deployment and actual storage/owner setup:

1. Open the exact deployed URL on real Android in both the intended supported Site
   surface and a normal browser tab. Sign in at top level and verify return navigation.
   Record Android/browser versions. A signed-out/non-owner caller cannot list or read
   projects/documents/history/exports or mutate them; forged browser identity headers
   must not bypass Sites dispatch. Do not export cookies or credentials into logs.
2. At 360–390px, create a project and document, enter non-sensitive text, tap Save and
   wait for Saved. Reload: exact content/version must persist. Rename the project;
   verify it persists. Repeat from a second authorized browser/device, with the PC off.
3. Open the same document in two sessions. Save different changes from the same base
   version. The second save must show Conflict while retaining its unsaved text.
   Download that draft, then explicitly Load latest; verify the committed content and
   unchanged prior revisions. A failed reload must not discard the editor text.
4. Interrupt a submit/save response, then retry the same unchanged form in the same tab.
   It must produce one project/document/revision. Pending request IDs are in memory;
   after a tab reload check existing records before resubmitting an uncertain creation.
5. Inspect History. Archive a document: its text/history remain readable and editing
   is disabled. Archive a project: enable Include archived projects to reopen it,
   with its documents retained and new edits/creation disabled.
6. Export the project and check its versioned JSON, archived data and revisions. It
   must not contain owner IDs, receipt hashes or credentials. Above the budget, require
   an explicit error rather than partial history. Full import/restore is still unrun
   and not implemented in this first slice.
7. Verify phone touch, visible focus, keyboard Save, labelled fields, native dialog
   focus/close behavior and screen-reader status announcements; then tablet ~820px
   and desktop ~1440px. Check a busy save cannot navigate away/replace another document.
8. Close/reopen the Site and repeat reads while the Windows PC is off. This proves
   hosted independent persistence only if observed. No Windows companion or audio
   playback is required, and browser emulation is not actual Android proof.

Known first-slice limits: manual Save only; unsaved editor/pending receipt state is
in memory and may be lost on tab crash/reload. Leave warnings are advisory and may
not appear on every mobile lifecycle transition. There is no autosave, durable local
draft/session restoration, live cross-device subscription, project restore/unarchive,
export-import pipeline, file library or AI generation. None is marked complete.
The browser/controller and `sites-preview` command are unavailable here; no substitute
preview server or browser was installed or launched.
