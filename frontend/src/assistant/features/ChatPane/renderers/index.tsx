import { TOOL } from "assistant/helpers/tools";
import CodeValue from "./CodeValue";
import FileSetValue, { FileEntry } from "./FileSetValue";
import FileSystemValue from "./FileSystemValue";
import MarkdownValue from "./MarkdownValue";
import TableValue from "./TableValue";
import { findTabularArray, isPlainObject } from "./tabular";
import { RenderContext, SemanticRenderer } from "./types";

export type { RenderContext } from "./types";

function asString(value: unknown): string | null {
  return typeof value === "string" && value.length > 0 ? value : null;
}

// A changeset of files-with-content (propose_pipeline_version output `{files}`,
// or its input `{modified_files}`).
function fileSet(value: unknown): FileEntry[] | null {
  if (!isPlainObject(value)) return null;
  const arr = value.files ?? value.modified_files;
  if (
    Array.isArray(arr) &&
    arr.length > 0 &&
    arr.every((f) => isPlainObject(f) && typeof f.content === "string")
  ) {
    return arr as FileEntry[];
  }
  return null;
}

// The names listed in a propose_pipeline_version input's `deleted_files`.
function deletedFiles(value: unknown): string[] {
  if (!isPlainObject(value) || !Array.isArray(value.deleted_files)) return [];
  return value.deleted_files.filter((f): f is string => typeof f === "string");
}

// Ordered by specificity: tool-specific renderers first, generic shape-based
// ones last. The first whose `match` returns true wins; otherwise the caller
// falls back to the raw JSON view.
//
// `label` is a translator thunk (`(t) => t("Files")`) rather than a plain key:
// the i18next parser only extracts literal `t("…")` calls, so keeping the call
// here — co-located with the renderer — lets the key be picked up while staying
// the single source of truth (no separate label→t() map to keep in sync).
const RENDERERS: SemanticRenderer[] = [
  {
    id: "files-changeset",
    label: (t) => t("Files"),
    match: (value, ctx) =>
      ctx.tool === TOOL.ProposePipelineVersion &&
      (fileSet(value) !== null || deletedFiles(value).length > 0),
    render: (value) => (
      <FileSetValue
        files={fileSet(value) ?? []}
        deleted={deletedFiles(value)}
      />
    ),
  },
  {
    id: "files",
    label: (t) => t("Files"),
    match: (value, ctx) =>
      ctx.tool === TOOL.ListFiles && findTabularArray(value) !== null,
    render: (value) => <FileSystemValue files={findTabularArray(value)!} />,
  },
  {
    id: "code",
    label: (t) => t("Code"),
    match: (value, ctx) =>
      ctx.tool === TOOL.ReadFile &&
      ctx.kind === "output" &&
      isPlainObject(value) &&
      asString(value.content) !== null,
    render: (value, ctx) => (
      <CodeValue
        content={(value as { content: string }).content}
        fileName={
          isPlainObject(ctx.input)
            ? (ctx.input.file_path as string | undefined)
            : undefined
        }
      />
    ),
  },
  {
    id: "markdown",
    label: (t) => t("Document"),
    match: (value, ctx) =>
      ctx.tool === TOOL.GetHelpOrDoc &&
      ctx.kind === "output" &&
      isPlainObject(value) &&
      asString(value.content) !== null,
    render: (value) => (
      <MarkdownValue content={(value as { content: string }).content} />
    ),
  },
  {
    id: "table",
    label: (t) => t("Table"),
    wide: true,
    match: (value) => findTabularArray(value) !== null,
    render: (value) => <TableValue rows={findTabularArray(value)!} />,
  },
];

export function resolveSemanticRenderer(
  value: unknown,
  ctx: RenderContext,
): SemanticRenderer | null {
  return RENDERERS.find((r) => r.match(value, ctx)) ?? null;
}
