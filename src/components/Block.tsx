import clsx from "clsx";
import {
  ComponentClass,
  createElement,
  FunctionComponent,
  HTMLAttributes,
  ReactNode,
} from "react";

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
        "sm:rounded-lg overflow-hidden shadow border-b border-gray-200 bg-white",
        className
      ),
    },
    children
  );
};

Block.Content = function BlockContent({
  children,
  className,
}: HTMLAttributes<HTMLDivElement>) {
  return <div className={clsx("px-4 py-5 sm:px-6", className)}>{children}</div>;
};

Block.Title = function BlockTitle({
  className,
  children,
}: HTMLAttributes<HTMLHeadingElement>) {
  return (
    <h3
      className={clsx(
        "px-4 py-5 pt-7 text-lg font-medium leading-4 text-gray-900 sm:px-6",
        className
      )}
    >
      {children}
    </h3>
  );
};

export default Block;
