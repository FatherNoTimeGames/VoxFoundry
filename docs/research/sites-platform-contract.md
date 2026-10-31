# Sites platform contract checkpoint — 2026-10-31

Task S0-02: **documentation verified in part; exact hosting setup and live behavior
remain blocked/unverified**. This checkpoint changes no implementation, environment,
Site, storage, access policy or credentials. Windows audio stays deferred.

## Documented contract and current source

| Area | Accessed evidence | Implication for VoxFoundry | Still unverified |
| --- | --- | --- | --- |
| Identity | Installed Sites identity reference and starter README: private Sites authenticate visitors; server receives Site-scoped user ID/email; sign-in/out/callback are dispatch-owned; sign-in is top-level navigation. | `sites/studio` uses the stable ID, owner allowlist and same-origin writes. Its anchors use platform routes. Do not replace this with custom OAuth. | Actual account login/return, header stripping/injection and owner access on private Sites; Android session behavior. |
| Structured data | Installed storage reference: declare a logical D1 binding, use `DB`, schema-only migrations, one SQL statement per prepare and batches for multiple statements. | The prepared text foundation expects `env.DB`; its mutation/revision/replay transactions are locally tested. No user-library migration is intended. | Exact ESM `d1` JSON structure, migration discovery/metadata, live D1 execution and durability/consistency. |
| Files | Installed storage reference: R2 server-side storage, normally `BUCKET`; unused bindings stay null. | Text-only foundation does not require R2 or uploads. Future file features must authorize reads/writes and bound uploads. | Actual R2 binding shape, private upload/download/retention; not required to test basic text editing. |
| ChatGPT tools | Installed MCP reference: `mcp` capability and a stateless JSON-RPC `POST /mcp`; Sites authenticates callers; app enforces record permissions. | Supported route for future owner-authorized library/context tools. No MCP endpoint is implemented in the current slice. No external chat history or API credits are assumed. | Plugin creation/connection, usable tools in the intended account, actual owner identity and record isolation. |

MCP's installed contract lists `server/discover`, `tools/list`, `tools/call` and
version `2026-07-28`. The capability is added only when an actual server exists.
Publication/connection is a separate step; a documented capability is not an
installed, connected or successfully tested VoxFoundry tool.

## Exact references successfully accessed

Installed skill resources:

- `skill://plugin_connector_1p_689987207de08191979cf68eca2941c6/sites/SKILL.md`
- `skill://plugin_connector_1p_689987207de08191979cf68eca2941c6/sites/references/storage.md`
- `skill://plugin_connector_1p_689987207de08191979cf68eca2941c6/sites/references/identity-and-secrets.md`
- `skill://plugin_connector_1p_689987207de08191979cf68eca2941c6/sites/references/site-mcp-server.md`
- `skill://plugin_connector_1p_689987207de08191979cf68eca2941c6/sites/references/troubleshooting.md`
- The starter README was accessed previously; its `package.json` was read today.
  Its framework/migration scripts require dependencies; none were installed here.

Public primary sources successfully accessed through the supported web tool:

- O5: [Sites guide](https://learn.chatgpt.com/docs/sites), reached through the official
  Help Center's developer-guide link. Cost findings are recorded once in [costs](costs.md).
- O6: [Creating and using Sites](https://help.openai.com/en/articles/20001339-creating-and-using-chatgpt-sites).
- O7: [Hosting a plugin with Sites](https://help.openai.com/en/articles/20001547-hosting-a-plugin-with-chatgpt-sites):
  Site-hosted MCP tools become usable through a separately connected plugin after
  owner publication. Site access and plugin connection are distinct. No live proof.
- O8: [OpenAI Sparkboard showcase](https://developers.openai.com/showcase/idea-intake):
  example prompt names DB, null R2 and Drizzle migrations, but does not provide the
  exact ESM manifest/migration schema. It is example guidance, not a parsed schema.

The public guide's visible page contained no `hosting.json` or starter setup match.
It did not resolve the internal hosting configuration. Do not turn prose naming a
binding into a guessed JSON value/type or synthesize migration metadata.

## Concrete executor and source access limits

- Executor-owned skill inventory is empty, while cloud Sites skills and native Sites
  tools are available. This does **not** mean the Sites plugin is uninstalled.
- Lifecycle helpers were not found in inspected workspace/shared or executor program
  locations, including hidden paths under `/opt/codex`, `/tmp`, `/workspace`, `/mnt`.
  No known plugin installation root was returned. No secrets or credential values
  were read. `sites-preview` is unavailable.
- Skill-provider reads failed for the named `project-setup.mjs`/`build-site.mjs`
  helper paths and starter `drizzle.config.ts`; earlier starter config/auth source
  reads failed too. Their contents were **not** accessed or executed. Main/reference
  pages and starter `package.json` did succeed, so this is partial asset access.
- Native read-only owner Site inventory returned no VoxFoundry title/slug match,
  with no next page. No existing Site identity was selected and no resource created.
  This does not identify the selected account's plan, budget or remaining allowances.

The needed artifact is the supported Sites lifecycle/starter tooling **including its
exact manifest parser and migration integration**, accessible to the selected
executor, or equivalent official schema documentation. No runtime repair, plugin
reinstallation, alternative platform or fabricated manifest was attempted.

## Remaining acceptance and next action

1. Obtain the exact supported binding/migration configuration and lifecycle assets.
   Check `sites/studio/schema.sql` against that path; do not apply it to existing data.
2. Resolve account/allowance applicability using [the dated cost findings](costs.md)
   and the intended account. The current tools do not expose plan-specific billing.
3. Only after applicable deployment/cost authorization, register one private Site,
   persist the actual ID, configure the real owner ID and isolated DB, then publish
   through supported source/package tools. This checkpoint authorizes none of that.
4. Verify sign-in, unauthorized reads/writes, save/reload, revision/conflict/retry,
   retained data and real Android use. Then verify any separately implemented MCP
   tools through the Site-created plugin. Keep receipts of observed results.

No live Site, D1/R2, browser, Android or MCP test ran. Existing 19 foundation tests
were not rerun for this source-free research batch. S0-02 is not marked done;
S0-07/S0-09 and Site completion remain open. This report prevents repeated source
guessing: resume the blocked configuration step only with new tooling/schema evidence.
