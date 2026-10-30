# Planned features after the Site

## Windows audio connection — deferred 2026-10-30

The user asked to take the Windows audio connection out of the current work and
finish Site functionality first. This is deferred scope, not cancellation of the
audiobook-studio goal and not a successful audio integration test.

The Site must be useful and independently complete without an installed Windows
companion, a paired device, a Site service credential, a worker queue or local audio
generation. Do not show active narration/worker setup controls or deploy the old
tone experiment as the Site's main application. Generic project/document/file
features do not depend on the Windows connection.

Preserved research, excluded from the active Site entrypoint:

- `sites/phase0/`: direct-Sites audio transport experiment and portable tone worker.
- `backend/voxfoundry/poc` and `tests/poc`: original local transport experiment.
- `docs/POC.md` and `docs/research/sites-worker-integration.md`: protocol/manual steps.
- Original task IDs S0-03 and S0-06, and narration/audio/distribution phases 6–8.

These files remain available for later review. Their tests and validation history
remain evidence of component behavior only; nothing is deployed by preserving them.

When the feature is resumed, plan and verify:

1. Windows companion compatibility and explicit owner-approved script/config jobs.
2. Private Site ingress, independently scoped/revocable device identity, leases,
   idempotency, progress, cancellation/retry and durable local/cloud recovery.
3. Windows-only inference and FFmpeg; exact model/voice artifacts, sizes, rights,
   licenses and any costs approved before downloads or provider selection.
4. Validated private audio uploads, retained originals, bounded storage and independent
   streaming/download access while the worker is offline.
5. Real Windows execution and real Android playback/seek/download/offline checks.
6. Later narration editing/mastering, MP3/M4B exports and optional tray/installer work.

No actual Windows/audio/device test has passed. The 25 original and 29 reviewed
component tests remain separate from hosted Sites/D1/R2/private-dispatch tests and
real-device validation. Recheck the implementation and platform contracts before
resuming; the preserved prototype is not production authorization.

## Site completion checkpoint before resuming audio

Complete and verify the active Site features: owner sign-in, projects and writing,
durable saves and cross-device visibility, knowledge records/sources/search, revisions
and portable restore, supported ChatGPT tools and proposal/canon review, the lore
atlas, and any enabled Wiki integration. Test touch, keyboard and readable mobile
layouts on actual Android; preserve distinct evidence for browser emulation.

Record implemented, failed, unavailable and deferred features explicitly. Verify
private access, persistence while the PC is off, exports/restoration, costs and
remaining limits before calling the Site complete. Site feature completion is not
automatically a public launch, a paid deployment or approval to resume audio work.
