import clsx from "clsx";
import { ReactNode } from "react";

type SettingsCardProps = {
  title?: ReactNode;
  actions?: ReactNode;
  footer?: ReactNode;
  className?: string;
  children: ReactNode;
};

const SettingsCard = ({
  title,
  actions,
  footer,
  className,
  children,
}: SettingsCardProps) => (
  <div
    className={clsx(
      "rounded-[10px] border border-gray-200 bg-white px-5 py-4",
      className,
    )}
  >
    {(title || actions) && (
      <div className="mb-3.5 flex items-center justify-between gap-3">
        {title && (
          <h3 className="text-sm font-semibold text-gray-900">{title}</h3>
        )}
        {actions}
      </div>
    )}
    {children}
    {footer && <div className="mt-4 flex justify-end gap-2">{footer}</div>}
  </div>
);

export default SettingsCard;
