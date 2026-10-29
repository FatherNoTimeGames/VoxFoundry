# Revised Phase 0 validation ledger

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
