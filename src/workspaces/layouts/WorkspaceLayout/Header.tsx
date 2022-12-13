import clsx from "clsx";
import { ReactNode } from "react";

type HeaderProps = {
  children?: ReactNode;
  className?: string;
};

const Header = (props: HeaderProps) => {
  const { className, children } = props;
  return (
    <div
      className={clsx(
        "sticky top-0 z-10 flex h-16 flex-shrink-0 items-center justify-between border-b border-gray-200 bg-white py-3 shadow",
        "px-4 md:px-6 xl:px-10 2xl:px-12"
      )}
    >
      <div className={clsx("flex-1", className)}>{children}</div>
    </div>
  );
};

export default Header;
