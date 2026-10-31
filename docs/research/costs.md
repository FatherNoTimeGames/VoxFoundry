# Cost and resource assessment

## Current public terms checked — 2026-10-31

The [official Sites guide](https://learn.chatgpt.com/docs/sites) says hosting is free
through December 31, 2026; metering is planned for January 1, 2027. Proposed monthly
usage before plan allowances:

| Resource | Proposed credits |
| --- | --- |
| Storage-enabled Site, including empty database | 25 / month |
| Traffic | 16 / 100,000 requests |
| Database storage | 150 / GiB-month |
| File storage | 3.75 / GiB-month |

Illustration only: 10,000 requests + 10 MiB records + no files gives approximately
28.065 credits/month before allowance. Proposed rates can change; no dollar conversion
or account allowance is established. Building/editing consumes Codex usage separately.

The [Help Center](https://help.openai.com/en/articles/20001339-creating-and-using-chatgpt-sites)
currently describes hosting as included for personal Plus/Pro and waived for Enterprise.
Those current terms and the guide's proposed future rates concern different periods.
Business terms and the selected account/remaining allowance are unconfirmed. A plan
question is pending; no account type was inferred from Site names or repository ownership.

**S0-D1 is partially resolved, not approved:** public pricing is now available, but
account applicability/budget and future retention still need confirmation. No new
Site, database, file store, credits purchase or paid service was created. Existing
development-account usage is not claimed free. No hosting permission is implied.

## Historical assessment and deferred audio arithmetic

The older unknown-pricing statements below describe the prior session and are
superseded for current public terms by the dated check above. Audio/bridge estimates
are preserved planned-feature research, not an active Site dependency.

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
