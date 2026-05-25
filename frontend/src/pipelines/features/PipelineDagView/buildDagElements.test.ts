import { PipelineDagOutputType } from "graphql/types";
import {
  buildDagElements,
  PARAMETERS_NODE_ID,
  PIPELINE_NODE_ID,
} from "./buildDagElements";

const dag = {
  tasks: [
    { id: "load", name: "load" },
    { id: "transform", name: "transform" },
  ],
  edges: [{ source: "load", target: "transform" }],
  outputs: [
    {
      id: "o1",
      type: PipelineDagOutputType.Db,
      name: "baz",
      taskId: "transform",
    },
    {
      id: "o2",
      type: PipelineDagOutputType.File,
      name: "out.csv",
      taskId: "transform",
    },
  ],
};

const build = (overrides = {}) =>
  buildDagElements({
    triggers: { manual: true, schedule: null, webhook: false },
    dag,
    parameters: [],
    pipelineName: "Demo",
    ...overrides,
  });

describe("buildDagElements", () => {
  it("wraps tasks in a labeled pipeline container", () => {
    const { nodes } = build();
    const container = nodes.find((n) => n.id === PIPELINE_NODE_ID);
    expect(container?.type).toBe("pipeline");
    expect(container?.data.label).toBe("Demo");
    // tasks are children of the container
    const tasks = nodes.filter((n) => n.type === "task");
    expect(tasks).toHaveLength(2);
    expect(tasks.every((t) => t.parentId === PIPELINE_NODE_ID)).toBe(true);
  });

  it("connects triggers to the container, not to individual tasks", () => {
    const { edges } = buildDagElements({
      triggers: { manual: true, schedule: "0 6 * * *", webhook: true },
      dag,
      parameters: [],
      pipelineName: "Demo",
    });
    const triggerEdges = edges.filter((e) => e.source.startsWith("trigger-"));
    expect(triggerEdges).toHaveLength(3);
    expect(triggerEdges.every((e) => e.target === PIPELINE_NODE_ID)).toBe(true);
    // no trigger connects straight to a task
    expect(triggerEdges.some((e) => e.target === "load")).toBe(false);
  });

  it("creates one output group per non-empty type, wired from its task", () => {
    const { nodes, edges } = build();
    expect(nodes.filter((n) => n.type === "outputGroup")).toHaveLength(2);
    // outputs originate from the emitting task, exiting the container
    expect(
      edges.some((e) => e.source === "transform" && e.target.includes("db")),
    ).toBe(true);
    expect(
      edges.some((e) => e.source === "transform" && e.target.includes("file")),
    ).toBe(true);
  });

  it("omits hidden triggers", () => {
    const { nodes } = build();
    expect(nodes.filter((n) => n.type === "trigger")).toHaveLength(1);
  });

  it("adds a parameters node connected to the container when parameters exist", () => {
    const { nodes, edges } = build({
      parameters: [
        { code: "output_table", name: "Output table", type: "str" },
        { code: "rows", name: null, type: "int" },
      ],
    });
    const params = nodes.find((n) => n.id === PARAMETERS_NODE_ID);
    expect(params?.type).toBe("parameters");
    expect(
      (params?.data.items as { code: string }[]).map((p) => p.code),
    ).toEqual(["output_table", "rows"]);
    expect(
      edges.some(
        (e) => e.source === PARAMETERS_NODE_ID && e.target === PIPELINE_NODE_ID,
      ),
    ).toBe(true);
  });

  it("omits the parameters node when there are no parameters", () => {
    const { nodes } = build();
    expect(nodes.some((n) => n.id === PARAMETERS_NODE_ID)).toBe(false);
  });

  it("renders a container with no children when there are no tasks", () => {
    const { nodes, edges } = build({
      dag: { tasks: [], edges: [], outputs: [] },
    });
    const container = nodes.find((n) => n.id === PIPELINE_NODE_ID);
    expect(container?.type).toBe("pipeline");
    expect(nodes.filter((n) => n.type === "task")).toHaveLength(0);
    expect(
      edges.some(
        (e) => e.source.startsWith("trigger-") && e.target === PIPELINE_NODE_ID,
      ),
    ).toBe(true);
  });
});
