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

// Ordered by specificity: tool-specific renderers first, generic shape-based
// ones last. The first whose `match` returns true wins; otherwise the caller
// falls back to the raw JSON view.
const RENDERERS: SemanticRenderer[] = [
  {
    id: "files-changeset",
    label: "Files",
    match: (value, ctx) =>
      ctx.toolName === "propose_pipeline_version" && fileSet(value) !== null,
    render: (value) => <FileSetValue files={fileSet(value)!} />,
  },
  {
    id: "files",
    label: "Files",
    match: (value, ctx) =>
      ctx.toolName === "list_files" && findTabularArray(value) !== null,
    render: (value) => <FileSystemValue files={findTabularArray(value)!} />,
  },
  {
    id: "code",
    label: "Code",
    match: (value, ctx) =>
      ctx.toolName === "read_file" &&
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
      ctx.toolName === "get_help_or_doc" &&
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
