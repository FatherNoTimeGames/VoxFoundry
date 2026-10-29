# Sites / Windows worker feasibility

Status: **direct Sites integration unverified; no platform adoption decision**.
The user confirms no Site has been deployed and no Windows companion has been built.
This cloud session exposes no callable Sites deployment, database, file-storage or
ChatGPT runtime API. No Windows PC or actual Android device is attached. Absence of a
tool is not proof that the platform lacks a capability.

## Evidence and capability gates

| Capability | Current evidence | Required proof |
| --- | --- | --- |
| Exact Sites product/official contract | Product URL/version not identified | Identify platform/account capabilities and official docs |
| Site creation/deployment | No Site supplied; no deployment tool available | Create disposable Site using supported route; record URL/version |
| Persistent project/job storage | No Sites-specific persistence tested | Save job, restart client/server, retrieve with authorized identity |
| Worker-facing server API | No documented/tested endpoint available here | Windows client obtains scoped credential; authorized read/write; unauthorized fails |
| File upload, retention and playback URLs | No Sites file API verified | Upload audio, authenticated/ranged playback/download, expiry/retention tests |
| Cross-device auth, ChatGPT context/tools | Unverified | Same project on Android/Windows; supported app-owned sessions/context/actions |
| Costs/quotas/hosting while PC off | Unverified | Current terms/pricing, file limits, egress, sleep/retention/inactivity policy |

Official OpenAI/API and map documentation retrieval was attempted through the supported
permission flow. Automatic approval review failed (capacity, then deadline; the allowed
retry also hit capacity). Those commands **did not execute**; this is not a source's
HTTP response or proof of unsupported APIs. Required host additions are saved in the
environment draft; runtime access/application remains unverified. See REFERENCES.

## Preferred direct route (conditional)

Use Sites-supported server actions, authenticated persistence and durable file storage
only after verifying a documented worker integration. A worker can poll a supported
external HTTPS API; it cannot read an internal Sites database, a user's browser session,
private files or undocumented internal endpoints by assumption. Validate scoped device
identity, short-lived leases, conditional completion, upload limits, private streaming
and direct download on actual Android. Keep completed audio available independently
of the Windows process. Site deployment alone is not an end-to-end pass.

## Smallest external bridge candidate (approval required)

If direct supported APIs are absent or insufficient, propose one small authenticated
HTTPS service with durable job metadata + private object storage, exposed to the Site
through a **supported** integration. The worker uses outbound HTTPS polling, bounded
leases/heartbeats, fenced uploads and idempotent commits. This removes the need for
inbound home ports. A single-host SQLite/persistent disk can be sufficient for a personal
experiment; managed database/object services may fit verified platform capabilities.
No ephemeral disk or multi-replica shared SQLite. Do not select/deploy a paid host or
replace Sites silently. If Sites cannot even call/render the bridge with appropriate
authorization, this bridge alone does not solve the product requirement.

A regular authenticated mobile web app with a supported ChatGPT app/tool integration
is a candidate fallback, **not approved or proven equivalent**. Preserve ChatGPT as the
collaborator only through documented mechanisms; no mandatory paid inference API or
unsupported account/session automation. Obtain explicit platform-change approval.

## Local disposable experiment

`backend/voxfoundry/poc` implements a separate loopback browser client, persistent SQLite
queue, portable outbound worker harness, private WAV objects and owner/device checks.
It generates a deterministic two-second **tone**, not speech. It never opens a home
network port or connects to Sites. Existing local manuscript libraries are untouched.
Local HTTP/browser evidence can validate only component/protocol behavior. It cannot
verify hosted TLS, Sites UI/runtime, Windows execution, mobile OS downloads or actual
cross-device synchronization. Exact test outcomes live in VALIDATION.

## Manual end-to-end gates

1. Identify Sites and get official API/storage/auth/ChatGPT documentation; verify costs.
2. Decide direct route or explicitly approve the smallest feasible bridge/fallback.
3. Create disposable hosted Site/queue/storage, scoped owner/device auth and HTTPS.
4. Run the harness on Windows 10 with its private credential provisioned securely;
   submit an explicitly approved test passage from the Site, not this local browser.
5. Disconnect/reconnect the worker before/after rendering and before/after upload;
   verify leases, retry budget, duplicate prevention and progress across restarts.
6. On a real Android phone, play/seek the returned audio with a user gesture and save
   the download; reopen it offline and compare bytes. Test tablet/desktop as well.
7. Stop the worker/PC; confirm the Site and uploaded file still work. Restart Site
   components and reauthenticate; confirm durable jobs/assets and access controls.
8. Test expired/revoked device credentials, another user/unauthed browser, upload limits,
   stale completion and short-lived URL expiry. Record evidence/versions and clean up
   only the disposable fixture. Full success requires all mandatory gates.
