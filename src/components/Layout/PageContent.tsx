import clsx from "clsx";
import { HTMLAttributes } from "react";

export function PageHeader({
  className,
  ...delegated
}: HTMLAttributes<HTMLDivElement>) {
  return (
    <div className="bg-blue">
      <div
        {...delegated}
        className={clsx(
          "max-w-5xl px-4 sm:px-4 md:px-8 py-4 md:py-8 w-full mx-auto",
          className
        )}
      />
    </div>
  );
}

export function PageContent(props: HTMLAttributes<HTMLDivElement>) {
  const { children, className, ...delegated } = props;
  return (
    <main
      className="flex-1 bg-gray-50 pb-6 before:bg-blue before:block before:h-16 before:content-['']"
      {...delegated}
    >
      <div
        className={clsx(
          "max-w-5xl px-4 sm:px-4 md:px-8 w-full mx-auto -mt-16",
          className
        )}
      >
        {children}
      </div>
    </main>
  );
}
