import { gql } from "@apollo/client";
import { Background, Controls, ReactFlow } from "@xyflow/react";
import clsx from "clsx";
import { useTranslation } from "next-i18next";
import { useMemo } from "react";
import { buildGraph } from "./layout";
import { nodeTypes } from "./nodes";
import type { PipelineDagView_VersionFragment } from "./PipelineDagView.generated";

// React Flow positions everything through these styles; without them the canvas renders as a
// pile of overlapping divs. base.css is the structural minimum — the full style.css also
// carries their visual theme, which the Tailwind-styled nodes would fight.
import "@xyflow/react/dist/base.css";

type PipelineDagViewProps = {
  version: PipelineDagView_VersionFragment;
  className?: string;
};

const PipelineDagView = ({ version, className }: PipelineDagViewProps) => {
  const { t } = useTranslation();

  const { nodes, edges } = useMemo(
    () =>
      buildGraph(
        version.dag.tasks,
        version.dag.edges,
        version.parameters ?? [],
      ),
    [version.dag.tasks, version.dag.edges, version.parameters],
  );

  if (nodes.length === 0) {
    return null;
  }

  return (
    <div
      className={clsx(
        "h-80 w-full overflow-hidden rounded-md border border-gray-100 bg-gray-50/50",
        className,
      )}
      data-testid="pipeline-dag-view"
      aria-label={t("Pipeline task graph")}
    >
      <ReactFlow
        nodes={nodes}
        edges={edges}
        nodeTypes={nodeTypes}
        fitView
        // The canvas sits inside a scrolling page: zooming on scroll would trap the wheel and
        // make the page feel broken. Zoom stays available through the controls.
        zoomOnScroll={false}
        preventScrolling={false}
        nodesDraggable={false}
        nodesConnectable={false}
        edgesFocusable={false}
        proOptions={{ hideAttribution: true }}
      >
        <Background gap={16} size={1} color="#e5e7eb" />
        <Controls showInteractive={false} position="bottom-right" />
      </ReactFlow>
    </div>
  );
};

PipelineDagView.fragments = {
  version: gql`
    fragment PipelineDagView_version on PipelineVersion {
      id
      parameters {
        code
        name
        type
        required
      }
      dag {
        tasks {
          id
          name
        }
        edges {
          source
          target
        }
      }
    }
  `,
};

export default PipelineDagView;
