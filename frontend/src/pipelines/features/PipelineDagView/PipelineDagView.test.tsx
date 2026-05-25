import { render, screen } from "@testing-library/react";
import { PipelineDagOutputType } from "graphql/types";
import PipelineDagView from "./PipelineDagView";

// React Flow needs layout APIs jsdom lacks; smoke-test that content renders.
jest.mock("@xyflow/react", () => {
  const actual = jest.requireActual("@xyflow/react");
  return {
    ...actual,
    ReactFlow: ({ nodes }: any) => (
      <div data-testid="rf">
        {nodes.map((n: any) => (
          <div key={n.id} data-node-type={n.type}>
            {n.data?.label ?? n.data?.outputType}
          </div>
        ))}
      </div>
    ),
  };
});

const dag = {
  tasks: [{ id: "load", name: "load" }],
  edges: [],
  outputs: [
    { id: "o1", type: PipelineDagOutputType.Db, name: "baz", taskId: "load" },
  ],
};

describe("PipelineDagView", () => {
  it("renders task and trigger nodes", () => {
    render(
      <PipelineDagView
        pipelineName="Demo"
        triggers={{ manual: true, schedule: null, webhook: false }}
        parameters={[]}
        dag={dag}
      />,
    );
    expect(screen.getByTestId("rf")).toBeInTheDocument();
    expect(screen.getByText("load")).toBeInTheDocument();
    expect(screen.getByText("Manual")).toBeInTheDocument();
    expect(screen.getByText("Demo")).toBeInTheDocument();
  });
});
