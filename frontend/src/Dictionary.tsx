import { useEffect, useState } from "react";
import type {
  Settings,
  Preset,
  Node,
  Rule,
  Configuration,
} from "./manuscriptTypes";

export function Dictionary({
  settings,
  presets,
  nodes,
  selectedId,
  disabled,
  save,
  createPreset,
}: {
  settings: Settings;
  presets: Preset[];
  nodes: Node[];
  selectedId?: string;
  disabled: boolean;
  save: (value: unknown) => Promise<boolean>;
  createPreset: (name: string, config: Configuration) => Promise<void>;
}) {
  const [presetId, setPresetId] = useState(settings.preset_id ?? "");
  const [rules, setRules] = useState<Rule[]>(settings.overrides.rules ?? []);
  const [term, setTerm] = useState(""),
    [replacement, setReplacement] = useState(""),
    [scope, setScope] = useState("");
  useEffect(() => {
    setPresetId(settings.preset_id ?? "");
    setRules(settings.overrides.rules ?? []);
  }, [settings.version, settings.preset_id]);
  function body(updatedRules = rules) {
    return {
      version: settings.version,
      preset_id: presetId || null,
      controls: settings.overrides.controls ?? {},
      rules: updatedRules,
    };
  }
  return (
    <details>
      <summary>Pronunciation dictionary and presets</summary>
      <p className="hint">
        Case-sensitive literal terms. A document rule overrides a project rule,
        which overrides a pinned shared preset. Changes never rewrite manuscript
        originals.
      </p>
      <fieldset disabled={disabled}>
        <label htmlFor="manuscript-field-17">Shared preset version</label>
        <select
          id="manuscript-field-17"
          value={presetId}
          onChange={(e) => setPresetId(e.target.value)}
        >
          <option value="">No shared preset</option>
          {presets.map((p) => (
            <option key={p.id} value={p.id}>
              {p.name} · version {p.version}
            </option>
          ))}
        </select>

        <button onClick={() => void save(body())}>Use preset version</button>
        <form
          onSubmit={(e) => {
            e.preventDefault();
            const rule = {
              term,
              replacement,
              ...(scope ? { node_id: scope } : {}),
            };
            const updated = [
              ...rules.filter(
                (r) => !(r.term === term && (r.node_id ?? "") === scope),
              ),
              rule,
            ];
            void save(body(updated)).then((ok) => {
              if (!ok) return;
              setRules(updated);
              setTerm("");
              setReplacement("");
            });
          }}
        >
          <label htmlFor="manuscript-field-18">Pronunciation term</label>
          <input
            id="manuscript-field-18"
            required
            maxLength={120}
            value={term}
            onChange={(e) => setTerm(e.target.value)}
          />

          <label htmlFor="manuscript-field-19">Spoken replacement</label>
          <input
            id="manuscript-field-19"
            required
            maxLength={240}
            value={replacement}
            onChange={(e) => setReplacement(e.target.value)}
          />

          <label htmlFor="manuscript-field-20">Rule scope</label>
          <select
            id="manuscript-field-20"
            value={scope}
            onChange={(e) => setScope(e.target.value)}
          >
            <option value="">Whole project</option>
            {nodes.map((n) => (
              <option key={n.id} value={n.id}>
                {n.title}
                {n.id === selectedId ? " (selected)" : ""}
              </option>
            ))}
          </select>

          <button>Save pronunciation rule</button>
        </form>
        <ul>
          {rules.map((r) => (
            <li key={r.term + ":" + r.node_id}>
              {r.term} → {r.replacement} (
              {r.node_id
                ? nodes.find((n) => n.id === r.node_id)?.title
                : "project"}
              ){" "}
              <button
                onClick={() => void save(body(rules.filter((x) => x !== r)))}
              >
                Remove override for {r.term}
              </button>
            </li>
          ))}
        </ul>
        <details>
          <summary>Resolved settings</summary>
          <p>
            Language: {settings.resolved.controls.language ?? "Engine default"}{" "}
            · Pace: {settings.resolved.controls.pace ?? "Engine default"}
          </p>
          <ul>
            {settings.resolved.rules.map((r) => (
              <li key={r.term + ":" + r.node_id}>
                {r.term} → {r.replacement} (
                {r.node_id
                  ? nodes.find((n) => n.id === r.node_id)?.title
                  : "project"}
                )
              </li>
            ))}
          </ul>
        </details>
        <form
          onSubmit={(e) => {
            e.preventDefault();
            const form = new FormData(e.currentTarget);
            void createPreset(String(form.get("name")), {
              controls: settings.resolved.controls,
              rules: settings.resolved.rules.filter((r) => !r.node_id),
            });
          }}
        >
          <label htmlFor="manuscript-field-21">New shared preset name</label>
          <input
            id="manuscript-field-21"
            name="name"
            required
            maxLength={200}
          />

          <button>Create shared preset version</button>
        </form>
      </fieldset>
    </details>
  );
}
