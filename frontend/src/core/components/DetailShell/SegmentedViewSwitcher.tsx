import clsx from "clsx";
import { ComponentType, ReactNode } from "react";

export type Segment<T extends string> = {
  id: T;
  label: string;
  icon: ComponentType<{ className?: string }>;
};

type SegmentedViewSwitcherProps<T extends string> = {
  segments: Segment<T>[];
  value: T;
  onChange: (id: T) => void;
  actions?: ReactNode;
};

const SegmentedViewSwitcher = <T extends string>({
  segments,
  value,
  onChange,
  actions,
}: SegmentedViewSwitcherProps<T>) => (
  <div className="flex flex-none items-center gap-3 border-b border-gray-100 px-5 py-2">
    <div className="inline-flex rounded-[7px] bg-gray-100 p-[3px]">
      {segments.map((segment) => {
        const Icon = segment.icon;
        const active = value === segment.id;
        return (
          <button
            key={segment.id}
            onClick={() => onChange(segment.id)}
            className={clsx(
              "inline-flex items-center gap-1.5 rounded-[5px] px-3 py-1 text-xs transition-colors",
              active
                ? "bg-white font-semibold text-gray-900 shadow-sm"
                : "font-medium text-gray-500 hover:text-gray-700",
            )}
          >
            <Icon className="h-3.5 w-3.5" />
            {segment.label}
          </button>
        );
      })}
    </div>
    {actions}
  </div>
);

export default SegmentedViewSwitcher;
