# Revised Phase 0 decisions, approvals and audit

## Site first; Windows audio deferred — 2026-10-30

The user explicitly asked to take the Windows audio connection out for now, list it
as a planned feature, and get Site functionality working and complete first.
This supersedes the earlier mandatory Phase 0 Site → Windows → audio → Android loop.
S0-03, S0-06 and audio phases 6–8 are deferred, not passed or deleted. They no longer
block Site foundation or Site completion. Updated the active task dependency view,
requirements, roadmap, architecture, Site foundation prompt and operating instructions.
PLANNED-FEATURES records the preserved prototype paths and later resume criteria.

The Site remains independent of any companion: identity, projects/documents, durable
saves/sync, library/search/sources, revisions/export/restore, supported ChatGPT tools
and review/canon, enabled Wiki and atlas are the Site feature path. Actual Android
Site usability and private hosted identity/storage remain required. Windows worker
execution and Android audio play/download are deferred to the future audio feature.
General Site backup/restore is not postponed along with worker distribution.

No prototype/code/data was removed or deployed. Do not use the audio proof as the
active Site entrypoint or add worker setup, service credentials or audio-job schema
to the foundation. Historical component tests remain truthful evidence only. This
scope change does not approve paid resources, models, significant dependencies,
public release, main merge or force push. Phase 0 remains incomplete under its
revised Site-only acceptance, pending actual Site evidence.

## Recovery provenance and review — 2026-10-30

The user authorized checksum-gated patch recovery, narrow Phase 0 defect fixes,
independent component checks and publication to `phase0-direct-sites-recovered` only.
The original `phase0-direct-sites` branch and existing work remain preserved.
Verified source provenance: `e5b1ea245bd12ae5c0de28e1438013557f72f948`; base:
`9a0c8213719d626c84658105e8febcb4f6cdca3c`; checksum-exact local patch import:
`48deb9c10026008433be08bc292ad639bff96a1a`. VALIDATION records the complete patch hash
and independent before/after results. Review fixed request-ID type coercion and
insecure existing POSIX worker-cache modes, and added cross-device/concurrent-upload
checks. No credentials/media/models or runtime data belong in the source publication.
Supported GitHub API publication may create different commit metadata/SHA; require
the published tree to match the tested local tree and record original provenance.
No merge, force push, deployment, hosting spend or Phase 0 exit is authorized.

## Direct Sites continuation — 2026-10-29

The user identified the Sites plugin and exact base commit
`9a0c8213719d626c84658105e8febcb4f6cdca3c`, then authorized only a smallest direct
Phase 0 proof and tests, with no new costs, significant dependencies, models, bridge
or public release absent separate approval. Source changes are isolated under
`sites/phase0`; legacy application/POC code is preserved. No remote push authorized
by this continuation and none performed.

Installed Sites primary references now document D1/R2, identity/service ingress and
authenticated MCP. This supersedes earlier session-specific absence statements below
at the documentation level only. Implemented a dependency-free native Worker and
standard-library outbound client reusing the original tone generator. Site ingress,
revocable per-owner device identity and expiring per-job leases remain separate.

No deployment/resource creation: account-specific rates/allowances and exact custom
Worker binding/migration integration remain unknown. No alternative bridge or paid
provider was selected. Tests/evidence/manual device matrix are recorded in VALIDATION
and sites/phase0/README. No full-app architecture or Phase 0 exit is approved.

2026-10-29. The user replaced the previous local-first audiobook-only mission with a
personal Sites-first creative studio and explicitly requested Phase 0 only. Old source,
LICENSE and Git history are preserved; old plans/task outcomes are archived in
[local-first-2026-10-29](archive/local-first-2026-10-29/TASKS.md). Prior architecture and
phase approvals do not authorize this new platform, hosting or full implementation.

## Scope decisions from the user

- Sites-first supported ChatGPT collaboration; Android first; persistent cross-device
  projects even when the Windows PC is off; knowledge/canon/review/wiki/atlas plus audio.
- Personal use supersedes the commercial-product goal and mandatory offline-only central
  storage. Local worker/recovery remains local. Respect all rights/license/security terms.
- No deployed Site and no Windows app exist (user clarified). No Windows/Android device
  is attached here. A portable foreground worker harness can test a protocol before a
  full tray/installer, but Linux results cannot establish Windows compatibility.
- Add a final Phase 0 deliverable: a copy-ready Sites deployment prompt (task S0-08).
  Finalize it against verified capabilities/cost/auth/storage decisions; generating a
  prompt is not deploying or approving paid hosting. Conditional draft is explicitly labeled.
- Every AI model download remains separately gated by exact artifacts, sizes, licenses
  and purpose. No significant dependency installs, cloud GPUs, paid APIs or remote wiki/
  software publication are authorized. Apache-2.0 project source license remains intact.

## R-D01 — Direct Sites first; evidence required

No Sites deployment/runtime/storage interface is available in this session and the
exact product/API contract is not identified. Direct integration is **unverified**, not
proven unsupported. Do not label Apps SDK or an ordinary web app as Sites. Official
source retrieval commands were not executed because automatic permission review failed
(capacity, deadline, permitted retry capacity). No unsupported session automation.

## R-D02 — External bridge only a conditional candidate

One durable HTTPS queue + private audio store may be the smallest bridge if a supported
Site can call it. Hosting/auth/storage/costs and platform changes need approval; no
provider selected/deployed. A bridge that cannot integrate with Sites does not meet the
mission. If necessary, propose the smallest supported mobile web/ChatGPT integration
fallback and stop for approval. Do not silently adopt it.

## R-D03 — Isolated disposable protocol experiment

A separate local queue/browser client/portable worker lives in backend/voxfoundry/poc,
with explicit one-owner/device auth, request idempotency, leases, attempts, bounded
validated WAV uploads and durable output. It uses test tones, not TTS. Existing user
libraries and app migrations are untouched. The experiment does not claim Sites,
Windows, Android, Internet TLS or deployment evidence. No new dependencies/models.

## R-D04 — Central graph/canon and portable ownership

One authoritative project graph, typed relationships/provenance and immutable revision
history serve many views. Autosave, sync and session restoration are separate. Canon
promotion/review and external publication are separate explicit actions. App-owned AI
sessions do not imply access to external ChatGPT history. Project exports must round-trip
without original DB/vendor UI. Direct Sites store versus hosted bridge store remains
conditional on supported capabilities, data portability, privacy and costs.

## Open decisions / blockers

1. Identify the intended Sites product and inspect current official contracts; exact
   project/deployment link cannot be supplied yet because nothing is deployed.
2. Restore working automatic permission review and apply required documentation host
   access. Source fetch and live loopback/browser commands were rejected before execution
   by the review service, not judged unsafe by policy. The normal pure-component tests run.
3. Verify direct worker/files/ChatGPT/mobile contracts. Decide bridge/fallback only from
   evidence and explicit approval. Hosting/storage/egress costs and quotas unverified.
4. Run actual Windows harness and Android play/download/worker-off availability gates.
5. Read map/Wiki/AI primary docs/current licenses; no map data or wiki push authorized.
6. Finalize the Sites deployment prompt after evidence. S0-08 remains an end-of-Phase-0
   deliverable; a conditional preflight draft does not satisfy deployable integration.

## Audit

Last audit: revised Phase 0 available-work boundary, POC commit 9893611, after prior
implementation 77a2165 and audit 8bf7cd9. Preserved old history/source; reviewed scope, evidence labels, Sites
and model/cost gates, isolated credentials/data, queue fencing and manual device tests.
Exact tests/outcomes are in VALIDATION. No full feasibility/phase exit approval exists.
Next audit: ten development commits after this scope-reset audit documentation commit
or the next major phase boundary, whichever comes first. New task IDs use S prefixes;
old P task IDs remain historical and must not be reinterpreted as completed Site work.

Environment draft: documentation host additions saved without dropping package-manager
presets. Startup instructions now follow revised tasks/evidence, and the old automatic
full local-app install script was cleared to avoid unnecessary installs in Phase 0.
Existing dependencies remain on disk; no new installation is needed for the verified
component tests. Review/save environment settings and publish the cloud snapshot
separately if retaining it; no environment/Site/software publication was performed.

## Continuation evidence and limits

- Execution recovered enough to run the initial live POC suite and primary source
  fetch. Test run: 7 passed/5 fixture failures, not an integration pass. Corrected
  httpx context lifecycle and CSP-compatible polling; kept the CSP intact. Reruns
  blocked by renewed review timeouts/capacity; S0-I2 reopened, S0-03 remains incomplete.
- Browser cases observed real separate Linux worker completion/upload before polling
  assertion failures. Independent FFmpeg decode succeeds. Neither result proves actual
  Windows, Android playback/download, ChatGPT runtime or Sites integration.
- Official OpenAI examples document MCP tool/widget servers and production server-side
  persistence. This is a supported-documentation candidate, not Sites identification
  or platform-change approval. A single hosted MCP/application service could share
  knowledge/queue/private files with a scoped outbound worker API if explicitly chosen
  and verified; no server/SDK dependency or hosting was adopted.
- GitHub's official wiki source verifies the separate wiki Git workflow and initial
  page prerequisite; no wiki auth/read/write operation was performed. Leaflet's code
  license is BSD 2-Clause, separate from map imagery/tiles/marker rights. Pindrop/full
  OpenAI docs remain proxy-blocked and unread; price/account/device limits unverified.
- No new approvals, downloads or publication. Final S0-08 deployment prompt remains
  conditional until platform and required evidence are available.

Continuation checkpoint: test correction commit bfd755a; source/evidence/tracker updates
are in the following documentation commit. Cloud startup draft updated successfully;
network/runtime changes and snapshot publication remain unconfirmed/unperformed.

## GitHub source synchronization authorization

The user explicitly authorized pushing all committed work to FatherNoTimeGames/VoxFoundry
after being told commits were local only. Origin main was fetched and confirmed an
ancestor of the local work; use a normal fast-forward push, never force. This authorizes
source synchronization for this batch, not a Site deployment, software Release, Wiki
publication, paid hosting or model downloads. Phase 0 limitations remain unchanged.
The push result is verified separately after this authorization record is committed.
