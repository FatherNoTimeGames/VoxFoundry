# Revised Phase 0 validation ledger

## Binding-format follow-up — 2026-10-31

The official Manage a site subpage (O9) resolved the minimal binding format that
the previous review missed. Added the pre-registration manifest and updated the
builder to validate/copy it. No project ID, runtime values or guessed migration
metadata was added. Existing application, schema, tests and audio source are unchanged.

**Executed:** `node scripts/build.mjs` from `sites/studio` passed. A Node artifact
smoke check confirmed that built/source manifests match, identity remains absent,
and the generated Worker returns 401 without identity and 503 without DB setup.
These checks use Node Web APIs, not hosted Sites or D1. The 19 foundation component
tests were not rerun for this build-metadata-only change; their prior results stand.

Read official Create a site, Data and connections and Publish and share pages as
well as O9. Some starter `.mjs` scripts were readable but do not supply the required
migration integration. Project resolution and bounded runtime inspection found no
Drizzle, Wrangler or Vinext tools available. No dependency was installed. npm page
and registry reads failed through the web tool; no retrieved package was executed.

No Site, database, file store, preview, login, MCP connection or deployment was
created or tested. No environment repair/policy/proxy change occurred. The exact
binding-format gap is closed; migration/lifecycle packaging, account applicability
and private hosted/actual Android acceptance remain open. Phase 0 is incomplete.

## S0-02 documentation and tooling checkpoint — 2026-10-31

Read current AGENTS/TASKS and confirmed a clean checkout. Re-read installed Sites
main, storage, identity, MCP and troubleshooting references; starter `package.json`
was accessible. Lifecycle helper and starter Drizzle-config reads failed. Executor
skill inventory returned none, while cloud Sites resources and native tools work.
Bounded filesystem checks found no lifecycle scripts/preview CLI in inspected locations.
No dependency, runtime repair or substitute browser/platform was introduced.

Accessed primary web sources O5–O8 via the supported web tool. This supersedes the
old documentation-access failures for these pages, not for unread sources. Public
terms now have a dated evidence record; selected-account applicability is unresolved.
Do not treat template/example prose as the exact manifest/migration schema.
Full contract/asset limits are in [the checkpoint](research/sites-platform-contract.md).

Read-only owner Site inventory completed with no VoxFoundry title/slug match and no
remaining page. No Site ID was selected, registered or changed; no other Site's
source, database, environment values or credentials were read. No account plan can
be inferred from that inventory. A plan question was requested for S0-D1 applicability.

No implementation changed; no tests were rerun. The 19 foundation checks and earlier
audio evidence retain their previously recorded scope. No actual login, hosted
D1/R2, MCP connection, browser or Android check ran. S0-02 remains blocked on the
specified setup/runtime evidence; no feasibility/phase exit or deployment is claimed.

## Site foundation local slice — 2026-10-30

Prepared `sites/studio` independently of `sites/phase0` and the local application.
No worker/audio code or existing libraries were changed. This is first-slice source
preparation while Site-only hosting/preflight gates remain unresolved, not a phase exit.

**Executed with existing Node v24.19.0, no install:**

```sh
cd sites/studio
node --test --test-isolation=none tests/foundation.test.mjs
node scripts/build.mjs
```

**19 tests passed, 0 failed, 0 skipped; single-file ESM/browser-script validation passed.**
Actual SQLite SQL ran through a local D1-shaped adapter. Coverage: missing/wrong owner,
same-origin writes/no CORS, owner-scoped records/history/exports, atomic duplicate
creation and payload-bound durable receipts, version-conflicting concurrent saves,
immutable revisions, replay after later edits, injected SQL rollback/lost commit-ack
recovery, non-destructive archives, strict type/Unicode/body/content validation, caps,
complete bounded export semantics, and file-backed SQLite close/reopen persistence.
UI/script/CSP checks are structural/syntax checks, not browser or accessibility proof.

Re-read installed Sites references:
- `skill://plugin_connector_1p_689987207de08191979cf68eca2941c6/sites/references/storage.md`:
  D1 records, R2 files, schema-only migrations, deployment-time migration application,
  one statement per prepare and batch for multiple statements.
- `skill://plugin_connector_1p_689987207de08191979cf68eca2941c6/sites/templates/vinext-starter/README.md`:
  platform-owned sign-in, Site-scoped IDs, top-level navigation, separate local/hosted
  storage and migration workflow. No self-hosted OAuth replacement is implemented.

These sources did not establish the exact Worker ESM hosting binding/migration JSON
or account-specific prices/allowances. The skill's lifecycle helper is not present in
the executor; a skill-resource read of `scripts/project-setup.mjs` failed. Referenced
example/config/auth source-file reads also failed; no contents are claimed accessed.
The storage and template README reads did succeed. No price or manifest schema was
invented. D1 `env.DB` and owner configuration are required; R2 is unused in this slice.

No Site/resource was registered or deployed. No model, package or significant
dependency was installed. No preview/controller or `sites-preview` was available,
so no preview server, substitute browser or screenshot was attempted. No audio tests
were rerun: source is isolated and the feature remains deferred.

**UNVERIFIED:** platform sign-in/header trust and access policies, hosted D1/migrations,
any R2/file behavior, MCP/ChatGPT tools, real browser interactions/accessibility,
actual Android and cross-device/PC-off behavior, hosting costs/limits/retention/backups,
independent import/restore. Manual checks and first-slice limits are in
[sites/studio/README.md](../sites/studio/README.md). Manual Save is not autosave or
crash-safe draft/session restoration. Exports fail explicitly above their size budget;
history is never silently truncated. Phase 0 and Site completion remain incomplete.

## Scope change: Windows audio is planned — 2026-10-30

The user deferred the Windows audio connection until Site functionality is complete.
Updated only documentation/operating instructions: active tasks/dependencies,
requirements, roadmap, architecture, Site foundation prompt, planned-feature list
and prototype status labels. Source, tests, existing libraries and history are
preserved. Neither audio proof is the current Site entrypoint.

Validated document links and the active dependency change: S0-07 excludes the
deferred S0-03/S0-06 audio proof; Site phases 1–5 do not depend on a worker, service
credential, audio job schema or Windows narration. Site auth, durable data, exports,
costs and actual Android Site usability remain acceptance requirements. General
Site backup/restore stays required before Site completion.

No implementation tests were rerun for this documentation-only change. The prior
25 original and 29 reviewed component results below are retained as previously
executed evidence, not new tests or hosted proof. No live Site, D1/R2, private
dispatch, Windows, Android, browser or deployment checks ran in this scope update.
Hosted Site behavior and real Android Site use remain unverified. Windows execution,
audio transport and actual Android playback/download remain unverified and deferred.
No cost/installation/resource/public-release change occurred; Phase 0 is incomplete.

Earlier sections retain the old audio-first acceptance and historical session
constraints. The active acceptance in TASKS/PLANNED-FEATURES supersedes that scope;
deferral does not upgrade any unrun test to a pass.

## Recovered patch and independent review — 2026-10-30

The checkout was clean on `phase0-direct-sites`; existing branches and source were
preserved. Read AGENTS and TASKS before recovery. Rejoined the retained byte-exact
text corresponding to the three previously supplied chunks, using their 1–500,
501–1000 and 1001–1499 line boundaries, without headings or normalization.

- Patch: `voxfoundry-phase0-e5b1ea2.patch`, **87,420 bytes / 1,499 LF lines**,
  no CR bytes, trailing patch separator space and final blank line preserved.
- SHA-256: `dc33e36b01fce120d3b499cb92fcf5bce332750f10b1938c92f60fe3377a41a1`.
- Base: `9a0c8213719d626c84658105e8febcb4f6cdca3c`.
- Original source commit (provenance): `e5b1ea245bd12ae5c0de28e1438013557f72f948`.
- Applied using `git am` on separate branch `phase0-direct-sites-recovered` as
  `48deb9c10026008433be08bc292ad639bff96a1a`; the resulting tree was verified identical
  to the original source commit before review fixes. Original branch unchanged.

Independently ran the three requested commands from `sites/phase0` using existing
Node v24.19.0 and Python 3.12.14. **Before edits: 16 JS/SQL + 9 Python tests passed,
0 failures, 0 skips; ESM build/parse check passed.** This independently reproduces
the originating session's 25 component results, not its hosted/device claims.

Review examined owner identity/origin checks, Site-versus-device authority, device
revocation, assignment-specific leases, claim/attempt atomicity, body-bound
idempotency, WAV bounds/hash validation, R2-before-D1 commit order, orphan handling,
local SQLite locking and durable output/lost-ack/cache recovery. Two concrete defects
were reproduced with failing tests, then fixed within the disposable proof:

1. JavaScript regex coercion admitted an array containing a valid request ID and
   caused a database error/HTTP 500. Request IDs must now be strings; malformed IDs
   return 400 without creating a job.
2. An existing POSIX cache directory could be shared/readable despite containing
   lease credentials in SQLite. Worker startup now requires it to be owned by the
   current user with no group/other permissions, before creating the ledger. It does
   not silently change permissions. Windows NTFS ACL enforcement remains manual.

**After fixes: 19 JS/SQL + 10 Python tests passed, 0 failures, 0 skips; ESM build/parse
check passed.** New cases cover malformed request-ID types, another enrolled device
using a copied lease, simultaneous differing uploads and unsafe existing cache modes.
The competing-upload case verifies exactly one committed result and readable winning
bytes; the losing valid upload remains a documented orphan. The new POSIX permission
test will be explicitly skipped on Windows, where real ACL validation is required.

Commands executed:

```sh
node --test --test-isolation=none tests/routes.test.mjs
python -m unittest discover -s tests -p test_worker.py -v
node scripts/build.mjs
```

These use a local real-SQLite D1 adapter, in-memory R2 and Python transport doubles.
They are **not hosted Sites authentication/D1/R2/private-dispatch tests, Windows
execution or actual Android playback/download**. Those remain unrun and unverified.
No additional browser/device/FFmpeg test was run during this recovery. No deployment,
resource provisioning, models or dependency installation occurred. Phase 0 is incomplete.

Git transport could not connect to its configured proxy. The supported GitHub connector
could read the pinned base and confirmed the requested review branch did not exist.
Publish only to that separate branch; verify its head and source tree before reporting
success. API-created commit metadata can yield a different SHA from the local reviewed
commit; original source/patch provenance above remains authoritative. No force or main
update is authorized. Final remote publication evidence is reported separately.

## Direct Sites component proof — 2026-10-29

Based on exact commit `9a0c8213719d626c84658105e8febcb4f6cdca3c`. All six requested
files were read from that Git snapshot: README, AGENTS, TASKS, ARCHITECTURE, POC and
SITES-DEPLOYMENT-PROMPT. New implementation is isolated in `sites/phase0`.

- **16 JS/SQL tests passed, 0 failed, 0 skipped** using Node v24.19.0:
  `node --test --test-isolation=none tests/routes.test.mjs` in `sites/phase0`.
  Tests use actual SQLite SQL through a D1-shaped local adapter and in-memory R2.
  Approval/body-bound idempotency, owner/origin checks, wrong worker credentials,
  competing claims, attempt audit, monotonic progress, lease fencing, revocation
  during upload, WAV bounds/format/hash, idempotent lost-ack completion, immutable
  results, authorized ranges/download, handler restart, storage failure/recovery,
  expired upload orphan handling, attempt/retry/job caps and fail-closed setup pass.
  Static UI/script/CSP checks pass; these are not browser accessibility/audio tests.
- **9 Python tests passed, 0 failed, 0 skipped** using Python 3.12.14:
  `python -m unittest discover -s tests -p test_worker.py -v` in `sites/phase0`.
  Reuses original tone generator/verifier; tests durable render-before-upload ledger,
  restart/cache/lost-ack/expired-lease handling, process exclusion, path protection,
  separate Site/device transport headers, redirect refusal and HTTPS/origin binding.
  Worker network tests use protocol doubles, not actual HTTP or private dispatch.
- **Worker ESM build/parse check passed:** `node scripts/build.mjs`. Copies one ESM
  entrypoint with `default.fetch` to ignored `dist/server/index.js`; explicitly not a
  deployable archive without verified hosting bindings/migrations/Site identity.
- **Independent local decode passed:** original Python generator produced 64,044-byte
  WAV; system FFprobe reported `pcm_s16le`, 16,000 Hz, mono, duration 2 seconds;
  system FFmpeg fully decoded 64,000 PCM bytes with exit 0. No new software installed.
  This ran on Linux, not Windows, Android or a Site Worker.
- Initial route run exposed a missing-owner configuration binding error (14/15 pass);
  fixed by rejecting worker access before binding absent owner configuration. Final
  successful test run supersedes this failure. Node's subprocess-isolated test launcher
  also returned an opaque file-level failure; using its supported in-process isolation
  option ran the complete suite. No browser protections or TLS checks were disabled.

No new dependencies/models, secrets, outside bridge, hosting resources, remote push,
public release or Site deployment. No generated data/credentials/audio in Git.
Existing POC full tests are **unrun here** (`filelock` absent); original evidence below
is historical. No `sites-preview` command or `cua_repl.js` was found; browser QA was
not attempted via a substitute server/browser. Cloud status reports unrestricted
enforced networking, no configured secrets/identities; this is not provider API proof.

**UNVERIFIED:** actual D1/R2 persistence and migration provisioning, exact Worker ESM
hosting binding JSON/migration plumbing, account pricing/quotas/retention/egress,
private dispatch service credential acceptance and forwarding of independent worker
Authorization, trusted hosted visitor identity, hosted HTTP recovery, real Windows
ACL/runtime/3060, real Android sign-in/play/seek/download/offline/PC-off use, MCP calls.
MCP is documented but intentionally not added to this minimal transport experiment.
Manual steps and exact sources are in [the proof README](../sites/phase0/README.md).
Phase 0 remains incomplete; none of this upgrades the old end-to-end matrix to pass.

2026-10-29. A result is a pass only if its command ran and the required behavior was
observed. Old local-app results remain in the [historical ledger](archive/local-first-2026-10-29/VALIDATION.md),
not evidence of Sites/device integration. No full new Phase 0 success claim.

## Initial reset checks (continuation results below)

- Inspected repository at clean base 8bf7cd9, active instructions/tasks, pinned tools
  and available connectors. No Sites deployment/persistence/runtime tool is callable.
  User confirms no deployed Site and no Windows app. Windows/Android not attached.
- **7 component tests passed, 0 failed, 0 skipped**:
  durable queued jobs across store close/reopen; request-id/body binding; exclusive store
  lock; lease expiry/fencing/monotonic progress; bounded automatic attempts and explicit
  retry without deleting attempt history; wrong worker auth; refusal to reuse an existing
  manuscript-library directory; idempotent committed
  completion and retained bytes; WAV integrity; worker restart and expired-lease recovery
  reusing cached generated output. Worker tests use an in-process protocol double.
- Initial component run found a credential-file creation API error; corrected it and
  reran the affected component tests successfully. No credential value was printed.
- Ruff checks/formatting, Python compile checks and formatting of the POC HTML/JS/CSS
  executed. Documentation links/task graph checked at the final review. These do not
  replace live HTTP/browser or security/integration acceptance tests.
- No new dependencies, models, external host, map assets or wiki changes installed/
  deployed/published. Generated test databases/credentials/audio stay outside Git.

## Initial blocked attempts (historical; later execution below supersedes some items)

- Official documentation fetch: automatic approval review failed with reviewer capacity;
  another attempt timed out; the expressly allowed retry again failed with capacity.
  Commands were not executed. No new OpenAI/Map/Wiki page was read or HTTP status observed.
- Live loopback server/worker/Chromium test command: automatic permission review failed
  with reviewer capacity; **not executed**. No live HTTP endpoint, browser audio decode,
  download, cross-origin auth, separate worker process or bridge restart over HTTP is
  claimed to work. Tests are present for later execution when permission review recovers.
- Required documentation host additions were saved in a draft, not confirmed active in
  the runtime. Saving does not establish network access, source truth or deployment.

## End-to-end gate matrix

| Required step | Result | Remaining proof |
| --- | --- | --- |
| Create actual Site UI / submit approved passage | Unrun | Identify product; supported disposable Site deployment and auth |
| Persistent Site-accessible queue | Unrun for Sites | Direct platform or approved bridge; durable/authorized access and costs |
| Windows companion securely claims | Unrun | Run portable harness on actual Windows 10; auth/polling/recovery |
| Generate short local audio | Tone generation verified in component tests | Real transport and Windows runtime; speech/GPU separately gated |
| Upload/progress/complete through HTTP | Unrun | Execute live tests, then supported Site contract |
| Android playback/seek/download | Unrun | Real Android device/browser and saved offline bytes; emulation insufficient |
| Worker-off retained Site/file access | Unrun | Hosted queue/object retention, PC off, sessions/restores tested |
| Disconnect/retry/duplicate prevention | Component state machines passed | Real HTTP, device and cloud restart/credential tests |
| Access controls | Credential and lease unit behavior passed | Live owner/device authorization, TLS/CSP/CORS/CSRF, revocation and file access |
| Hosting/storage/account costs | Unknown | Current plan, billing/quotas/retention/egress verified and approved |

## Pending commands and manual checks

`tests/poc/test_live.py` defines live loopback owner/worker auth, invalid/oversize upload,
WAV/range/private download, bridge restart, separate worker CLI and browser tests at
390×844 touch, 820×1180 touch and 1440×900 desktop. It also checks playback/download after
worker exit and resuming generated output. These are **unrun**, and even a later pass
would establish Linux/local/emulated behavior only. Run the manual Site/Windows/Android
matrix in research/sites-worker-integration.md before an exit success claim.

No Phase 0 exit is approved. A partial evidence/blocker report and conditional deployment
prompt do not satisfy the mandatory end-to-end proof. Finalize S0-08 only after the
platform/architecture/test evidence is available; never expand into the full app early.

POC implementation commit: 9893611. Cloud startup/network draft persistence was confirmed;
the legacy automatic full-app install script was cleared for this minimal scope. No
runtime network grant, new snapshot publication or fresh-task restoration is claimed.

## Continuation: execution and source recovery

- The first `pytest -q tests/poc` command executed: **7 passed, 5 failed, 0 skipped**.
  Two failures were fixture lifecycle errors: the owner helper made a request and then
  entered the same already-open httpx client again. Three viewport failures occurred in
  the Playwright polling expression: its string eval was rejected by the page's CSP.
  The application CSP was not relaxed. The helper now opens/closes its client in a
  contextmanager; polling uses a function. Those test corrections are not claimed to
  have passed live re-verification yet.
- Before the three browser assertion failures, phone/tablet/desktop cases submitted
  jobs, ran a separate Linux worker subprocess with exit 0, and observed succeeded
  uploaded-audio status after worker exit. Playback decode/download final assertions
  remain unverified; no actual Android/Windows/Sites evidence is inferred.
- Corrected reruns did not execute: automatic approval review timed out twice, and a
  later attempt after a successful documentation read hit reviewer capacity. This is
  an execution-review outage, not a code test result or unsafe-action determination.
- **7 component tests passed again**, no skips. Ruff/format/compile passed. The corrected
  owner fixture lifecycle was independently exercised with a mock transport and closed
  cleanly; that check does not replace live HTTP tests. FFprobe identified mono 16 kHz
  signed 16-bit PCM and FFmpeg decoded all 32000 samples (64000 raw bytes, 2 seconds)
  from the generated WAV. No browser/device playback is inferred from this decode.
- Successful primary reads: official OpenAI Apps SDK examples README, GitHub wiki Git
  documentation, Leaflet LICENSE. SHA-256/source URLs are in REFERENCES. Apps SDK
  documentation evidence supports MCP widgets/tools and server-side persistence, not
  Sites equivalence or an included hosted database. Wiki Git and Leaflet BSD 2-Clause
  are documented, not live integration/renderer tests.
- Full OpenAI Apps SDK docs and Pindrop returned proxy CONNECT 403. Runtime custom host
  list is still empty; prior draft additions are not active evidence. Other requested
  map pages/terms, Wiki auth/plan limits, hosting prices and exact Sites product remain
  unresolved. No new dependency/model/install/deployment/publication occurred.

Test fixture corrections are committed as bfd755a. Updated cloud start_skill draft
persistence is confirmed; this neither runs tests nor activates host access/publishes
a snapshot. Review/save environment settings and publish the cloud snapshot separately
if retaining the updated runtime state; no Site or software publication was performed.
