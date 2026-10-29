# Sites deployment prompt — conditional draft

User-requested final Phase 0 task: **S0-08**. This is a preflight/template, not the final
platform-specific deployment prompt: the Sites product/APIs, hosting and real integration
are not verified. Finalize only after S0-07 evidence; never copy unsupported assumptions
into a deployment. Do not enter secrets into the prompt. Deployment/cost approval remains
separate. No Site or Windows app is assumed to exist.

Copy-ready preflight text for the intended supported builder:

```text
Create only a disposable VoxFoundry audio-transport proof of concept, not the full app.

First identify this Sites product/runtime/version and cite its current official supported
capabilities for ChatGPT collaboration, authenticated persistent storage, external
worker APIs, private file upload/stream/download, Android access and deployment costs.
Do not invent internal endpoints, direct DB/file access or access to ChatGPT history.
If a capability is unavailable or undocumented, report the gap and stop for a decision.
Do not silently substitute a different product or a paid AI API.

Use the verified configuration below only after the feasibility report is approved:
- Sites product/build: {{verified product/build and docs}}
- Direct supported job/file APIs OR explicitly approved bridge: {{decision and contract}}
- Authorized disposable environment/project: {{identifier}}
- Hosting/storage/retention/quotas/expected costs: {{verified values and approval}}
- Owner login and scoped worker device auth: {{supported scheme; secret references only}}

Implement a phone-first interface with a short test passage, explicit approval checkbox,
submit/progress/retry controls, last-worker-contact indicator, completed audio player and
explicit download. Use 44px tap targets, readable compact 360–390px layouts, keyboard/
screen-reader support, no hover-only controls; enhance tablet/desktop. Clearly label
synthetic test tones as non-speech. Do not implement unrelated app features.

Persist requests/results on approved central storage independently of the Windows PC.
Bind idempotency IDs to immutable approved text/config hashes; keep attempts/finite
leases/heartbeats and reject stale completions. Worker communication is outbound HTTPS,
not an exposed home port or browser-session automation. Do not give worker credentials,
DB admin keys or long-lived private audio URLs to client code.

Use the repository's portable test-worker contract only after adapting it to supported
platform auth/endpoints. The current local harness is not a deployed Sites adapter.
Use a lightweight tone generator or an already approved local engine; no model or
significant dependency download without exact purpose/size/license approval.

Validate bounded staged uploads and format/hash before atomic success; support private
ranged playback/download after worker disconnection. Retain queue/files across restarts.
Use TLS, owner/project authorization, scoped/revocable device identity and appropriate
CSRF/CORS/CSP rules for the actual Sites runtime; do not assume loopback cookies work
inside a cross-origin widget. No public read bucket or wildcard credentialed CORS.

Test request persistence, wrong/expired credentials, duplicate submit/upload, lost
acknowledgment, worker/bridge restart, lease expiry/reclaim, retry budget, corrupt/truncated
WAV, unauthorized file reads and limits. On real Windows 10 run the companion; on real
Android play/seek/download/open offline, then confirm hosted access while the PC is off.
Phone emulation and Linux execution must remain labeled as such.

Report exact verified results, unrun/manual steps, account/hosting/storage/egress costs,
security limitations and rollback/cleanup for the disposable project. No canon promotion,
GitHub Wiki push, full app expansion, paid hosting or public software release is implied.
Stop at the Phase 0 approval checkpoint. If required endpoints/platform/device access are
unavailable, deliver the concrete blockers and next steps instead of claiming success.
```

Verified preflight update: OpenAI's Apps SDK example README documents MCP widgets/tools
and server-side persistence. If the intended builder is Apps SDK, identify it explicitly
and use its current official auth/runtime docs; do not relabel that app as a different
Sites product or assume storage is included. Direct Site APIs and actual Android/Windows
proof are still unresolved, so S0-08 is not final.
