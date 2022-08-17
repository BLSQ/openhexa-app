import _ from "lodash";
import { ReactElement, useMemo } from "react";
import { BaseColumnProps } from "./BaseColumn";
import { useCellContext } from "./helpers";

type TextColumnProps = BaseColumnProps & {
  textPath?: string;
  defaultValue?: ReactElement | string;
  subtextPath?: string;
};

export function TextColumn(props: TextColumnProps) {
  const { textPath, subtextPath, defaultValue } = props;
  const cell = useCellContext();

  const text = useMemo(
    () => (textPath ? _.get(cell.value, textPath) : cell.value),
    [cell.value, textPath]
  );
  const subtext = useMemo(
    () => (subtextPath ? _.get(cell.value, subtextPath) : "-"),
    [cell.value, subtextPath]
  );

  return (
    <div className="w-full">
      <div title={text} className="truncate lg:whitespace-nowrap">
        {text ?? defaultValue}
      </div>
      {subtextPath && (
        <div className="mt-1 text-xs text-gray-400">{subtext}</div>
      )}
    </div>
  );
}
