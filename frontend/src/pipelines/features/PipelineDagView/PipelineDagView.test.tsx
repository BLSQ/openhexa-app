import { render, screen } from "@testing-library/react";
import PipelineDagView from "./PipelineDagView";

const version = (dag: {
  tasks: { id: string; name: string }[];
  edges: { source: string; target: string }[];
  parameters?: {
    code: string;
    name: string;
    type: string;
    required: boolean;
  }[];
}) => ({ id: "version-1", dag: { parameters: [], ...dag } }) as any;

const DIAMOND = {
  tasks: [
    { id: "save_dataset", name: "save_dataset" },
    { id: "load_history", name: "load_history" },
    { id: "load_devices", name: "load_devices" },
  ],
  edges: [
    { source: "city", target: "load_devices" },
    { source: "load_devices", target: "load_history" },
    { source: "load_devices", target: "save_dataset" },
    { source: "load_history", target: "save_dataset" },
  ],
  parameters: [{ code: "city", name: "City", type: "str", required: true }],
};

describe("PipelineDagView", () => {
  it("renders a box per task", () => {
    render(<PipelineDagView version={version(DIAMOND)} />);

    expect(screen.getByText("load_devices")).toBeInTheDocument();
    expect(screen.getByText("load_history")).toBeInTheDocument();
    expect(screen.getByText("save_dataset")).toBeInTheDocument();
  });

  it("renders the parameters the graph returns", () => {
    render(<PipelineDagView version={version(DIAMOND)} />);

    expect(screen.getByText("City")).toBeInTheDocument();
  });

  it("renders nothing when the version has no tasks", () => {
    const { container } = render(
      <PipelineDagView version={version({ tasks: [], edges: [] })} />,
    );

    expect(container).toBeEmptyDOMElement();
    expect(screen.queryByTestId("pipeline-dag-view")).not.toBeInTheDocument();
  });

  it("renders a single task with no edges", () => {
    render(
      <PipelineDagView
        version={version({ tasks: [{ id: "only", name: "only" }], edges: [] })}
      />,
    );

    expect(screen.getByTestId("pipeline-dag-view")).toBeInTheDocument();
    expect(screen.getByText("only")).toBeInTheDocument();
  });
});
