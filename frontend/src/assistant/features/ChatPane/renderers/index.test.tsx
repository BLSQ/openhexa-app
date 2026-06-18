import { render, screen } from "@testing-library/react";
import { resolveSemanticRenderer, RenderContext } from "./index";

function ctx(overrides: Partial<RenderContext>): RenderContext {
  return {
    kind: "output",
    toolName: "",
    success: true,
    input: {},
    output: {},
    ...overrides,
  };
}

describe("resolveSemanticRenderer", () => {
  it("picks the file-set renderer for propose_pipeline_version output", () => {
    const value = { files: [{ name: "pipeline.py", content: "print(1)" }] };
    const r = resolveSemanticRenderer(
      value,
      ctx({ toolName: "propose_pipeline_version" }),
    );
    expect(r?.id).toBe("files-changeset");
  });

  it("renders proposed file content as readable code, not a truncated cell", () => {
    const content = "def run():\n    return 42";
    const r = resolveSemanticRenderer(
      { files: [{ name: "pipeline.py", content }] },
      ctx({ toolName: "propose_pipeline_version" }),
    );
    const { container } = render(
      <>{r!.render({ files: [{ name: "pipeline.py", content }] }, ctx({}))}</>,
    );
    expect(screen.getByText("pipeline.py")).toBeInTheDocument();
    // Single file opens by default and shows its full content (syntax
    // highlighting splits it across spans, so assert on the combined text).
    expect(container.textContent).toContain("return 42");
  });

  it("picks the file-set renderer for a deletion-only changeset", () => {
    const r = resolveSemanticRenderer(
      { deleted_files: ["old.py"] },
      ctx({ toolName: "propose_pipeline_version", kind: "input" }),
    );
    expect(r?.id).toBe("files-changeset");
  });

  it("renders modified and deleted files together", () => {
    const value = {
      modified_files: [{ name: "pipeline.py", content: "print(1)" }],
      deleted_files: ["old.py"],
    };
    const r = resolveSemanticRenderer(
      value,
      ctx({ toolName: "propose_pipeline_version", kind: "input" }),
    );
    render(<>{r!.render(value, ctx({ kind: "input" }))}</>);
    expect(screen.getByText("pipeline.py")).toBeInTheDocument();
    expect(screen.getByText("old.py")).toBeInTheDocument();
  });

  it("picks the file-system renderer for list_files", () => {
    const value = { items: [{ name: "a.csv", type: "file", size: 12 }] };
    const r = resolveSemanticRenderer(value, ctx({ toolName: "list_files" }));
    expect(r?.id).toBe("files");
  });

  it("picks the code renderer for read_file output with content", () => {
    const value = { content: "print('hi')", size: 11 };
    const r = resolveSemanticRenderer(
      value,
      ctx({ toolName: "read_file", input: { file_path: "main.py" } }),
    );
    expect(r?.id).toBe("code");
  });

  it("declines markdown for the structured help overview", () => {
    const overview = { about: "x", tips: ["a"], docs: [{ name: "cli" }] };
    const r = resolveSemanticRenderer(
      overview,
      ctx({ toolName: "get_help_or_doc" }),
    );
    // No `content` string → falls through (overview has a docs array → table).
    expect(r?.id).not.toBe("markdown");
  });

  it("uses markdown for a help doc page", () => {
    const doc = { name: "cli", title: "CLI", content: "# CLI\nUse it." };
    const r = resolveSemanticRenderer(doc, ctx({ toolName: "get_help_or_doc" }));
    expect(r?.id).toBe("markdown");
  });

  it("falls back to a table for a generic list, then JSON for detail objects", () => {
    expect(
      resolveSemanticRenderer({ datasets: { items: [{ slug: "d" }] } }, ctx({}))?.id,
    ).toBe("table");
    expect(resolveSemanticRenderer({ id: "x", name: "y" }, ctx({}))).toBeNull();
  });

  it("renders the table renderer output", () => {
    const r = resolveSemanticRenderer([{ name: "covid", country: "BE" }], ctx({}));
    render(<>{r!.render([{ name: "covid", country: "BE" }], ctx({}))}</>);
    expect(screen.getByText("name")).toBeInTheDocument();
    expect(screen.getByText("covid")).toBeInTheDocument();
  });
});
