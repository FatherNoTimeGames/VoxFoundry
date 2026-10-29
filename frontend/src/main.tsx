import React, { useEffect, useState } from "react";
import { createRoot } from "react-dom/client";
import "./style.css";
import { api, setCsrf } from "./api";
import { Workbench } from "./Workbench";

type Project = {
  id: string;
  name: string;
  description: string;
  version: number;
  series_id: string | null;
  trashed_at: string | null;
};
type Series = { id: string; name: string };
type Asset = {
  id: string;
  filename: string;
  size: number;
  state: string;
  digest: string;
};
type Library = {
  id: string;
  path: string;
  failed_imports: { id: string; error: string }[];
};
function App() {
  const [ready, setReady] = useState(false),
    [error, setError] = useState(""),
    [notice, setNotice] = useState("");
  const [busy, setBusy] = useState(false),
    [library, setLibrary] = useState<Library>();
  const [projects, setProjects] = useState<Project[]>([]),
    [series, setSeries] = useState<Series[]>([]);
  const [trashed, setTrashed] = useState(false),
    [selected, setSelected] = useState<Project | null>(null);
  const [name, setName] = useState(""),
    [description, setDescription] = useState(""),
    [seriesId, setSeriesId] = useState("");
  const [newName, setNewName] = useState(""),
    [seriesName, setSeriesName] = useState("");
  const [assets, setAssets] = useState<Asset[]>([]),
    [file, setFile] = useState<File | null>(null);
  const [dirty, setDirty] = useState(false);
  const [manuscriptDirty, setManuscriptDirty] = useState(false);
  async function run(action: () => Promise<void>) {
    setBusy(true);
    setError("");
    setNotice("");
    try {
      await action();
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setBusy(false);
    }
  }
  async function refresh(showTrash = trashed) {
    const [p, s, l] = await Promise.all([
      api<Project[]>(`/projects?trashed=${showTrash}`),
      api<Series[]>("/series"),
      api<Library>("/library"),
    ]);
    setProjects(p);
    setSeries(s);
    setLibrary(l);
  }
  function select(project: Project | null) {
    setSelected(project);
    setName(project?.name ?? "");
    setDescription(project?.description ?? "");
    setSeriesId(project?.series_id ?? "");
    setDirty(false);
    if (project?.id !== selected?.id) {
      setAssets([]);
      setFile(null);
    }
  }
  function canLeave() {
    if (manuscriptDirty) {
      setError("Save or reload the manuscript before switching projects.");
      return false;
    }
    return !dirty || window.confirm("Discard unsaved project changes?");
  }
  useEffect(() => {
    void run(async () => {
      const token = new URLSearchParams(window.location.hash.slice(1)).get(
        "token",
      );
      history.replaceState(null, "", window.location.pathname);
      const session = token
        ? await api<{ csrf: string }>("/session", {
            method: "POST",
            body: JSON.stringify({ token }),
          })
        : await api<{ csrf: string }>("/session");
      setCsrf(session.csrf);
      await refresh(false);
      setReady(true);
    });
  }, []);
  useEffect(() => {
    const prevent = (e: BeforeUnloadEvent) => {
      if (dirty || manuscriptDirty) {
        e.preventDefault();
        e.returnValue = "";
      }
    };
    window.addEventListener("beforeunload", prevent);
    return () => window.removeEventListener("beforeunload", prevent);
  }, [dirty, manuscriptDirty]);
  useEffect(() => {
    let cancelled = false;
    if (selected)
      api<Asset[]>(`/projects/${selected.id}/assets`)
        .then((a) => {
          if (!cancelled) setAssets(a);
        })
        .catch((e) => {
          if (!cancelled) setError(e.message);
        });
    return () => {
      cancelled = true;
    };
  }, [selected?.id]);
  return (
    <>
      <header>
        <div>
          <p className="eyebrow">Your stories, kept local</p>
          <h1>VoxFoundry</h1>
        </div>
        <span className="badge">Manuscript preview</span>
      </header>
      <main>
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
        {!ready ? (
          <p>
            Open VoxFoundry through its launcher to connect to your local
            library.
          </p>
        ) : (
          <>
            <p className="library">Library: {library?.path}</p>
            <p className="hint">
              Project organization and original asset storage are available.
              Narration and project archives are planned; this preview is not a
              backup system.
            </p>
            {!!library?.failed_imports.length && (
              <section aria-label="Import recovery">
                <h2>Imports needing attention</h2>
                {library.failed_imports.map((o) => (
                  <p key={o.id}>{o.error}</p>
                ))}
                <p>
                  Partial files are retained. Check disk space, then upload the
                  original again.
                </p>
              </section>
            )}
            <div className="layout">
              <aside>
                <h2>Projects</h2>
                <div className="tabs">
                  <button
                    disabled={busy}
                    aria-pressed={!trashed}
                    onClick={() => {
                      if (canLeave())
                        void run(async () => {
                          setTrashed(false);
                          select(null);
                          await refresh(false);
                        });
                    }}
                  >
                    Active projects
                  </button>
                  <button
                    disabled={busy}
                    aria-pressed={trashed}
                    onClick={() => {
                      if (canLeave())
                        void run(async () => {
                          setTrashed(true);
                          select(null);
                          await refresh(true);
                        });
                    }}
                  >
                    Trash
                  </button>
                </div>
                {projects.length === 0 && (
                  <p>
                    {trashed
                      ? "No trashed projects."
                      : "Create your first project."}
                  </p>
                )}
                <ul className="projects">
                  {projects.map((p) => (
                    <li key={p.id}>
                      <button
                        disabled={busy}
                        aria-current={
                          selected?.id === p.id ? "true" : undefined
                        }
                        onClick={() => {
                          if (canLeave()) select(p);
                        }}
                      >
                        {p.name}
                      </button>
                    </li>
                  ))}
                </ul>
                {!trashed && (
                  <form
                    onSubmit={(e) => {
                      e.preventDefault();
                      if (!canLeave()) return;
                      void run(async () => {
                        const p = await api<Project>("/projects", {
                          method: "POST",
                          body: JSON.stringify({ name: newName }),
                        });
                        await refresh();
                        select(p);
                        setNewName("");
                        setNotice("Project created.");
                      });
                    }}
                  >
                    <label htmlFor="project-field-1">New project name</label>
                    <input
                      id="project-field-1"
                      required
                      maxLength={200}
                      value={newName}
                      onChange={(e) => setNewName(e.target.value)}
                    />

                    <button disabled={busy}>Create project</button>
                  </form>
                )}
                <details>
                  <summary>Series</summary>
                  <ul>
                    {series.map((s) => (
                      <li key={s.id}>{s.name}</li>
                    ))}
                  </ul>
                  <form
                    onSubmit={(e) => {
                      e.preventDefault();
                      void run(async () => {
                        await api("/series", {
                          method: "POST",
                          body: JSON.stringify({ name: seriesName }),
                        });
                        setSeriesName("");
                        await refresh();
                        setNotice("Series created.");
                      });
                    }}
                  >
                    <label htmlFor="project-field-2">New series name</label>
                    <input
                      id="project-field-2"
                      required
                      maxLength={200}
                      value={seriesName}
                      onChange={(e) => setSeriesName(e.target.value)}
                    />

                    <button disabled={busy}>Create series</button>
                  </form>
                </details>
              </aside>
              <section aria-label="Project details">
                {!selected ? (
                  <>
                    <h2>Make room for a story</h2>
                    <p>
                      Select a project to organize its details and preserve
                      original assets.
                    </p>
                  </>
                ) : (
                  <>
                    <h2>{selected.name}</h2>
                    <form
                      onSubmit={(e) => {
                        e.preventDefault();
                        void run(async () => {
                          const p = await api<Project>(
                            `/projects/${selected.id}`,
                            {
                              method: "PUT",
                              body: JSON.stringify({
                                name,
                                description,
                                series_id: seriesId || null,
                                version: selected.version,
                              }),
                            },
                          );
                          select(p);
                          await refresh();
                          setNotice("Project saved.");
                        });
                      }}
                    >
                      <fieldset disabled={busy || trashed}>
                        <label htmlFor="project-field-3">Project name</label>
                        <input
                          id="project-field-3"
                          required
                          maxLength={200}
                          value={name}
                          onChange={(e) => {
                            setName(e.target.value);
                            setDirty(true);
                          }}
                        />

                        <label htmlFor="project-description">Description</label>
                        <textarea
                          id="project-description"
                          maxLength={10000}
                          value={description}
                          onChange={(e) => {
                            setDescription(e.target.value);
                            setDirty(true);
                          }}
                        />
                        <label htmlFor="project-field-4">Series</label>
                        <select
                          id="project-field-4"
                          value={seriesId}
                          onChange={(e) => {
                            setSeriesId(e.target.value);
                            setDirty(true);
                          }}
                        >
                          <option value="">Independent project</option>
                          {series.map((s) => (
                            <option key={s.id} value={s.id}>
                              {s.name}
                            </option>
                          ))}
                        </select>

                        <button disabled={!dirty}>Save changes</button>
                        <span className="save-state">
                          {dirty ? "Unsaved changes" : "Saved"}
                        </span>
                      </fieldset>
                    </form>
                    <div className="actions">
                      <button
                        disabled={busy}
                        onClick={() => {
                          if (canLeave())
                            void run(async () => {
                              await api(
                                `/projects/${selected.id}/${trashed ? "restore" : "trash"}`,
                                {
                                  method: "POST",
                                  body: JSON.stringify({
                                    version: selected.version,
                                  }),
                                },
                              );
                              select(null);
                              await refresh();
                              setNotice(
                                trashed
                                  ? "Project restored."
                                  : "Project moved to trash. Assets are preserved.",
                              );
                            });
                        }}
                      >
                        {trashed ? "Restore project" : "Move to trash"}
                      </button>
                      <button
                        disabled={busy}
                        onClick={() => {
                          if (canLeave())
                            void run(async () => {
                              select(
                                await api<Project>(`/projects/${selected.id}`),
                              );
                              setNotice("Project reloaded.");
                            });
                        }}
                      >
                        Reload project
                      </button>
                    </div>
                    <Workbench
                      key={selected.id}
                      projectId={selected.id}
                      readOnly={trashed}
                      canRestore={!dirty}
                      onGuardChange={setManuscriptDirty}
                      onImported={async () =>
                        setAssets(
                          await api<Asset[]>(`/projects/${selected.id}/assets`),
                        )
                      }
                      onRestored={async () => {
                        select(await api<Project>(`/projects/${selected.id}`));
                        await refresh();
                      }}
                    />
                    <h3>Original assets</h3>
                    <p className="hint">
                      Original bytes are preserved. Downloads are attachments;
                      imported content is never executed. Limit: 25 MiB per
                      file.
                    </p>
                    {assets.length === 0 ? (
                      <p>No assets yet.</p>
                    ) : (
                      <ul>
                        {assets.map((a) => (
                          <li key={a.id}>
                            <a
                              href={`/api/projects/${selected.id}/assets/${a.id}`}
                            >
                              {a.filename}
                            </a>{" "}
                            <span className="hint">
                              {a.size.toLocaleString()} bytes · {a.state}
                            </span>
                          </li>
                        ))}
                      </ul>
                    )}
                    {!trashed && (
                      <form
                        onSubmit={(e) => {
                          e.preventDefault();
                          if (!file) return;
                          void run(async () => {
                            const data = new FormData();
                            data.append("file", file);
                            await api(`/projects/${selected.id}/assets`, {
                              method: "POST",
                              body: data,
                            });
                            setAssets(
                              await api<Asset[]>(
                                `/projects/${selected.id}/assets`,
                              ),
                            );
                            await refresh();
                            setNotice("Original asset stored.");
                          });
                        }}
                      >
                        <label htmlFor="project-field-5">
                          Choose original asset
                        </label>
                        <input
                          id="project-field-5"
                          key={selected.id}
                          type="file"
                          disabled={busy}
                          onChange={(e) => setFile(e.target.files?.[0] ?? null)}
                        />

                        <button disabled={busy || !file}>Store original</button>
                      </form>
                    )}
                  </>
                )}
              </section>
            </div>
          </>
        )}
      </main>
      <footer>
        Offline by design · Libraries stay outside the application · Apache 2.0
      </footer>
    </>
  );
}
createRoot(document.getElementById("root")!).render(<App />);
