import clsx from "clsx";
import React, { ReactNode } from "react";

type TitleProps = {
  level: 1 | 2 | 3 | 4 | 5 | 6;
  className?: string;
  children: ReactNode;
};

const Classes = {
  1: "font-semibold text-2xl mb-6",
  2: "font-semibold text-xl mb-4",
  3: "font-medium text-xl mb-3",
  4: "font-medium text-lg mb-2.5",
  5: "font-medium text-md mb-2",
  6: "font-medium text-md mb-1",
};

const Title = (props: TitleProps) => {
  const { level, children, className } = props;

  return React.createElement(
    `h${level}`,
    {
      className: clsx(className, Classes[level]),
    },
    children,
  );
};

export default Title;
