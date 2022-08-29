import clsx from "clsx";
import {
  getValue,
  ItemInstance,
  useItemContext,
  ValueAccessor,
} from "core/hooks/useItemContext";
import { ReactElement } from "react";
import Block from "../Block";

type HeadingProps<T> = {
  titleAccessor?: ValueAccessor;
  className?: string;
  renderActions?(item: T): ReactElement;
};

function Heading<T extends ItemInstance>(props: HeadingProps<T>) {
  const { titleAccessor, renderActions, className } = props;
  const { item } = useItemContext<T>();

  return (
    <Block.Title
      className={clsx(className, "flex items-center justify-between")}
    >
      {getValue(item, titleAccessor)}
      {renderActions ? renderActions(item) : null}
    </Block.Title>
  );
}

export default Heading;
