import { Handle, Position } from "@xyflow/react";
import {
  PlayIcon,
  ClockIcon,
  LinkIcon,
  CircleStackIcon,
  DocumentIcon,
  Squares2X2Icon,
  AdjustmentsHorizontalIcon,
} from "@heroicons/react/24/outline";
import { PipelineDagOutputType } from "graphql/types";
import { DagOutputType, PipelineParameter } from "./buildDagElements";

const TRIGGER_ICON: Record<string, typeof PlayIcon> = {
  manual: PlayIcon,
  schedule: ClockIcon,
  webhook: LinkIcon,
};

export const TriggerNode = ({
  data,
}: {
  data: { label: string; kind: string };
}) => {
  const Icon = TRIGGER_ICON[data.kind] ?? PlayIcon;
  return (
    <div className="flex items-center gap-2 rounded-lg border border-gray-200 bg-white px-3 py-2 shadow-sm">
      <Icon className="h-4 w-4 text-gray-500" />
      <span className="text-xs font-medium text-gray-900">{data.label}</span>
      <Handle
        type="source"
        position={Position.Right}
        className="!bg-gray-300"
      />
    </div>
  );
};

export const TaskNode = ({ data }: { data: { label: string } }) => (
  <div className="flex items-center gap-2 rounded-lg border border-indigo-200 bg-white px-3 py-2 shadow-sm">
    <Handle type="target" position={Position.Left} className="!bg-gray-300" />
    <span className="flex h-5 w-5 items-center justify-center rounded bg-indigo-100 text-[10px] font-semibold text-indigo-700">
      ƒ
    </span>
    <span className="text-xs font-semibold text-gray-900">{data.label}</span>
    <Handle type="source" position={Position.Right} className="!bg-gray-300" />
  </div>
);

export const PipelineNode = ({
  data,
}: {
  data: { label: string; hasTasks?: boolean };
}) => (
  <div className="relative h-full w-full rounded-xl border-2 border-blue-200 bg-blue-50/40">
    <Handle type="target" position={Position.Left} className="!bg-blue-300" />
    <div
      className={
        data.hasTasks
          ? "absolute left-0 top-0 px-3 py-1.5 text-xs font-semibold text-blue-800"
          : "flex h-full w-full items-center justify-center px-3 text-xs font-semibold text-blue-800"
      }
    >
      {data.label}
    </div>
    <Handle type="source" position={Position.Right} className="!bg-blue-300" />
  </div>
);

const OUTPUT_META: Record<
  DagOutputType,
  { label: string; Icon: typeof CircleStackIcon; dot: string }
> = {
  [PipelineDagOutputType.Db]: {
    label: "Database",
    Icon: CircleStackIcon,
    dot: "bg-blue-500",
  },
  [PipelineDagOutputType.File]: {
    label: "Files",
    Icon: DocumentIcon,
    dot: "bg-green-500",
  },
  [PipelineDagOutputType.Dataset]: {
    label: "Datasets",
    Icon: Squares2X2Icon,
    dot: "bg-violet-500",
  },
};

export const OutputGroupNode = ({
  data,
}: {
  data: {
    outputType: DagOutputType;
    items: { id: string; name?: string | null }[];
  };
}) => {
  const meta = OUTPUT_META[data.outputType];
  return (
    <div className="min-w-[150px] rounded-lg border border-dashed border-slate-300 bg-slate-50 p-2">
      <Handle type="target" position={Position.Left} className="!bg-gray-300" />
      <div className="mb-1.5 flex items-center gap-1.5 text-[10px] font-bold uppercase tracking-wide text-slate-600">
        <meta.Icon className="h-3 w-3" />
        {meta.label}
      </div>
      {data.items.map((o) => (
        <div
          key={o.id}
          className="mb-1 flex items-center gap-1.5 rounded border border-gray-200 bg-white px-2 py-1 text-[11px] text-gray-900"
        >
          <span className={`h-2 w-2 rounded-full ${meta.dot}`} />
          {o.name ?? meta.label.toLowerCase()}
        </div>
      ))}
    </div>
  );
};

export const ParametersNode = ({
  data,
}: {
  data: { items: PipelineParameter[] };
}) => (
  <div className="min-w-[180px] rounded-lg border border-dashed border-slate-300 bg-slate-50 p-2">
    <div className="mb-1.5 flex items-center gap-1.5 text-[10px] font-bold uppercase tracking-wide text-slate-600">
      <AdjustmentsHorizontalIcon className="h-3 w-3" />
      Parameters
    </div>
    {data.items.map((p) => (
      <div
        key={p.code}
        className="mb-1 flex items-center justify-between gap-2 rounded border border-gray-200 bg-white px-2 py-1 text-[11px]"
      >
        <span className="text-gray-900">{p.name || p.code}</span>
        <code className="rounded bg-gray-100 px-1 text-[10px] text-gray-600">
          {p.type}
        </code>
      </div>
    ))}
    <Handle type="source" position={Position.Right} className="!bg-gray-300" />
  </div>
);

export const nodeTypes = {
  trigger: TriggerNode,
  task: TaskNode,
  pipeline: PipelineNode,
  outputGroup: OutputGroupNode,
  parameters: ParametersNode,
};
