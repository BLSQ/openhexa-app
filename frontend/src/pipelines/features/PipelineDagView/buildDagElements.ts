import dagre from "@dagrejs/dagre";
import { Edge, Node } from "@xyflow/react";
import { PipelineDagOutputType } from "graphql/types";

export type DagOutputType = PipelineDagOutputType;

export type PipelineDag = {
  tasks: { id: string; name: string }[];
  edges: { source: string; target: string }[];
  outputs: {
    id: string;
    type: DagOutputType;
    name?: string | null;
    taskId?: string | null;
  }[];
};

export type Triggers = {
  manual: boolean;
  schedule?: string | null;
  webhook: boolean;
};

export const PIPELINE_NODE_ID = "pipeline";

const NODE_W = 180;
const NODE_H = 44;
const TRIGGER_W = 160;
const TRIGGER_H = 44;
const GROUP_W = 172;
const CONTAINER_PAD = 16; // inner padding around the task graph
const CONTAINER_HEADER = 30; // top space reserved for the pipeline name

type Sized = { id: string; width: number; height: number };
type DagreGraph = InstanceType<typeof dagre.graphlib.Graph>;
type DagreNode = { x: number; y: number; width: number; height: number };

const nodeOf = (g: DagreGraph, id: string): DagreNode =>
  g.node(id) as DagreNode;

const runDagre = (
  sized: Sized[],
  edges: { source: string; target: string }[],
  ranksep: number,
): DagreGraph => {
  const g = new dagre.graphlib.Graph();
  g.setGraph({ rankdir: "LR", nodesep: 24, ranksep });
  g.setDefaultEdgeLabel(() => ({}));
  sized.forEach((n) => g.setNode(n.id, { width: n.width, height: n.height }));
  edges.forEach((e) => g.setEdge(e.source, e.target));
  dagre.layout(g);
  return g;
};

const topLeft = (g: DagreGraph, id: string): { x: number; y: number } => {
  const n = nodeOf(g, id);
  return { x: n.x - n.width / 2, y: n.y - n.height / 2 };
};

export const buildDagElements = ({
  triggers,
  dag,
  pipelineName,
}: {
  triggers: Triggers;
  dag: PipelineDag;
  pipelineName: string;
}): { nodes: Node[]; edges: Edge[] } => {
  const nodes: Node[] = [];
  const edges: Edge[] = [];

  const triggerNodes: { id: string; label: string; kind: string }[] = [];
  if (triggers.manual)
    triggerNodes.push({
      id: "trigger-manual",
      label: "Manual",
      kind: "manual",
    });
  if (triggers.schedule)
    triggerNodes.push({
      id: "trigger-schedule",
      label: triggers.schedule,
      kind: "schedule",
    });
  if (triggers.webhook)
    triggerNodes.push({
      id: "trigger-webhook",
      label: "Webhook",
      kind: "webhook",
    });

  const hasTasks = dag.tasks.length > 0;

  // --- inner layout: position the task graph and measure the container ---
  const childPosition = new Map<string, { x: number; y: number }>();
  let containerW = NODE_W + CONTAINER_PAD * 2;
  let containerH = NODE_H + CONTAINER_HEADER + CONTAINER_PAD;
  if (hasTasks) {
    const inner = runDagre(
      dag.tasks.map((t) => ({ id: t.id, width: NODE_W, height: NODE_H })),
      dag.edges,
      80,
    );
    let minX = Infinity;
    let minY = Infinity;
    let maxX = -Infinity;
    let maxY = -Infinity;
    dag.tasks.forEach((t) => {
      const n = nodeOf(inner, t.id);
      minX = Math.min(minX, n.x - NODE_W / 2);
      maxX = Math.max(maxX, n.x + NODE_W / 2);
      minY = Math.min(minY, n.y - NODE_H / 2);
      maxY = Math.max(maxY, n.y + NODE_H / 2);
    });
    dag.tasks.forEach((t) => {
      const n = nodeOf(inner, t.id);
      childPosition.set(t.id, {
        x: n.x - NODE_W / 2 - minX + CONTAINER_PAD,
        y: n.y - NODE_H / 2 - minY + CONTAINER_HEADER,
      });
    });
    containerW = maxX - minX + CONTAINER_PAD * 2;
    containerH = maxY - minY + CONTAINER_HEADER + CONTAINER_PAD;
  }

  // --- group outputs by type ---
  const grouped = new Map<DagOutputType, PipelineDag["outputs"]>();
  dag.outputs.forEach((o) => {
    const list = grouped.get(o.type) ?? [];
    list.push(o);
    grouped.set(o.type, list);
  });
  const groupOrder: DagOutputType[] = [
    PipelineDagOutputType.Db,
    PipelineDagOutputType.File,
    PipelineDagOutputType.Dataset,
  ];
  const groupDefs = groupOrder
    .filter((type) => grouped.has(type))
    .map((type) => {
      const items = grouped.get(type)!;
      return {
        id: `outputGroup-${type}`,
        type,
        items,
        height: 36 + items.length * 22,
      };
    });

  // --- outer layout: triggers -> pipeline container -> output groups ---
  const outerSized: Sized[] = [
    ...triggerNodes.map((t) => ({
      id: t.id,
      width: TRIGGER_W,
      height: TRIGGER_H,
    })),
    { id: PIPELINE_NODE_ID, width: containerW, height: containerH },
    ...groupDefs.map((gd) => ({
      id: gd.id,
      width: GROUP_W,
      height: gd.height,
    })),
  ];
  const outerEdges = [
    ...triggerNodes.map((t) => ({ source: t.id, target: PIPELINE_NODE_ID })),
    // synthetic edges so groups lay out to the right of the container; the
    // rendered edges (below) originate from the specific emitting task.
    ...groupDefs.map((gd) => ({ source: PIPELINE_NODE_ID, target: gd.id })),
  ];
  const outer = runDagre(outerSized, outerEdges, 120);

  // --- assemble nodes (parent must precede its children) ---
  triggerNodes.forEach((t) =>
    nodes.push({
      id: t.id,
      type: "trigger",
      position: topLeft(outer, t.id),
      data: { label: t.label, kind: t.kind },
    }),
  );
  nodes.push({
    id: PIPELINE_NODE_ID,
    type: "pipeline",
    position: topLeft(outer, PIPELINE_NODE_ID),
    data: { label: pipelineName, hasTasks },
    style: { width: containerW, height: containerH },
  });
  if (hasTasks) {
    dag.tasks.forEach((t) =>
      nodes.push({
        id: t.id,
        type: "task",
        parentId: PIPELINE_NODE_ID,
        extent: "parent",
        position: childPosition.get(t.id)!,
        data: { label: t.name },
      }),
    );
  }
  groupDefs.forEach((gd) =>
    nodes.push({
      id: gd.id,
      type: "outputGroup",
      position: topLeft(outer, gd.id),
      data: { outputType: gd.type, items: gd.items },
    }),
  );

  // --- assemble edges ---
  triggerNodes.forEach((t) =>
    edges.push({
      id: `e-${t.id}-${PIPELINE_NODE_ID}`,
      source: t.id,
      target: PIPELINE_NODE_ID,
    }),
  );
  if (hasTasks) {
    dag.edges.forEach((e) =>
      edges.push({
        id: `e-${e.source}-${e.target}`,
        source: e.source,
        target: e.target,
      }),
    );
  }
  groupDefs.forEach((gd) => {
    const taskIds = new Set(
      gd.items.map((o) => o.taskId).filter((id): id is string => Boolean(id)),
    );
    const sources =
      hasTasks && taskIds.size > 0 ? Array.from(taskIds) : [PIPELINE_NODE_ID];
    sources.forEach((src) =>
      edges.push({ id: `e-${src}-${gd.id}`, source: src, target: gd.id }),
    );
  });

  return { nodes, edges };
};
