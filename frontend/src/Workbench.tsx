import { useEffect, useRef, useState } from "react";
import { api } from "./api";
import { Dictionary } from "./Dictionary";
import type {
  Props,
  Doc,
  Node,
  Workspace,
  Snapshot,
  Preview,
  Preset,
} from "./manuscriptTypes";

const kinds = [
  "part",
  "chapter",
  "episode",
  "manuscript",
  "research",
  "reference",
  "note",
];

export function Workbench({
  projectId,
  readOnly,
  canRestore,
  onGuardChange,
  onImported,
  onRestored,
}: Props) {
  const base = `/projects/${projectId}`;
  const [workspace, setWorkspace] = useState<Workspace>();
  const [document, setDocument] = useState<Doc | null>(null);
  const [text, setText] = useState(""),
    [dirty, setDirty] = useState(false),
    [saving, setSaving] = useState(false);
  const [busy, setBusy] = useState(false),
    [error, setError] = useState(""),
    [notice, setNotice] = useState("");
  const [structureDirty, setStructureDirty] = useState(false);
  const [snapshots, setSnapshots] = useState<Snapshot[]>([]),
    [snapshotId, setSnapshotId] = useState(""),
    [preview, setPreview] = useState<Preview | null>(null);
  const [presets, setPresets] = useState<Preset[]>([]);
  const [revisionId, setRevisionId] = useState(""),
    [revisionPreview, setRevisionPreview] = useState<{
      text: string;
      draft_version: number;
    } | null>(null);
  const [script, setScript] = useState<{
    units: {
      id: string;
      text: string;
      spoken_text: string;
      start: number;
      end: number;
    }[];
  } | null>(null);
  const live = useRef(true),
    selected = useRef<Doc | null>(null),
    latest = useRef(""),
    saved = useRef(""),
    draftVersion = useRef(0);
  const blocked = useRef(false),
    flight = useRef<Promise<boolean> | null>(null);
  useEffect(() => {
    live.current = true;
    return () => {
      live.current = false;
      onGuardChange(false);
    };
  }, []);
  useEffect(
    () => onGuardChange(dirty || saving || structureDirty),
    [dirty, saving, structureDirty, onGuardChange],
  );
  async function refresh() {
    const [w, s, p] = await Promise.all([
      api<Workspace>(base + "/workspace"),
      api<Snapshot[]>(base + "/snapshots"),
      api<Preset[]>("/presets"),
    ]);
    if (live.current) {
      setWorkspace(w);
      setSnapshots(s);
      setPresets(p);
    }
    return w;
  }
  async function action(fn: () => Promise<void>) {
    setBusy(true);
    setError("");
    setNotice("");
    try {
      await fn();
    } catch (e) {
      if (live.current) setError((e as Error).message);
    } finally {
      if (live.current) setBusy(false);
    }
  }
  useEffect(() => {
    void action(async () => {
      await refresh();
    });
  }, []);
  function install(doc: Doc | null) {
    selected.current = doc;
    latest.current = doc?.draft.text ?? "";
    saved.current = latest.current;
    draftVersion.current = doc?.draft.version ?? 0;
    setDocument(doc);
    setText(latest.current);
    setDirty(false);
    setStructureDirty(false);
    blocked.current = false;
    setRevisionId("");
    setRevisionPreview(null);
    setScript(null);
    setPreview(null);
  }
  async function save(): Promise<boolean> {
    if (flight.current) return flight.current;
    if (!selected.current || latest.current === saved.current) return true;
    if (blocked.current) {
      setError(
        "Resolve the draft conflict or copy local text before reloading. Use Save draft now to retry.",
      );
      return false;
    }
    const work = async () => {
      setSaving(true);
      setError("");
      try {
        while (
          live.current &&
          selected.current &&
          latest.current !== saved.current
        ) {
          const id = selected.current.id,
            sent = latest.current;
          const result = await api<{ version: number; saved_at: string }>(
            `${base}/documents/${id}/draft`,
            {
              method: "PUT",
              body: JSON.stringify({
                version: draftVersion.current,
                text: sent,
              }),
            },
          );
          draftVersion.current = result.version;
          saved.current = sent;
          if (live.current) {
            setDirty(latest.current !== saved.current);
            setDocument((d) =>
              d
                ? {
                    ...d,
                    draft: {
                      ...d.draft,
                      version: result.version,
                      saved_at: result.saved_at,
                    },
                  }
                : d,
            );
            setPreview(null);
          }
        }
        return true;
      } catch (e) {
        blocked.current = true;
        if (live.current)
          setError(`${(e as Error).message} Copy your text before reloading.`);
        return false;
      } finally {
        if (live.current) setSaving(false);
      }
    };
    flight.current = work();
    const ok = await flight.current;
    flight.current = null;
    return ok;
  }
  useEffect(() => {
    if (!dirty || readOnly || blocked.current) return;
    const timer = setTimeout(() => void save(), 650);
    return () => clearTimeout(timer);
  }, [text, dirty, readOnly]);
  useEffect(() => {
    const prevent = (event: BeforeUnloadEvent) => {
      if (dirty || saving || structureDirty) {
        event.preventDefault();
        event.returnValue = "";
      }
    };
    window.addEventListener("beforeunload", prevent);
    return () => window.removeEventListener("beforeunload", prevent);
  }, [dirty, saving, structureDirty]);
  async function choose(id: string) {
    if (!(await save())) return;
    if (structureDirty && !window.confirm("Discard unsaved structure changes?"))
      return;
    install(await api<Doc>(`${base}/documents/${id}`));
  }
  function sortedNodes(): { node: Node; depth: number }[] {
    const result: { node: Node; depth: number }[] = [],
      seen = new Set<string>();
    function append(parent: string | null, depth: number) {
      for (const n of workspace?.nodes ?? [])
        if (n.parent_id === parent && !seen.has(n.id)) {
          seen.add(n.id);
          result.push({ node: n, depth });
          append(n.id, depth + 1);
        }
    }
    append(null, 0);
    return result;
  }
  async function reloadDocument() {
    if (document) install(await api<Doc>(`${base}/documents/${document.id}`));
    await refresh();
  }
  return (
    <section className="workbench" aria-label="Manuscripts and history">
      <h3>Manuscripts and history</h3>
      {error && (
        <p role="alert" className="error">
          {error}
        </p>
      )}
      {notice && (
        <p role="status" className="notice">
          {notice}
        </p>
      )}
      <fieldset disabled={busy || saving}>
        <ul className="document-tree">
          {sortedNodes().map(({ node: n, depth }) => (
            <li key={n.id}>
              <button
                aria-current={document?.id === n.id ? "true" : undefined}
                onClick={() => void action(() => choose(n.id))}
              >
                {"— ".repeat(Math.min(depth, 10))}
                {n.title} <small>({n.kind})</small>
              </button>
            </li>
          ))}
        </ul>
        {!readOnly && (
          <details>
            <summary>Add or import document</summary>
            <form
              onSubmit={(e) => {
                e.preventDefault();
                const form = new FormData(e.currentTarget);
                void action(async () => {
                  if (!(await save())) return;
                  if (structureDirty)
                    throw Error("Save or reload structure changes first.");
                  const body = {
                    title: String(form.get("title")),
                    kind: String(form.get("kind")),
                    parent_id: form.get("parent") || null,
                  };
                  const doc = await api<Doc>(base + "/documents", {
                    method: "POST",
                    body: JSON.stringify(body),
                  });
                  await refresh();
                  install(doc);
                  setNotice("Document created.");
                });
              }}
            >
              <label htmlFor="manuscript-field-1">New document title</label>
              <input
                id="manuscript-field-1"
                name="title"
                required
                maxLength={200}
              />

              <label htmlFor="manuscript-field-2">Document kind</label>
              <select
                id="manuscript-field-2"
                name="kind"
                defaultValue="manuscript"
              >
                {kinds.map((k) => (
                  <option key={k}>{k}</option>
                ))}
              </select>

              <label htmlFor="manuscript-field-3">New document parent</label>
              <select id="manuscript-field-3" name="parent">
                <option value="">Project root</option>
                {workspace?.nodes.map((n) => (
                  <option key={n.id} value={n.id}>
                    {n.title}
                  </option>
                ))}
              </select>

              <button>Create document</button>
            </form>
            <form
              onSubmit={(e) => {
                e.preventDefault();
                const form = new FormData(e.currentTarget);
                void action(async () => {
                  if (!(await save())) return;
                  if (structureDirty)
                    throw Error("Save or reload structure changes first.");
                  const data = new FormData();
                  data.append("file", form.get("file") as File);
                  const params = new URLSearchParams({
                    title: String(form.get("title")),
                    kind: String(form.get("kind")),
                  });
                  if (form.get("parent"))
                    params.set("parent_id", String(form.get("parent")));
                  const doc = await api<Doc>(
                    base + "/documents/import?" + params,
                    { method: "POST", body: data },
                  );
                  await refresh();
                  install(doc);
                  await onImported();
                  setNotice(
                    "Original file preserved; editable manuscript imported.",
                  );
                });
              }}
            >
              <label htmlFor="manuscript-field-4">Import title</label>
              <input
                id="manuscript-field-4"
                required
                name="title"
                maxLength={200}
              />

              <label htmlFor="manuscript-field-5">Import kind</label>
              <select
                id="manuscript-field-5"
                name="kind"
                defaultValue="manuscript"
              >
                {kinds.map((k) => (
                  <option key={k}>{k}</option>
                ))}
              </select>

              <label htmlFor="manuscript-field-6">Import parent</label>
              <select id="manuscript-field-6" name="parent">
                <option value="">Project root</option>
                {workspace?.nodes.map((n) => (
                  <option key={n.id} value={n.id}>
                    {n.title}
                  </option>
                ))}
              </select>

              <label htmlFor="manuscript-field-7">TXT or Markdown file</label>
              <input
                id="manuscript-field-7"
                required
                name="file"
                type="file"
                accept=".txt,.md,.markdown"
              />

              <p className="hint">
                UTF-8 or BOM-marked UTF-16, up to 1 MiB. Imported text is never
                executed.
              </p>
              <button>Import manuscript</button>
            </form>
          </details>
        )}
      </fieldset>
      {document && (
        <>
          <h4>{document.title}</h4>
          <details>
            <summary>Structure and research references</summary>
            <form
              key={document.id + ":" + document.version}
              onChange={() => setStructureDirty(true)}
              onSubmit={(e) => {
                e.preventDefault();
                const form = new FormData(e.currentTarget);
                void action(async () => {
                  if (!(await save())) return;
                  const updated = await api<Doc>(
                    `${base}/documents/${document.id}`,
                    {
                      method: "PUT",
                      body: JSON.stringify({
                        title: form.get("title"),
                        kind: form.get("kind"),
                        position: Number(form.get("position")),
                        parent_id: form.get("parent") || null,
                        version: document.version,
                        references: form.getAll("references"),
                      }),
                    },
                  );
                  install(updated);
                  await refresh();
                  setNotice("Structure saved.");
                });
              }}
            >
              <fieldset disabled={readOnly || busy || saving}>
                <label htmlFor="manuscript-field-8">Document title</label>
                <input
                  id="manuscript-field-8"
                  required
                  name="title"
                  defaultValue={document.title}
                  maxLength={200}
                />

                <label htmlFor="manuscript-field-9">Kind</label>
                <select
                  id="manuscript-field-9"
                  name="kind"
                  defaultValue={document.kind}
                >
                  {kinds.map((k) => (
                    <option key={k}>{k}</option>
                  ))}
                </select>

                <label htmlFor="manuscript-field-10">Parent</label>
                <select
                  id="manuscript-field-10"
                  name="parent"
                  defaultValue={document.parent_id ?? ""}
                >
                  <option value="">Project root</option>
                  {workspace?.nodes
                    .filter((n) => n.id !== document.id)
                    .map((n) => (
                      <option key={n.id} value={n.id}>
                        {n.title}
                      </option>
                    ))}
                </select>

                <label htmlFor="manuscript-field-11">Order within parent</label>
                <input
                  id="manuscript-field-11"
                  name="position"
                  type="number"
                  min="0"
                  max="100000"
                  defaultValue={document.position}
                />

                <label htmlFor="manuscript-field-12">Research references</label>
                <select
                  id="manuscript-field-12"
                  name="references"
                  multiple
                  defaultValue={document.references}
                >
                  {workspace?.nodes
                    .filter((n) => n.id !== document.id)
                    .map((n) => (
                      <option key={n.id} value={n.id}>
                        {n.title}
                      </option>
                    ))}
                </select>

                <button disabled={!structureDirty}>Save structure</button>
              </fieldset>
            </form>
          </details>
          <label htmlFor="manuscript-text">Manuscript text</label>
          <textarea
            id="manuscript-text"
            className="manuscript-text"
            readOnly={readOnly || busy}
            value={text}
            onChange={(e) => {
              latest.current = e.target.value;
              setText(e.target.value);
              setDirty(latest.current !== saved.current);
              setRevisionPreview(null);
              setScript(null);
            }}
          />
          <p role="status" className="draft-status">
            {saving
              ? "Saving draft…"
              : dirty
                ? "Unsaved draft — keep this page open."
                : "Draft saved locally."}{" "}
            {structureDirty ? "Unsaved structure changes." : ""}
          </p>
          <div className="actions">
            <button
              disabled={readOnly || busy || saving || !dirty}
              onClick={() =>
                void action(async () => {
                  blocked.current = false;
                  await save();
                })
              }
            >
              Save draft now
            </button>
            <button
              disabled={busy || saving}
              onClick={() => {
                if (
                  (dirty || structureDirty) &&
                  !window.confirm(
                    "Discard local unsaved text/structure and reload? Copy any conflicted text first.",
                  )
                )
                  return;
                void action(reloadDocument);
              }}
            >
              Reload manuscript
            </button>
          </div>
          <form
            onSubmit={(e) => {
              e.preventDefault();
              const form = new FormData(e.currentTarget);
              void action(async () => {
                if (!(await save())) return;
                await api(`${base}/documents/${document.id}/revisions`, {
                  method: "POST",
                  body: JSON.stringify({
                    version: draftVersion.current,
                    name: form.get("name"),
                  }),
                });
                await reloadDocument();
                setNotice("Revision frozen.");
              });
            }}
          >
            <fieldset disabled={readOnly || busy || saving || structureDirty}>
              <label htmlFor="manuscript-field-13">Revision note</label>
              <input
                id="manuscript-field-13"
                name="name"
                required
                maxLength={200}
                defaultValue="Manuscript revision"
              />

              <button>Freeze revision</button>
            </fieldset>
          </form>
          <details>
            <summary>Revision comparison and restoration</summary>
            <label htmlFor="manuscript-field-14">Revision</label>
            <select
              id="manuscript-field-14"
              value={revisionId}
              onChange={(e) => {
                setRevisionId(e.target.value);
                setRevisionPreview(null);
              }}
            >
              <option value="">Select a frozen revision</option>
              {document.revisions.map((r) => (
                <option key={r.id} value={r.id}>
                  {r.created_at} · {r.reason}
                </option>
              ))}
            </select>

            <button
              disabled={!revisionId || busy || saving}
              onClick={() =>
                void action(async () => {
                  if (!(await save())) return;
                  const p = await api<{
                    text_diff: string;
                    draft_version: number;
                  }>(
                    `${base}/documents/${document.id}/revisions/${revisionId}/compare`,
                  );
                  setRevisionPreview({
                    text: p.text_diff,
                    draft_version: p.draft_version,
                  });
                })
              }
            >
              Compare revision to draft
            </button>
            {revisionPreview && (
              <>
                <pre className="diff">
                  {revisionPreview.text || "No text differences."}
                </pre>
                <button
                  disabled={
                    readOnly || busy || saving || dirty || structureDirty
                  }
                  onClick={() => {
                    if (
                      !window.confirm(
                        "Restore this revision? Current saved text will be preserved in history.",
                      )
                    )
                      return;
                    void action(async () => {
                      install(
                        await api<Doc>(
                          `${base}/documents/${document.id}/restore`,
                          {
                            method: "POST",
                            body: JSON.stringify({
                              revision_id: revisionId,
                              version: revisionPreview.draft_version,
                            }),
                          },
                        ),
                      );
                      await refresh();
                      setNotice("Revision restored as a new history entry.");
                    });
                  }}
                >
                  Restore revision
                </button>
              </>
            )}
          </details>
          <details>
            <summary>Pronunciation preview for frozen script</summary>
            <p className="hint">
              Text-only preview; no speech engine is installed. Freeze changes
              first to preview them.
            </p>
            <button
              disabled={busy || saving}
              onClick={() =>
                void action(async () =>
                  setScript(
                    await api(
                      `${base}/documents/${document.id}/script/${document.head_revision_id}`,
                    ),
                  ),
                )
              }
            >
              Preview pronunciations
            </button>
            {script?.units.map((u) => (
              <div key={u.id}>
                <p>{u.spoken_text}</p>
                <small>
                  Source characters {u.start}–{u.end}
                </small>
              </div>
            ))}
          </details>
        </>
      )}
      <details>
        <summary>Project snapshots</summary>
        <p className="hint">
          A named snapshot freezes saved manuscripts, organization, settings and
          asset references. History is not a backup.
        </p>
        <form
          onSubmit={(e) => {
            e.preventDefault();
            const form = new FormData(e.currentTarget);
            void action(async () => {
              if (!(await save())) return;
              const w = await refresh();
              const p = await api<{ version: number }>(base);
              await api(base + "/snapshots", {
                method: "POST",
                body: JSON.stringify({
                  name: form.get("name"),
                  generation: w.generation,
                  project_version: p.version,
                }),
              });
              await refresh();
              if (document) await reloadDocument();
              setNotice("Project snapshot created.");
            });
          }}
        >
          <fieldset disabled={readOnly || busy || saving || structureDirty}>
            <label htmlFor="manuscript-field-15">Snapshot name</label>
            <input
              id="manuscript-field-15"
              name="name"
              required
              maxLength={200}
            />

            <button>Create project snapshot</button>
          </fieldset>
        </form>
        <label htmlFor="manuscript-field-16">Snapshot</label>
        <select
          id="manuscript-field-16"
          value={snapshotId}
          onChange={(e) => {
            setSnapshotId(e.target.value);
            setPreview(null);
          }}
        >
          <option value="">Select a snapshot</option>
          {snapshots.map((s) => (
            <option key={s.id} value={s.id}>
              {s.name} · {s.created_at}
            </option>
          ))}
        </select>

        <button
          disabled={!snapshotId || busy || saving || structureDirty}
          onClick={() =>
            void action(async () => {
              if (!(await save())) return;
              setPreview(
                await api<Preview>(`${base}/snapshots/${snapshotId}/preview`),
              );
            })
          }
        >
          Preview snapshot restoration
        </button>
        {preview && (
          <div>
            <h4>Changes to restore</h4>
            {preview.changes.map((c) => (
              <div key={c.id}>
                <p>
                  {c.action}: {c.title}
                </p>
                <pre className="diff">
                  {Object.entries(c.structure)
                    .map(([key, values]) => {
                      const pair = values as [unknown, unknown];
                      const display = (v: unknown) =>
                        key === "parent_id"
                          ? (workspace?.nodes.find((n) => n.id === v)?.title ??
                            (v ? "Saved parent" : "Project root"))
                          : key === "references_json"
                            ? "Saved research links"
                            : String(v ?? "None");
                      return `${({ title: "Title", kind: "Kind", parent_id: "Parent", position: "Order", references_json: "References", original_asset_id: "Original source" } as Record<string, string>)[key] ?? "Structure"}: ${display(pair[0])} → ${display(pair[1])}`;
                    })
                    .join("\n")}
                  {"\n"}
                  {c.text_diff}
                </pre>
              </div>
            ))}
            <details>
              <summary>Metadata, settings and asset comparison</summary>
              <pre className="diff">
                {`Project: ${preview.metadata.current.name} → ${preview.metadata.target.name}\nDescription: ${preview.metadata.current.description} → ${preview.metadata.target.description}\nSeries association: ${preview.metadata.current.series_id === preview.metadata.target.series_id ? "unchanged" : "restored to saved series"}\nOriginal assets: ${preview.assets.current.map((a) => a.filename).join(", ")}\nSnapshot originals: ${preview.assets.target.map((a) => a.filename).join(", ")}\n${preview.assets.policy}\nLanguage: ${preview.settings.current.resolved.controls.language ?? "Default"} → ${preview.settings.target.resolved.controls.language ?? "Default"}\nPace: ${preview.settings.current.resolved.controls.pace ?? "Default"} → ${preview.settings.target.resolved.controls.pace ?? "Default"}\nCurrent pronunciations: ${preview.settings.current.resolved.rules.map((r) => `${r.term} → ${r.replacement}`).join("; ")}\nSnapshot pronunciations: ${preview.settings.target.resolved.rules.map((r) => `${r.term} → ${r.replacement}`).join("; ")}`}
              </pre>
            </details>
            <p>
              Later drafts, nodes and history will be preserved in a “Before
              snapshot restore” snapshot. Newer asset originals remain
              available.
            </p>
            <button
              disabled={
                readOnly ||
                busy ||
                saving ||
                dirty ||
                structureDirty ||
                !canRestore
              }
              onClick={() => {
                if (
                  !window.confirm(
                    "Restore this project snapshot? Later work will be preserved in history.",
                  )
                )
                  return;
                void action(async () => {
                  await api(
                    `${base}/snapshots/${preview.snapshot_id}/restore`,
                    {
                      method: "POST",
                      body: JSON.stringify({
                        generation: preview.generation,
                        project_version: preview.project_version,
                      }),
                    },
                  );
                  install(null);
                  setPreview(null);
                  await refresh();
                  await onRestored();
                  setNotice(
                    "Project snapshot restored; later history retained.",
                  );
                });
              }}
            >
              Restore project snapshot
            </button>
            {!canRestore && (
              <p>Save project details before restoring a snapshot.</p>
            )}
          </div>
        )}
      </details>
      {workspace && (
        <Dictionary
          settings={workspace.settings}
          presets={presets}
          nodes={workspace.nodes}
          selectedId={document?.id}
          disabled={readOnly || busy || saving}
          save={async (value) => {
            let success = false;
            await action(async () => {
              await api(base + "/settings", {
                method: "PUT",
                body: JSON.stringify(value),
              });
              setPreview(null);
              setScript(null);
              await refresh();
              setNotice("Pronunciation settings saved as a new version.");
              success = true;
            });
            return success;
          }}
          createPreset={(name, configuration) =>
            action(async () => {
              await api("/presets", {
                method: "POST",
                body: JSON.stringify({ name, ...configuration }),
              });
              await refresh();
              setNotice(
                "Shared preset version created; existing projects unchanged.",
              );
            })
          }
        />
      )}
    </section>
  );
}
