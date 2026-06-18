import type { TFunction } from "i18next";
import { TOOL } from "assistant/helpers/tools";
import CodeValue from "./CodeValue";
import FileSetValue, { FileEntry } from "./FileSetValue";
import FileSystemValue from "./FileSystemValue";
import MarkdownValue from "./MarkdownValue";
import TableValue from "./TableValue";
import { findTabularArray, isPlainObject } from "./tabular";
import { RendererLabel, RenderContext, SemanticRenderer } from "./types";

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
const RENDERERS: SemanticRenderer[] = [
  {
    id: "files-changeset",
    label: "Files",
    match: (value, ctx) =>
      ctx.toolName === TOOL.PROPOSE_PIPELINE_VERSION &&
      (fileSet(value) !== null || deletedFiles(value).length > 0),
    render: (value) => (
      <FileSetValue files={fileSet(value) ?? []} deleted={deletedFiles(value)} />
    ),
  },
  {
    id: "files",
    label: "Files",
    match: (value, ctx) =>
      ctx.toolName === TOOL.LIST_FILES && findTabularArray(value) !== null,
    render: (value) => <FileSystemValue files={findTabularArray(value)!} />,
  },
  {
    id: "code",
    label: "Code",
    match: (value, ctx) =>
      ctx.toolName === TOOL.READ_FILE &&
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
    label: "Document",
    match: (value, ctx) =>
      ctx.toolName === TOOL.GET_HELP_OR_DOC &&
      ctx.kind === "output" &&
      isPlainObject(value) &&
      asString(value.content) !== null,
    render: (value) => (
      <MarkdownValue content={(value as { content: string }).content} />
    ),
  },
  {
    id: "table",
    label: "Table",
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

// Renderer labels are stored as plain keys on RENDERERS, so translate them
// through literal t() calls here — the i18next parser only extracts string
// literals and would otherwise warn (and purge) on a dynamic `t(label)`. The
// RendererLabel union keeps this map exhaustive: a new label won't type-check
// until it is registered here.
export function getRendererLabel(t: TFunction, label: RendererLabel): string {
  const labels: Record<RendererLabel, string> = {
    Files: t("Files"),
    Code: t("Code"),
    Document: t("Document"),
    Table: t("Table"),
  };
  return labels[label];
}
