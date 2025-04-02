import clsx from "clsx";
import {
  ComponentClass,
  createElement,
  FunctionComponent,
  HTMLAttributes,
  ReactNode,
} from "react";
import BlockContent from "./BlockContent";
import BlockHeader from "./BlockHeader";
import BlockSection from "./BlockSection";

type Props = {
  as?: string | FunctionComponent | ComponentClass;
  children: ReactNode | undefined | null;
} & HTMLAttributes<HTMLElement>;

const Block = (props: Props) => {
  const { children, className, ...delegated } = props;

  return createElement<{ className?: string }>(
    props.as ?? "article",
    {
      ...delegated,
      className: clsx(
        "sm:rounded-lg overflow-hidden shadow-xs border-b border-gray-200 bg-white",
        className,
      ),
    },
    children,
  );
};

Block.Content = BlockContent;
Block.Section = BlockSection;
Block.Header = BlockHeader;

export default Block;
