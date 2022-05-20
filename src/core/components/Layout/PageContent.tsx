import clsx from "clsx";
import { HTMLAttributes } from "react";
import { LayoutClasses } from "./styles";

export function PageContent(props: HTMLAttributes<HTMLDivElement>) {
  const { children, className, ...delegated } = props;
  return (
    <main className={clsx(LayoutClasses.container, "pb-6")} {...delegated}>
      {children}
    </main>
  );
}
