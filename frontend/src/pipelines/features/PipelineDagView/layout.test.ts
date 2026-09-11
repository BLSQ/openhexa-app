import { buildGraph, NODE_HEIGHT, NODE_WIDTH } from "./layout";

// The shapes below are the ones the backend extractor actually produces, taken from the
// pipelines it was validated against.

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

const ids = (nodes: { id: string }[]) => nodes.map((node) => node.id).sort();

describe("buildGraph", () => {
  it("builds a node per task and per connected parameter", () => {
    const { nodes, edges } = buildGraph(
      DIAMOND.tasks,
      DIAMOND.edges,
      DIAMOND.parameters,
    );

    expect(ids(nodes)).toEqual([
      "city",
      "load_devices",
      "load_history",
      "save_dataset",
    ]);
    expect(edges).toHaveLength(4);
  });

  it("types parameter nodes apart from task nodes", () => {
    const { nodes } = buildGraph(
      DIAMOND.tasks,
      DIAMOND.edges,
      DIAMOND.parameters,
    );

    const city = nodes.find((node) => node.id === "city")!;
    expect(city.type).toBe("parameter");
    expect(city.data).toMatchObject({
      label: "City",
      code: "city",
      type: "str",
      required: true,
    });
    expect(nodes.find((node) => node.id === "load_devices")!.type).toBe("task");
  });

  it("wires a parameter to the task that consumes it", () => {
    const { edges } = buildGraph(
      DIAMOND.tasks,
      DIAMOND.edges,
      DIAMOND.parameters,
    );

    expect(edges).toContainEqual(
      expect.objectContaining({ source: "city", target: "load_devices" }),
    );
  });

  it("falls back to the parameter code when it has no display name", () => {
    const { nodes } = buildGraph(
      [{ id: "t", name: "t" }],
      [{ source: "raw_code", target: "t" }],
      [{ code: "raw_code", name: null, type: "int", required: false }],
    );

    expect(nodes.find((node) => node.id === "raw_code")!.data.label).toBe(
      "raw_code",
    );
  });

  it("omits a parameter the code never passes to a task", () => {
    const { nodes } = buildGraph(
      [{ id: "t", name: "t" }],
      [],
      [
        { code: "used", name: "Used", type: "str", required: true },
        { code: "unused", name: "Unused", type: "str", required: false },
      ],
    );

    // Drawing an unconnected box would claim a relationship the pipeline does not have; the
    // parameters table below the diagram remains the exhaustive list.
    expect(ids(nodes)).toEqual(["t"]);
  });

  it("renders tasks when the pipeline declares no parameters", () => {
    const { nodes, edges } = buildGraph(
      [
        { id: "a", name: "a" },
        { id: "b", name: "b" },
      ],
      [{ source: "a", target: "b" }],
      [],
    );

    expect(ids(nodes)).toEqual(["a", "b"]);
    expect(edges).toHaveLength(1);
  });

  it("renders a single task with its parameter", () => {
    const { nodes, edges } = buildGraph(
      [{ id: "fetch", name: "fetch" }],
      [{ source: "conn", target: "fetch" }],
      [{ code: "conn", name: "Connection", type: "dhis2", required: true }],
    );

    expect(ids(nodes)).toEqual(["conn", "fetch"]);
    expect(edges).toHaveLength(1);
  });

  it("keeps disconnected components", () => {
    const { nodes, edges } = buildGraph(
      [
        { id: "a1", name: "a1" },
        { id: "a2", name: "a2" },
        { id: "lonely", name: "lonely" },
      ],
      [{ source: "a1", target: "a2" }],
      [],
    );

    expect(ids(nodes)).toEqual(["a1", "a2", "lonely"]);
    expect(edges).toHaveLength(1);
  });

  it("returns nothing when there are no tasks", () => {
    expect(
      buildGraph(
        [],
        [],
        [{ code: "a", name: "A", type: "str", required: true }],
      ),
    ).toEqual({ nodes: [], edges: [] });
  });

  it("drops an edge pointing at something that is neither task nor parameter", () => {
    const { edges } = buildGraph(
      [{ id: "t", name: "t" }],
      [
        { source: "t", target: "ghost" },
        { source: "ghost", target: "t" },
      ],
      [],
    );

    expect(edges).toEqual([]);
  });

  it("lays out left to right, sources left of their targets", () => {
    const { nodes } = buildGraph(
      DIAMOND.tasks,
      DIAMOND.edges,
      DIAMOND.parameters,
    );
    const at = (id: string) => nodes.find((node) => node.id === id)!.position.x;

    expect(at("city")).toBeLessThan(at("load_devices"));
    expect(at("load_devices")).toBeLessThan(at("load_history"));
    expect(at("load_history")).toBeLessThan(at("save_dataset"));
  });

  it("anchors nodes top-left, not centred as dagre reports them", () => {
    const { nodes } = buildGraph([{ id: "only", name: "only" }], [], []);

    // dagre places a lone node at (width/2, height/2); React Flow expects its corner.
    expect(nodes[0].position).toEqual({ x: 0, y: 0 });
    expect(NODE_WIDTH).toBeGreaterThan(0);
    expect(NODE_HEIGHT).toBeGreaterThan(0);
  });

  it("gives every edge a stable unique id", () => {
    const { edges } = buildGraph(
      DIAMOND.tasks,
      DIAMOND.edges,
      DIAMOND.parameters,
    );
    const edgeIds = edges.map((edge) => edge.id);

    expect(new Set(edgeIds).size).toBe(edgeIds.length);
    expect(edgeIds).toContain("load_devices->save_dataset");
  });
});
