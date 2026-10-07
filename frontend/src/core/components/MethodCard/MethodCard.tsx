import clsx from "clsx";
import { ReactNode } from "react";

type MethodCardProps = {
  icon: ReactNode;
  title: string;
  description: string;
  onClick: () => void;
  disabled?: boolean;
  footer?: ReactNode;
};

const MethodCard = ({
  icon,
  title,
  description,
  onClick,
  disabled = false,
  footer,
}: MethodCardProps) => (
  <button
    onClick={onClick}
    disabled={disabled}
    className={clsx(
      "flex flex-1 flex-col items-start rounded-xl border border-gray-200 bg-white p-5 text-left shadow-sm transition-all",
      disabled
        ? "cursor-not-allowed opacity-60"
        : "hover:border-blue-400 hover:bg-blue-50 hover:shadow-md",
    )}
  >
    <div className="mb-4 rounded-lg bg-blue-50 p-2.5">{icon}</div>
    <span className="font-semibold text-gray-900">{title}</span>
    <span className="mt-1 text-sm leading-relaxed text-gray-500">
      {description}
    </span>
    {footer}
  </button>
);

export default MethodCard;
