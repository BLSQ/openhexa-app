import clsx from "clsx";
import { HTMLAttributes, ReactNode } from "react";

const BlockContent = ({
  children,
  className,
  title,
}: HTMLAttributes<HTMLDivElement> & { title?: ReactNode | string }) => {
  return (
    <section className="px-4 py-5 sm:px-6">
      {title && <h4 className="pb-4 font-medium">{title}</h4>}
      <div className={className}>{children}</div>
    </section>
  );
};

export default BlockContent;
