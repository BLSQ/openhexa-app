import clsx from "clsx";
import {
  getValue,
  ItemInstance,
  useItemContext,
  ValueAccessor,
} from "core/hooks/useItemContext";
import { ReactElement, useMemo } from "react";
import Block from "../Block";

type HeadingProps<T> = {
  titleAccessor?: ValueAccessor;
  subtitleAccessor?: ValueAccessor;
  className?: string;
  renderActions?(item: T): ReactElement;
};

function Heading<T extends ItemInstance>(props: HeadingProps<T>) {
  const { titleAccessor, subtitleAccessor, renderActions, className } = props;
  const { item } = useItemContext<T>();

  const title = useMemo(
    () => getValue(item, titleAccessor),
    [item, titleAccessor]
  );
  const subtitle = useMemo(
    () => getValue(item, subtitleAccessor),
    [item, subtitleAccessor]
  );

  return (
    <Block.Title
      className={clsx(className, "flex items-center justify-between")}
    >
      <div>
        {title}
        {subtitle && (
          <div className="truncate pt-2 text-sm text-gray-500">{subtitle}</div>
        )}
      </div>
      {renderActions ? renderActions(item) : null}
    </Block.Title>
  );
}

export default Heading;
