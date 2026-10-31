# Sites platform contract checkpoint — 2026-10-31

Task S0-02: **documentation verified in part; exact hosting setup and live behavior
remain blocked/unverified**. Follow-ups add binding/build metadata only; application
routes, schema, environment, Site resources and credentials are unchanged. Audio stays deferred.

## Follow-up: migration-sidecar packaging resolved

Primary source O13 is OpenAI's public tooling repository, pinned to
[`7eb9d4b9cf93ad7e64aebc8a5ca70e29ec2cfb94`](https://github.com/openai/sites/tree/7eb9d4b9cf93ad7e64aebc8a5ca70e29ec2cfb94).
Unlike the earlier unavailable installed-helper paths, these GitHub reads succeeded.
Actually accessed the production plugin README, package, `src/index.ts` and upstream
test source, generator `src/index.ts`, D1 `drizzle.config.ts` / `db/schema.ts`, and
the base template package. The upstream test source was inspected, not run as a suite.

The [plugin README](https://github.com/openai/sites/blob/7eb9d4b9cf93ad7e64aebc8a5ca70e29ec2cfb94/packages/sites-vite-plugin/README.md)
and [production hook](https://github.com/openai/sites/blob/7eb9d4b9cf93ad7e64aebc8a5ca70e29ec2cfb94/packages/sites-vite-plugin/src/index.ts)
establish that builds replace `dist/.openai`, copy the required source hosting manifest,
and recursively copy optional `drizzle/**` into `dist/.openai/drizzle/**`.
This resolves the **copy/discovery location**, not hosted parser validation.
`sites/studio/scripts/build.mjs` now follows that copy behavior in its native build.

Executed the original pinned plugin's `closeBundle` hook directly with Node's native
TypeScript support; no Vite installation/server was needed. Four disposable copy
checks against Studio passed: SQL/journal/nested snapshot bytes match; no-Drizzle
build removes stale files; missing manifest rejects; rebuild after failure restores
current metadata only. Fixtures were explicitly marked copy-only, were deleted,
and are not migration history. No local sign-in hook was invoked.

The official [D1 config](https://github.com/openai/sites/blob/7eb9d4b9cf93ad7e64aebc8a5ca70e29ec2cfb94/packages/create-sites/templates/addons/d1/drizzle.config.ts)
uses SQLite, `db/schema.ts` and output `./drizzle`; the generator pins
`drizzle-kit@0.31.10` / `drizzle-orm@0.45.2` and adds `db:generate`.
Those dependencies are absent. Their install has not been authorized, and neither
CLI nor initializer ran. There is no generated application SQL/journal/snapshot;
`schema.sql` remains the reviewed local test schema. Do not synthesize metadata.

Remaining concrete steps: approve the pinned build tools before installing; map and
generate the current schema; review SQL/metadata for ownership keys and constraints;
apply only to a fresh local DB and run route/reopen checks against that generated
schema. Then use the supported lifecycle helper after the separate account/budget
and deployment gates. The public Vite plugin does not replace that helper or prove
the native Worker deployment archive is accepted. No Site/D1 resource was created.

Earlier migration-packaging unknowns below are historical where superseded here.

## Follow-up: manifest format resolved

The separate official [Manage a site page](https://learn.chatgpt.com/docs/sites/managing-a-site)
provides the missing binding example and permits a starter to omit identity before
registration. Earlier research missed this subpage. The source now contains:

```json
{
  "d1": "DB",
  "r2": null
}
```

This supersedes the **binding-format** unknowns in the original checkpoint below.
The builder validates/copies this manifest, never generates a fake project ID, and
still reports that the output is not a deployment archive. The change creates no
Site or database and adds no migration metadata. Runtime application code is unchanged.
Migration discovery/metadata and lifecycle packaging remain unresolved.

Additional reads: the official Create a site, Data and connections and Publish and
share subpages. They did not supply the needed migration packaging contract. The
installed starter's `scripts/sites-env.mjs`, `scripts/run-framework.mjs` and
`scripts/build-verified.sh` were readable, unlike the named lifecycle helper/config
paths. These do not replace the missing migration/parser assets. Drizzle, Wrangler
and Vinext were unavailable to the project; bounded runtime inspection found none.

Search also surfaced package/mirror/issue results. They were not adopted as binding
authority. The npm package page returned 403 and its registry endpoint was not
accessible through the web tool; no package was downloaded or executed. No
environment settings, proxy, policies or installed packages were changed.

A bounded read of the public package metadata using the executor's inherited
proxy/TLS configuration also failed with `URLError`. It downloaded no package and
made no configuration change. This does not establish any package's provenance or
authorize using a replacement deployment path.

## Original checkpoint (binding-format gap superseded above)

## Documented contract and current source

| Area | Accessed evidence | Implication for VoxFoundry | Still unverified |
| --- | --- | --- | --- |
| Identity | Installed Sites identity reference and starter README: private Sites authenticate visitors; server receives Site-scoped user ID/email; sign-in/out/callback are dispatch-owned; sign-in is top-level navigation. | `sites/studio` uses the stable ID, owner allowlist and same-origin writes. Its anchors use platform routes. Do not replace this with custom OAuth. | Actual account login/return, header stripping/injection and owner access on private Sites; Android session behavior. |
| Structured data | Installed storage reference: logical D1, schema-only migrations, one statement per prepare and batches; follow-up resolves the binding format. | The prepared text foundation expects `env.DB`; its mutation/revision/replay transactions are locally tested. No user-library migration is intended. | Migration discovery/metadata, lifecycle packaging, live D1 execution and durability/consistency. |
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

The needed artifact is supported Sites lifecycle/starter tooling **including its
migration integration**, accessible to the selected executor, or equivalent official
migration packaging documentation. The manifest format no longer needs guessing.
No runtime repair, plugin reinstallation or alternative platform was attempted.

## Remaining acceptance and next action

1. Obtain the supported migration configuration and lifecycle assets.
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
S0-07/S0-09 and Site completion remain open. The follow-up above records the new
binding evidence; remaining migration setup needs new tooling/schema evidence.
