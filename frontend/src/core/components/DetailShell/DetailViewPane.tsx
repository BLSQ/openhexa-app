import clsx from "clsx";
import { ReactNode } from "react";

type DetailViewPaneProps = {
  className?: string;
  children: ReactNode;
};

const DetailViewPane = ({ className, children }: DetailViewPaneProps) => (
  <div className={clsx("min-h-0 flex-1 overflow-auto", className)}>
    {children}
  </div>
);

export default DetailViewPane;
