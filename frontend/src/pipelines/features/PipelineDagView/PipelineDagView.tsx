import { gql } from "@apollo/client";
import { InformationCircleIcon } from "@heroicons/react/24/outline";
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
      buildGraph(version.dag.tasks, version.dag.edges, version.dag.parameters),
    [version.dag.tasks, version.dag.edges, version.dag.parameters],
  );

  if (nodes.length === 0) {
    return (
      <div
        className={clsx(
          "flex items-center gap-2 rounded-md bg-blue-50 p-3 text-sm text-blue-800",
          className,
        )}
        role="status"
      >
        <InformationCircleIcon className="h-5 w-5 shrink-0" />
        {t(
          "No task graph to display: this pipeline version has no functions decorated with @task.",
        )}
      </div>
    );
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
        // Nodes are styled for zoom 1; without this cap fitView blows small graphs up to the
        // default maxZoom (2) and they look oversized next to the rest of the page.
        fitViewOptions={{ maxZoom: 1 }}
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
      dag {
        tasks {
          id
          name
        }
        edges {
          source
          target
        }
        parameters {
          code
          name
          type
          required
        }
      }
    }
  `,
};

export default PipelineDagView;
