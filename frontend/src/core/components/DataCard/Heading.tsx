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
  children?(item: T): ReactElement;
};

function Heading<T extends ItemInstance>(props: HeadingProps<T>) {
  const {
    titleAccessor,
    subtitleAccessor,
    renderActions,
    className,
    children,
  } = props;
  const { item } = useItemContext<T>();

  const title = useMemo(
    () => getValue(item, titleAccessor),
    [item, titleAccessor],
  );
  const subtitle = useMemo(
    () => (subtitleAccessor ? getValue(item, subtitleAccessor) : null),
    [item, subtitleAccessor],
  );

  return (
    <Block.Header
      className={clsx(className, "flex items-center justify-between")}
    >
      {children ? (
        children(item)
      ) : (
        <div>
          {title ?? ""}
          {subtitle && (
            <div className="truncate pt-2 text-sm text-gray-500">
              {subtitle}
            </div>
          )}
        </div>
      )}
      {renderActions ? renderActions(item) : null}
    </Block.Header>
  );
}

export default Heading;
