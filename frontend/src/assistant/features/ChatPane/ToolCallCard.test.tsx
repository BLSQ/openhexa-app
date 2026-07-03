import { render, screen, fireEvent, within } from "@testing-library/react";
import { TOOL } from "assistant/helpers/tools";
import ToolCallCard from "./ToolCallCard";

describe("ToolCallCard", () => {
  it("renders the humanized tool label", () => {
    render(<ToolCallCard tool={null} toolName="get_workspace" status="done" success />);
    expect(screen.getByText("Reading workspace")).toBeInTheDocument();
  });

  it("hides input/output until expanded", () => {
    render(
      <ToolCallCard
        tool={null}
        toolName="get_workspace"
        status="done"
        success
        toolInput={{ workspace_slug: "covid-19" }}
        toolOutput={{ name: "COVID-19" }}
      />,
    );
    expect(screen.queryByText("Input")).not.toBeInTheDocument();
    expect(screen.queryByText("Output")).not.toBeInTheDocument();
  });

  it("toggles details on click and shows input and output", () => {
    const { container } = render(
      <ToolCallCard
        tool={null}
        toolName="get_workspace"
        status="done"
        success
        toolInput={{ workspace_slug: "covid-19" }}
        toolOutput={{ name: "COVID-19" }}
      />,
    );

    fireEvent.click(screen.getByRole("button", { expanded: false }));

    expect(screen.getByText("Input")).toBeInTheDocument();
    expect(screen.getByText("Output")).toBeInTheDocument();
    expect(container.textContent).toContain("workspace_slug");
    expect(container.textContent).toContain("COVID-19");

    fireEvent.click(screen.getByRole("button", { expanded: true }));
    expect(screen.queryByText("Input")).not.toBeInTheDocument();
  });

  it("omits the input section when input is empty", () => {
    render(
      <ToolCallCard
        tool={null}
        toolName="list_workspaces"
        status="done"
        success
        toolInput={{}}
        toolOutput={{ items: [] }}
      />,
    );
    fireEvent.click(screen.getByRole("button"));
    expect(screen.queryByText("Input")).not.toBeInTheDocument();
    expect(screen.getByText("Output")).toBeInTheDocument();
  });

  it("shows a running placeholder for the output while pending", () => {
    render(
      <ToolCallCard
        tool={null}
        toolName="get_workspace"
        status="pending"
        toolInput={{ workspace_slug: "covid-19" }}
      />,
    );
    fireEvent.click(screen.getByRole("button"));
    expect(screen.getByText("Input")).toBeInTheDocument();
    expect(screen.getByText("Running…")).toBeInTheDocument();
  });

  it("shows the changeset and hides the redundant output for propose_pipeline_version", () => {
    render(
      <ToolCallCard
        tool={TOOL.ProposePipelineVersion}
        toolName="propose_pipeline_version"
        status="done"
        success
        toolInput={{ modified_files: [{ name: "pipeline.py", content: "x" }] }}
        toolOutput={{ files: [{ name: "pipeline.py", content: "x" }] }}
      />,
    );
    fireEvent.click(screen.getByRole("button", { expanded: false }));
    // The changeset is shown under a "Proposed changes" header, not "Input",
    // and the full-version output is dropped (it lives in the FilesEditor diff).
    expect(screen.getByText("Proposed changes")).toBeInTheDocument();
    expect(screen.queryByText("Input")).not.toBeInTheDocument();
    expect(screen.queryByText("Output")).not.toBeInTheDocument();
  });

  it("renders an error state when the tool failed", () => {
    render(
      <ToolCallCard
        tool={null}
        toolName="get_workspace"
        status="done"
        success={false}
        toolOutput={{ errors: ["boom"] }}
      />,
    );
    const button = screen.getByRole("button");
    expect(within(button).getByText(/failed/i)).toBeInTheDocument();
  });
});
