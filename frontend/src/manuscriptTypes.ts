export type Rule = { term: string; replacement: string; node_id?: string };
export type Configuration = {
  controls: { language?: string; pace?: number };
  rules: Rule[];
};
export type Settings = {
  version: number;
  preset_id: string | null;
  overrides: Partial<Configuration>;
  resolved: Configuration;
};
export type Node = {
  id: string;
  title: string;
  kind: string;
  parent_id: string | null;
  position: number;
  version: number;
  references: string[];
  head_revision_id: string;
};
export type Revision = {
  id: string;
  reason: string;
  created_at: string;
  restored_from: string | null;
};
export type Doc = Node & {
  draft: { text: string; version: number; saved_at: string };
  revisions: Revision[];
  unfrozen: boolean;
};
export type Workspace = {
  nodes: Node[];
  generation: number;
  head_snapshot_id: string | null;
  settings: Settings;
};
export type Snapshot = {
  id: string;
  name: string;
  created_at: string;
  restored_from: string | null;
};
export type Preview = {
  snapshot_id: string;
  generation: number;
  project_version: number;
  changes: {
    id: string;
    title: string;
    action: string;
    structure: Record<string, unknown>;
    text_diff: string;
  }[];
  metadata: {
    current: { name: string; description: string; series_id: string | null };
    target: { name: string; description: string; series_id: string | null };
  };
  settings: { current: Settings; target: Settings };
  assets: {
    current: { filename: string }[];
    target: { filename: string }[];
    policy: string;
  };
};
export type Preset = {
  id: string;
  name: string;
  version: number;
  settings: Configuration;
};
export type Props = {
  projectId: string;
  readOnly: boolean;
  canRestore: boolean;
  onGuardChange: (dirty: boolean) => void;
  onImported: () => Promise<void>;
  onRestored: () => Promise<void>;
};
