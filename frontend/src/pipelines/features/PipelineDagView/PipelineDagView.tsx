import { useMemo } from "react";
import { ReactFlow, Background, Controls } from "@xyflow/react";
import "@xyflow/react/dist/style.css";
import {
  buildDagElements,
  PipelineDag,
  PipelineParameter,
  Triggers,
} from "./buildDagElements";
import { nodeTypes } from "./nodes";

type Props = {
  triggers: Triggers;
  dag: PipelineDag;
  parameters: PipelineParameter[];
  pipelineName: string;
};

const PipelineDagView = ({
  triggers,
  dag,
  parameters,
  pipelineName,
}: Props) => {
  const { nodes, edges } = useMemo(
    () => buildDagElements({ triggers, dag, parameters, pipelineName }),
    [triggers, dag, parameters, pipelineName],
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
