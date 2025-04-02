import clsx from "clsx";
import { HTMLAttributes } from "react";

type CardContentProps = HTMLAttributes<HTMLDivElement>;

const CardContent = (props: CardContentProps) => {
  const { className, children, ...delegated } = props;
  return (
    <div className={clsx("flex-1 text-gray-600", className)} {...delegated}>
      {children}
    </div>
  );
};

export default CardContent;
