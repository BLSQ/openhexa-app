import dagre from "@dagrejs/dagre";
import { Position, type Edge, type Node } from "@xyflow/react";

/**
 * Turning a pipeline's DAG into positioned nodes is kept out of the component so it can be
 * tested on its own: React Flow only renders what it is given, and the interesting decisions
 * (which nodes exist, how they are wired, where they sit) all happen here.
 */

export type DagTask = { id: string; name: string };
export type DagEdge = { source: string; target: string };
export type DagParameter = {
  code: string;
  name: string;
  type: string;
  required: boolean;
};

export type ParameterNodeData = {
  label: string;
  code: string;
  type: string;
  required: boolean;
  [key: string]: unknown;
};

export type TaskNodeData = { label: string; [key: string]: unknown };

// dagre needs dimensions up front, so nodes are fixed-size and long names truncate in CSS.
export const NODE_WIDTH = 180;
export const NODE_HEIGHT = 48;

const RANK_SEPARATION = 90;
const NODE_SEPARATION = 24;

export const isParameterNode = (node: Node) => node.type === "parameter";

/**
 * Build the React Flow graph for a version.
 *
 * The backend already keeps only the parameters that reach a task, and only edges between
 * known nodes, so every input here becomes a node or an edge as is.
 */
export const buildGraph = (
  tasks: DagTask[],
  dagEdges: DagEdge[],
  parameters: DagParameter[],
): { nodes: Node[]; edges: Edge[] } => {
  if (tasks.length === 0) {
    return { nodes: [], edges: [] };
  }

  const nodes: Node[] = [
    ...parameters.map((parameter) => ({
      id: parameter.code,
      type: "parameter",
      position: { x: 0, y: 0 },
      data: {
        label: parameter.name,
        code: parameter.code,
        type: parameter.type,
        required: parameter.required,
      } satisfies ParameterNodeData,
    })),
    ...tasks.map((task) => ({
      id: task.id,
      type: "task",
      position: { x: 0, y: 0 },
      data: { label: task.name } satisfies TaskNodeData,
    })),
  ];

  const flowEdges: Edge[] = dagEdges.map((edge) => ({
    id: `${edge.source}->${edge.target}`,
    source: edge.source,
    target: edge.target,
    type: "smoothstep",
    animated: false,
  }));

  return { nodes: layout(nodes, flowEdges), edges: flowEdges };
};

/**
 * Position nodes left to right with dagre.
 *
 * dagre anchors a node by its centre while React Flow anchors by its top-left corner, so the
 * result is shifted by half the node's size — omitting that offset is the classic way this
 * integration drifts.
 */
export const layout = (nodes: Node[], edges: Edge[]): Node[] => {
  const graph = new dagre.graphlib.Graph();
  graph.setDefaultEdgeLabel(() => ({}));
  graph.setGraph({
    rankdir: "LR",
    ranksep: RANK_SEPARATION,
    nodesep: NODE_SEPARATION,
  });

  nodes.forEach((node) =>
    graph.setNode(node.id, { width: NODE_WIDTH, height: NODE_HEIGHT }),
  );
  edges.forEach((edge) => graph.setEdge(edge.source, edge.target));

  dagre.layout(graph);

  return nodes.map((node) => {
    const { x, y } = graph.node(node.id);
    return {
      ...node,
      position: { x: x - NODE_WIDTH / 2, y: y - NODE_HEIGHT / 2 },
      sourcePosition: Position.Right,
      targetPosition: Position.Left,
    };
  });
};
