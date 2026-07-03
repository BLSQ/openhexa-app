import { render, screen, fireEvent, within } from "@testing-library/react";
import ToolValueSection from "./ToolValueSection";
import { RenderContext } from "./renderers";

function ctx(overrides: Partial<RenderContext> = {}): RenderContext {
  return {
    kind: "output",
    tool: null,
    toolName: "",
    success: true,
    input: {},
    output: {},
    ...overrides,
  };
}

describe("ToolValueSection", () => {
  it("falls back to raw JSON (no view toggle) for an unrecognized shape", () => {
    const { container } = render(
      <ToolValueSection
        label="Output"
        value={{ id: "x", name: "y" }}
        ctx={ctx({ toolName: "get_pipeline" })}
      />,
    );
    // A detail object has no semantic renderer, so there's nothing to toggle.
    expect(screen.queryByRole("button", { name: "Raw" })).not.toBeInTheDocument();
    expect(container.textContent).toContain("name");
  });

  it("renders a recognized value with its formatted view by default", () => {
    render(
      <ToolValueSection
        label="Output"
        value={[{ name: "covid", country: "BE" }]}
        ctx={ctx()}
      />,
    );
    // Table renderer wins for an array of objects → column headers are shown.
    expect(screen.getByRole("table")).toBeInTheDocument();
    expect(screen.getByText("Table")).toBeInTheDocument();
    expect(screen.getByText("Raw")).toBeInTheDocument();
  });

  it("switches from the formatted view to raw JSON", () => {
    render(
      <ToolValueSection
        label="Output"
        value={[{ name: "covid", country: "BE" }]}
        ctx={ctx()}
      />,
    );
    fireEvent.click(screen.getByText("Raw"));
    expect(screen.queryByRole("table")).not.toBeInTheDocument();
  });

  it("opens the value in a modal from the expand control", () => {
    render(
      <ToolValueSection
        label="Output"
        value={[{ name: "covid", country: "BE" }]}
        ctx={ctx()}
      />,
    );
    fireEvent.click(screen.getAllByRole("button", { name: "Expand" })[0]);
    const dialog = screen.getByRole("dialog");
    expect(within(dialog).getByText("Output")).toBeInTheDocument();
    expect(within(dialog).getByRole("table")).toBeInTheDocument();
  });

  it("keeps the modal and inline view modes independent", () => {
    render(
      <ToolValueSection
        label="Output"
        value={[{ name: "covid", country: "BE" }]}
        ctx={ctx()}
      />,
    );
    fireEvent.click(screen.getAllByRole("button", { name: "Expand" })[0]);
    const dialog = screen.getByRole("dialog");

    // Switching to Raw inside the modal must not collapse the inline table.
    fireEvent.click(within(dialog).getByText("Raw"));
    expect(within(dialog).queryByRole("table")).not.toBeInTheDocument();
    // The open modal makes the background inert (aria-hidden), so query the
    // still-present inline table with hidden: true.
    const inline = document.querySelector(".relative.w-full.overflow-hidden");
    expect(
      within(inline as HTMLElement).getByRole("table", { hidden: true }),
    ).toBeInTheDocument();
  });
});
