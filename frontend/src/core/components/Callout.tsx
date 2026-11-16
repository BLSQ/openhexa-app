import {
  ExclamationTriangleIcon,
  InformationCircleIcon,
} from "@heroicons/react/24/outline";
import clsx from "clsx";
import { ReactNode } from "react";

const VARIANTS = {
  // Context that explains what the user sees.
  info: {
    Icon: InformationCircleIcon,
    className: "bg-blue-50 text-blue-800",
    iconClassName: "text-blue-600",
  },
  // Consequences of an action that the user must not miss.
  warning: {
    Icon: ExclamationTriangleIcon,
    className: "bg-amber-50 text-amber-800",
    iconClassName: "",
  },
};

type CalloutProps = {
  variant?: keyof typeof VARIANTS;
  className?: string;
  children: ReactNode;
};

const Callout = ({ variant = "info", className, children }: CalloutProps) => {
  const {
    Icon,
    className: variantClassName,
    iconClassName,
  } = VARIANTS[variant];
  return (
    <div
      className={clsx(
        "flex gap-2 rounded-md p-3 text-sm",
        variantClassName,
        className,
      )}
    >
      <Icon className={clsx("h-5 w-5 shrink-0", iconClassName)} />
      <p>{children}</p>
    </div>
  );
};

export default Callout;
