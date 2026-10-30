# Direct Sites Phase 0 audio-transport proof

Recovery review (2026-10-30): the exact original patch was imported on a separate
review branch and its source tree verified against original commit
`e5b1ea245bd12ae5c0de28e1438013557f72f948`. The original 25 component tests were
independently reproduced. Narrow request-ID type and POSIX cache-permission fixes
plus added isolation/race checks now pass **19 JS/SQL + 10 Python tests**. Hosted
Sites/D1/R2/private dispatch, Windows and actual Android remain unverified. See
`docs/VALIDATION.md` for provenance, failing regressions and exact results.
For an existing POSIX worker-cache directory, startup now rejects non-owner or
group/other permissions; use an owner-only local directory (mode 700). The worker
does not alter existing directory permissions. Windows NTFS ACLs still require the
manual verification below; a POSIX permission test does not establish Windows safety.

Status: **implemented and component-tested; NOT deployed or verified end to end**.
Based on repository snapshot `9a0c8213719d626c84658105e8febcb4f6cdca3c`.
Existing backend, frontend, libraries and previous POC are preserved. No dependencies
or models installed. No resource created, charge introduced, remote push, public
release, external bridge or full-app feature added. No MCP server is implemented in
this minimal transport proof; its documented availability is recorded below.

## Exact Sites documentation accessed

These are installed OpenAI Sites plugin references, not Cloudflare pricing promises
or observed hosted behavior. Read on 2026-10-29; a plugin build/version identifier was
not provided. Their full source identifiers are recorded to avoid invented web URLs.

1. `skill://plugin_connector_1p_689987207de08191979cf68eca2941c6/sites/references/storage.md`
   — “Use D1 for structured product data and R2 for files.” It also states “Sites
   provisions and connects the hosted resources” and “Sites applies hosted migrations
   before uploading the Worker.” Runtime database schema changes are prohibited.
2. `skill://plugin_connector_1p_689987207de08191979cf68eca2941c6/sites/references/site-mcp-server.md`
   — “Sites authenticates MCP requests and checks that the caller can view the Site
   before forwarding them to your server.” Publishing with the `mcp` capability
   creates a private App/plugin for the owner. Additional application access checks
   remain necessary. This is not proof of external ChatGPT history access or an
   embedded ChatGPT chat UI. No paid API credits are assumed.
3. `skill://plugin_connector_1p_689987207de08191979cf68eca2941c6/sites/references/identity-and-secrets.md`,
   **Service Access** — “If `get_site` returns `siwc_bypass_bearer_token`, send it only
   to that Site as `OAI-Sites-Authorization: Bearer <token>`. Dispatch validates and
   consumes it; it supplies neither a visitor identity nor connected-app consent.”
   Browser identity uses trusted `oai-authenticated-user-id` headers; the ID is
   Site-scoped. Sign-in requires top-level navigation, not fetch.
4. `skill://plugin_connector_1p_689987207de08191979cf68eca2941c6/sites/templates/worker-esm-starter/README.md`
   — no-dependency Worker ESM; `dist/server/index.js` exports `fetch(request, env, ctx)`.
   The provided starter's single-file build shape is followed here. Essential UI/JS
   assets are served from the Worker. This is a Sites-native server, not FastAPI.

Native tool schema corroboration: `sites_get_site` can return the service credential;
`sites_generate_siwc_bypass_token` creates/rotates it but may be called **only when
the user explicitly asks for a bypass token**. Neither tool was called for a Site
in this work. Do not create or rotate a credential to probe availability.

## Authentication contract and proof boundary

Every external worker request carries three independent credentials where applicable:

| Layer | Request material | Authority / revocation |
| --- | --- | --- |
| Private Site ingress | `OAI-Sites-Authorization: Bearer …` | Dispatch checks the Site service credential. Broad Site ingress, not a person or per-device identity. Site-level rotation can affect all workers. |
| Application device | `Authorization: Bearer …` | Random 256-bit secret; only its SHA-256 verifier is in D1. A device row binds it to the configured owner. Owner can revoke the row immediately; it cannot call owner endpoints. Rotate by revoking and enrolling a new ID/verifier. |
| Job attempt | `X-Lease-Token` | Random attempt token, hashed in D1; bound to the assigned device/job/attempt, expires after 60 seconds. A live heartbeat renews it. Reclaim fences the old attempt. It is not device enrollment or Site ingress. |

Dispatch consumes the Site credential; application code does not verify or log it.
The worker never follows redirects or sends credentials outside its configured HTTPS
Site origin. No secret is in browser code, source, Git, chat/tool prompts, query strings
or application logs. The setup utility requests the service credential only through
hidden local terminal input and writes an owner-only file outside the repository.
The browser sees a public device ID/verifier only. Server code requires the configured
Site-scoped owner ID and same-origin owner writes, independently of Site privacy.

**Documented, not live-verified:** private dispatch accepts the service credential and
forwards the second `Authorization` header without turning it into a visitor identity.
This must be tested on the actual private Site. If that second header is not preserved,
stop and inspect the supported contract; do not weaken authentication or change audience.
A local test injecting an identity header does not prove trusted hosted identity.

## Implementation

- `worker/index.js`: private owner UI/API, device-verifier enrollment/revocation,
  D1 queue/attempt SQL, outbound claim/heartbeat/result routes and authorized R2 audio.
- `schema.sql`: schema for a **fresh disposable** D1 database, never the old library.
  Requires the supported deployment-time migration path; no request-time DDL.
- `worker_client.py`: standard-library adaptation of the existing portable harness;
  directly reuses `backend/voxfoundry/poc/audio.py` generator and verifier. Durable
  SQLite audio/lease ledger, lost-ack recovery, cache reuse and an exclusive process
  lock. No dependency install. Generated output is committed locally before upload.
- `setup_device.py`: generates a worker secret locally; prints only its public verifier.
- `tests/`: real SQLite behind a D1 API adapter, in-memory R2 and Python protocol doubles.

The queue requires explicit passage approval, binds idempotency keys to exact text
digests, and has three attempts plus one explicit owner-approved retry budget of three.
Claim+attempt recording is a D1 batch. Completion writes validated bytes before a
conditional D1 commit that rechecks time, lease and device revocation. R2 and D1 are
not one transaction: failed commits can leave unreferenced objects, never fabricated
completion. Attempt/content-addressed keys protect newer results. Retain orphans until
cleanup; do not delete a key that an uncertain duplicate upload may have committed.

Progress is monotonic within an attempt; a reclaimed attempt resets it. Tap Refresh
to see current state; the UI does not continuously poll or autoplay. A submit retry
without editing in the same tab reuses its request ID. Pending submit state is in
memory; after a page reload, check existing jobs before resubmitting an uncertain job.
This disposable proof does not implement production session restoration.

## Costs and bounded workload — review before resources

Account-specific Sites pricing, included allowances, D1/R2 billing, retention, egress
and quotas **are not supplied by the accessed documentation/tools**. No zero-cost claim
is possible. Direct Cloudflare list prices would not establish Sites account charges.
No hosting resources were provisioned to discover pricing. Local testing added no
external service; any existing ChatGPT/Codex account usage is governed by that plan.

Application bounds: 20 jobs, 1,000 characters per passage, 8 KiB JSON bodies, exactly
64,044 bytes per canonical WAV (2s, mono, 16 kHz signed 16-bit PCM), three automatic
attempts and one explicit additional budget. Twenty successful WAVs occupy 1,280,880
bytes (~1.22 MiB), excluding orphan uploads, metadata and backups. This is **not a
billing cap**. Private ingress, rejected requests and retries can still consume usage.
Use one-shot worker runs for the proof. Optional 15-second polling makes up to 5,760
claim requests/day while idle; each claim executes a two-statement D1 batch.

Before deployment, obtain the account's actual rates/allowances for Site requests/CPU,
D1 reads/writes/storage, R2 operations/storage/download transfer, and backups/retention.
Record an approved budget and available provider-level limits. Stop if charges cannot
be bounded as required by the user. No inference API, model download or cloud GPU is
needed. FFmpeg, if used for independent decode, remains on the worker/test machine.

## Deployment preflight (not yet executed)

1. Resolve the cost gate above before provisioning. Keep the Site owner-private.
2. Inspect installed Sites helper/tooling for **exact D1/R2 binding JSON and ESM schema
   migration integration**. The accessed storage guide establishes these capabilities
   but does not specify the complete binding/migration configuration for this custom
   Worker. Do not invent it. No `.openai/hosting.json` or fake project ID is included.
3. Once authorized and verified, register exactly one disposable Site, persist its real
   ID, bind a fresh D1 as `DB` and a private R2 as `BUCKET`, and apply `schema.sql` through
   the supported migration mechanism. Do not attach production databases/buckets.
4. Sign in at top level and read `/api/identity` to obtain the Site-scoped ID. Configure
   `OWNER_USER_ID` server-side using the native environment tool, then publish the exact
   tested source/artifact through the Sites workflow. All record routes fail closed
   until owner and storage configuration exist. `/api/identity` exposes only the caller's ID.
5. `node scripts/build.mjs` validates/copies the Worker ESM but intentionally does not
   create a deployable archive without the verified hosting configuration. Package,
   source-sync and deploy through Sites helpers after completing that configuration.
6. Obtain supported service access using an existing credential when available; never
   print it. Creating/rotating a bypass token needs the explicitly requested native
   operation. Transfer it only into the worker's hidden local setup input via a secure
   owner-controlled channel. Do not paste it into this repository, chat or tickets.
7. Test private dispatch: no service credential must be rejected **by the platform**;
   valid service credential without a device secret must reach the app but be rejected;
   valid device secret without service access must still be rejected by the platform.
   Neither secret may impersonate owner identity or read owner audio. Do not disable
   TLS, rewrite trusted headers, change the audience or automate a ChatGPT browser session.

## Exact Windows manual steps (UNRUN)

Prerequisites: an approved deployed Site after the above gates, real Windows 10/target
machine, already approved compatible Python 3.12+ and this repository checkout. No new
Python package, model or FFmpeg installation is required for tone generation. If a
prerequisite is missing, report it before downloading anything.

In PowerShell, from the repository root, replace the example with the real deployed
origin. The paths/URL below contain no credentials:

```powershell
$Site = 'https://REPLACE-WITH-VERIFIED-SITE-ORIGIN'
$Private = Join-Path $env:LOCALAPPDATA 'VoxFoundrySitesPhase0'
New-Item -ItemType Directory -Path $Private -ErrorAction Stop
$Account = [System.Security.Principal.WindowsIdentity]::GetCurrent().Name
icacls $Private /inheritance:r /grant:r "${Account}:(OI)(CI)F"
icacls $Private
py -3 sites/phase0/setup_device.py --site $Site --output "$Private\worker.credentials.json" --device-id windows-tone-1
icacls "$Private\worker.credentials.json"
```

Use a fresh private directory; do not reuse an existing library. Verify ACL output
restricts the folder/file to the intended account before proceeding. POSIX mode bits
alone do not prove Windows ACL isolation. Enter the service credential only at the
hidden local terminal input. Copy **only** the displayed public ID and SHA-256 verifier
into the signed-in Site's Worker setup section; click Enroll device verifier.

1. On the Site, type a non-sensitive short test passage; explicitly check approval and
   tap Approve & queue. Record the non-secret job ID. Refresh once: it must be queued.
2. Run one outbound worker cycle (no long-running background service):

```powershell
py -3 sites/phase0/worker_client.py --site $Site --credentials "$Private\worker.credentials.json" --data "$Private\cache"
$LASTEXITCODE
```

3. Require exit code 0, then refresh the Site and confirm the same job is succeeded,
   progress 100%, and has one committed result. Output is a **tone, not narration**.
   Re-run once: no new job/output should be generated. Wrong/expired/revoked credentials
   must fail without revealing values. Revoke the public device ID in the owner UI,
   then repeat: claiming must fail. Re-enrollment uses a fresh device ID/verifier.
4. For private-boundary rejection tests, run the supplied read-only probe, which reads
   the protected file, selectively omits headers and reports status/categories only:

```powershell
py -3 sites/phase0/check_access.py --site $Site --credentials "$Private\worker.credentials.json"
```

   Require all checks to pass. After completing a job, repeat with `--job-id` followed
   by its public UUID to check owner-audio denial too. No job is claimed by the probe.
   Do not put secrets into `curl` arguments, shell history or logs. Redirects are
   rejected, never followed into a login page with either secret attached.
5. For recovery, interrupt after render/before acknowledgment in a disposable test and
   restart using the same cache. Verify retained output is reused and one immutable
   result is committed. Expire a lease, reclaim it, and require stale completion to fail.
   Automated protocol-double tests cover these cases, not Windows/HTTP execution.
6. Exit the worker, then turn off the Windows machine for the Android checks below.

If FFmpeg is already approved/installed, independently decode the downloaded file
**on Windows**, not in the Site Worker:

```powershell
ffprobe -v error -show_entries stream=codec_name,sample_rate,channels,duration -of json .\voxfoundry-test-tone.wav
ffmpeg -v error -i .\voxfoundry-test-tone.wav -f null -
```

## Real Android acceptance steps (UNRUN)

1. With the Windows PC off, open the deployed private Site in the real Android browser
   intended for use. Sign in through top-level ChatGPT navigation and return to the Site.
   Test both a normal browser tab and the actual supported Sites surface; do not infer
   embedded-cookie behavior from the tab. Record Android/browser versions and surface.
2. At a 360–390px phone layout, confirm no horizontal overflow, readable text, 44px
   targets, checkbox/textarea labels, touch controls and screen-reader announcements.
3. Refresh. The same completed job must still appear from central storage. Play the
   full two-second tone with audio enabled. Pause/resume and seek using native controls;
   record any short-file seek limitation rather than claiming long-audiobook support.
4. Tap Download test tone. Confirm a 64,044-byte WAV is saved, open it in the intended
   Android audio app, enable airplane mode and replay that downloaded file. This proves
   downloaded-file offline access; the Site itself does not implement offline mode.
5. Re-enable networking. Close/reopen the Site and confirm retained status/audio.
   A signed-out/private-tab visitor without access must not fetch job metadata/audio.
   If practical, check byte-range responses (206 and correct Content-Range) using an
   owner-controlled tool without exporting authentication cookies/tokens into logs.
6. Repeat at tablet ~820px and desktop ~1440px when available; record each device.
   Browser emulation or a unit test is not real Android/Windows evidence.

## Automated checks and current evidence

From `sites/phase0` (Node 24/Python 3.12 already available here):

```sh
node --test --test-isolation=none tests/routes.test.mjs
python -m unittest discover -s tests -p test_worker.py -v
node scripts/build.mjs
```

See `docs/VALIDATION.md` for exact executed results. SQLite tests run the actual SQL
through a local D1 API adapter. R2 is an in-memory double. Python tests use a transport
double; header assertions do not contact dispatch. The app-restart test re-instantiates
the handler with retained local bindings, not a restarted cloud service.

No hosted D1/R2, private dispatch, actual HTTP worker round trip, browser audio,
Windows, Android or account billing test has passed. No managed browser controller
or `sites-preview` command was available; no substitute server/browser was installed.
The old local POC suite was not rerun: its `filelock` dependency is absent here.

## Cleanup / rollback

After the approved disposable experiment, revoke device rows; stop the worker and
preserve needed evidence before removing its outside-repository private data. Revoke
or rotate the Site service credential through supported controls if retiring it;
remember the documented rotation overlap may temporarily leave the old token valid.
Remove orphan and committed R2 objects, job/attempt metadata, then the disposable
resources using supported provider controls after confirming their IDs. Deployment
rollback alone does not undo data migrations or delete storage. Resource deletion
is not automated here. Export any needed result before destructive cleanup.
