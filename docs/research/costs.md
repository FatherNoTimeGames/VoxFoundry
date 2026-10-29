# Cost and resource assessment

Status: current hosting/platform/pricing terms unverified; no provider selected. See
REFERENCES O1–O4. The local component experiment initiated no new service deployment,
paid API calls, cloud GPU or model download. Existing ChatGPT/cloud-development plan,
Internet, disk and electricity costs are outside that statement.

| Item | Current experiment | Production decision required |
| --- | --- | --- |
| ChatGPT collaboration | No app runtime/API call made | Verify Sites/account/tool usage entitlement and quotas; Plus is not assumed API credit |
| Site/auth/database | Not deployed | Confirm plan inclusion, persistence, inactivity/sleep, backups, connection limits |
| Optional bridge | Local loopback code only | Only if necessary/supported/approved; HTTPS compute, durable disk/DB, ops and backup cost |
| Audio storage/downloads | Temporary local test files | Verify private storage, egress/retention/streaming/range limits; no free-tier permanence claim |
| Local worker | Tone generator, no ML dependencies installed | PC power/driver/runtime/model disk and RAM/VRAM; no cloud GPU required |
| Map/Wiki | No requests/data/push performed | Licensing/plan/auth/API limits and permitted data/export rights |

Planning arithmetic, not vendor prices or hardware benchmarks:

- POC WAV: 2 seconds × 16000 samples/s × 2 bytes plus 44-byte header = **64044 bytes**.
- Mono 16 kHz 16-bit PCM: **115.2 MB/hour** before containers/metadata/backups.
- A hypothetical 64 kbit/s lossy export is about **28.8 MB/hour** before metadata.
  Bitrate/format are not quality-approved presets.
- Monthly media disk = retained source/render/export versions × duration × bitrate;
  egress = bytes per play/download × count. Duplicates/backups/retention multiply usage.
- Worker electricity = measured wall-power kW × processing hours × local tariff;
  RTX 3060 speed/power has not been measured here.

Ongoing production cost is **unknown**, not promised free. Prefer supported included
capabilities or the smallest durable service, but do not trade away retention/security
for an unverified free tier. Present exact provider/plan/quotas and incremental costs
for approval before deploying; never silently add a paid API to preserve ChatGPT UI.
