import { useMemo } from "react";
import { ReactFlow, Background, Controls } from "@xyflow/react";
import "@xyflow/react/dist/style.css";
import { buildDagElements, PipelineDag, Triggers } from "./buildDagElements";
import { nodeTypes } from "./nodes";

type Props = {
  triggers: Triggers;
  dag: PipelineDag;
  pipelineName: string;
};

const PipelineDagView = ({ triggers, dag, pipelineName }: Props) => {
  const { nodes, edges } = useMemo(
    () => buildDagElements({ triggers, dag, pipelineName }),
    [triggers, dag, pipelineName],
  );

  return (
    <div className="h-96 w-full rounded-md border border-gray-100 bg-gray-50">
      <ReactFlow
        nodes={nodes}
        edges={edges}
        nodeTypes={nodeTypes}
        fitView
        zoomOnScroll={false}
        panOnScroll={false}
        nodesDraggable={false}
        nodesConnectable={false}
        proOptions={{ hideAttribution: true }}
      >
        <Background gap={16} color="#e5e7eb" />
        <Controls showInteractive={false} />
      </ReactFlow>
    </div>
  );
};

export default PipelineDagView;
