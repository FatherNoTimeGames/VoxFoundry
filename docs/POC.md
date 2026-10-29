# Disposable audio transport experiment

This is a local prototype, **not a ChatGPT Site, deployed bridge, Windows tray app,
TTS engine, or verified Android integration**. It uses existing Python dependencies
and a two-second deterministic tone. No models, cloud services or significant new
packages were installed. Seven component tests pass. The first live run executed
(7 passed, 5 fixture failures); fixture corrections await a permitted rerun. Separate Linux worker upload/completion
was observed; final browser playback/download assertions remain unverified.

## Files and isolation

Code: `backend/voxfoundry/poc/{store,bridge,worker,audio}.py` plus a small phone-first
HTML/JS/CSS client. Tests: `tests/poc`. POC roots must stay outside the checkout and
outside existing manuscript libraries. Use fresh disposable directories. Generated
credentials/SQLite/staging/audio stay there and must never be committed or pasted into
chat. Existing application library/schema is not touched. The old app is retained.

The bridge creates one private local worker credential file. POSIX file permissions
are restricted; Windows ACL behavior is unverified and must be checked manually.
This fixture pairing is not production OAuth/device enrollment/revocation. Only
loopback is bound; do not expose it or forward a home port. An external bridge would
need an explicitly approved supported deployment/auth/TLS/storage design.

## Run only after execution is available

Use the existing prepared environment; no frontend/Node build is required for this
POC. The standalone launcher/manual commands remain instructions to verify; the live
test observed the worker subprocess but did not complete the full playback/download
suite. New Windows dependency installation requires size/purpose review; no installer exists yet.

```sh
# Terminal 1, repository cwd; launches a local browser with an unlogged one-time token
.venv/bin/python -m voxfoundry.poc.bridge --data /tmp/voxfoundry-poc-bridge

# Terminal 2, after bridge initialized; credential is passed by path, never printed
.venv/bin/python -m voxfoundry.poc.worker --bridge http://127.0.0.1:8766 \
  --credentials /tmp/voxfoundry-poc-bridge/worker-credential.json \
  --data /tmp/voxfoundry-poc-worker --poll
```

Windows equivalents use `.venv\Scripts\python.exe` and private directories outside the
installation, e.g. `$env:LOCALAPPDATA\VoxFoundryPocBridge` / `VoxFoundryPocWorker`.
They are **unrun examples**, not proof of Windows support. A worker run is a foreground
portable harness; tray UI/build/distribution comes later. For local Windows testing
run bridge+worker on that machine; actual Site testing needs the verified approved
hosted integration, which this loopback-only bridge does not provide.

Submit an approved disposable passage, run the worker, refresh status, play/download
the tone, stop the worker and confirm retained file access. Tone output is 64044 bytes
of WAV (2s, mono, 16 kHz PCM), not a narration of the passage. For a headless bridge
`--no-browser` only exposes health until an authenticated launcher session is established.
Keep tokens out of logs. Stop only processes you started.

## Checks and limits

```sh
# Verified seven tests: no network or browser
.venv/bin/pytest -q tests/poc/test_queue.py tests/poc/test_worker.py

# First run had 5 fixture failures; corrected full rerun still needed
.venv/bin/pytest -q tests/poc -o faulthandler_timeout=30
```

State-machine tests use a transport double. The initial live run observed worker-process
claim/render/upload/completion in three viewports, then failed in CSP-incompatible test
polling; the HTTP fixture also reopened a client incorrectly. Those fixes retain CSP
and were checked by lint/compile and a mock-transport lifecycle check. Live re-verification
of auth/limits/ranges/restart and browser play/download remains pending. No local test
can establish actual Sites/Windows/Android integration.

Queue requests use a unique idempotency ID bound to text digest, three automatic lease
attempts, explicit retry extension preserving attempt history, monotonically reported
progress and a fenced completion. Worker SQLite records generated/acknowledged results;
cache reuse handles restart/lost lease without unnecessary rerendering. No exactly-once
inference guarantee is claimed. Uploads are capped at 256 KiB and validated before
success; partial/orphan staging is retained. The worker uses HTTPS for non-loopback
origins, preserving normal TLS trust and proxies, but no hosted endpoint is configured.

Before production: proper device pairing/revocation, scoped multi-project auth, TLS/
origin policy for actual Sites, rate limits/quotas, CSRF/streaming URL policy, storage
backup/retention and monitoring, adversarial upload tests, Windows ACL/durability and
actual Android playback/download. See research/sites-worker-integration.md manual gates.
