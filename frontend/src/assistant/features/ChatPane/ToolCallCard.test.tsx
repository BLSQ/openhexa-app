import { render, screen, fireEvent, within } from "@testing-library/react";
import ToolCallCard from "./ToolCallCard";

describe("ToolCallCard", () => {
  it("renders the humanized tool label", () => {
    render(<ToolCallCard toolName="get_workspace" status="done" success />);
    expect(screen.getByText("Reading workspace")).toBeInTheDocument();
  });

  it("hides input/output until expanded", () => {
    render(
      <ToolCallCard
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
        toolName="get_workspace"
        status="pending"
        toolInput={{ workspace_slug: "covid-19" }}
      />,
    );
    fireEvent.click(screen.getByRole("button"));
    expect(screen.getByText("Input")).toBeInTheDocument();
    expect(screen.getByText("Running…")).toBeInTheDocument();
  });

  it("renders an error state when the tool failed", () => {
    render(
      <ToolCallCard
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
