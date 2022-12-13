import clsx from "clsx";
import { HTMLAttributes } from "react";

export default function PageContent(props: HTMLAttributes<HTMLDivElement>) {
  const { children, className } = props;
  return (
    <div className="py-6 xl:py-8">
      <div
        className={clsx("mx-auto px-4 md:px-6 xl:px-10  2xl:px-12", className)}
      >
        {children}
      </div>
    </div>
  );
}
