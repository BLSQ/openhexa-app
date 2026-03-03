import React, { ReactElement, ReactNode } from "react";
import { useTranslation } from "next-i18next";
import { ArrowTopRightOnSquareIcon } from "@heroicons/react/24/outline";
import Tooltip from "core/components/Tooltip";
import Link from "core/components/Link";
import { getPublicEnv } from "core/helpers/runtimeConfig";

type Props = {
  isLimitReached: boolean;
  children: ReactElement;
  title?: string;
  tooltipLabel?: ReactNode;
};

const SubscriptionLimitTooltip = ({
  isLimitReached,
  children,
  title,
  tooltipLabel,
}: Props) => {
  const { t } = useTranslation();
  const { CONSOLE_URL } = getPublicEnv();

  if (!isLimitReached) return children;

  const defaultLabel = (
    <>
      <span>{title ?? t("You've reached the limit for your subscription plan.")}</span>
      {CONSOLE_URL && (
        <Link
          href={CONSOLE_URL}
          target="_blank"
          noStyle
          className="mt-1 flex items-center gap-1 text-blue-600 hover:text-blue-800"
        >
          {t("Upgrade your subscription")}
          <ArrowTopRightOnSquareIcon className="h-3 w-3" />
        </Link>
      )}
    </>
  );

  return (
    <Tooltip
      interactive
      renderTrigger={(ref) => (
        <span ref={ref as React.Ref<HTMLSpanElement>} className="inline-flex">
          {React.cloneElement(children, { disabled: true })}
        </span>
      )}
      label={tooltipLabel ?? defaultLabel}
    />
  );
};

export default SubscriptionLimitTooltip;
