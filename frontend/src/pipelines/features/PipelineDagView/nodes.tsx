import { Handle, Position, type NodeProps } from "@xyflow/react";
import clsx from "clsx";
import { useTranslation } from "next-i18next";
import { NODE_HEIGHT, NODE_WIDTH } from "./layout";

const size = { width: NODE_WIDTH, height: NODE_HEIGHT };

/** Handles are what React Flow attaches edges to; without them edges render detached. */
const handleClassName = "!h-1.5 !w-1.5 !border-0 !bg-gray-300";

export const ParameterNode = ({ data }: NodeProps) => {
  const { t } = useTranslation();
  const { label, type, required } = data as {
    label: string;
    type: string | null;
    required: boolean;
  };

  return (
    <div
      style={size}
      className="flex flex-col justify-center rounded-md border border-dashed border-gray-300 bg-gray-50 px-3"
      title={type ? `${label} (${type})` : label}
    >
      <div className="flex items-baseline gap-1.5">
        <span className="truncate text-xs font-medium text-gray-700">
          {label}
        </span>
        {required && (
          <span className="text-xs text-red-500" title={t("Required")}>
            *
          </span>
        )}
      </div>
      {type && (
        <span className="truncate font-mono text-[10px] text-gray-400">
          {type}
        </span>
      )}
      <Handle
        type="source"
        position={Position.Right}
        className={handleClassName}
      />
    </div>
  );
};

export const TaskNode = ({ data }: NodeProps) => {
  const { label } = data as { label: string };

  return (
    <div
      style={size}
      className={clsx(
        "flex items-center justify-center rounded-md border border-gray-200 bg-white px-3",
        "shadow-sm",
      )}
      title={label}
    >
      <Handle
        type="target"
        position={Position.Left}
        className={handleClassName}
      />
      <span className="truncate font-mono text-xs text-gray-700">{label}</span>
      <Handle
        type="source"
        position={Position.Right}
        className={handleClassName}
      />
    </div>
  );
};

export const nodeTypes = { parameter: ParameterNode, task: TaskNode };
