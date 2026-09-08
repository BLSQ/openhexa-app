import { ArrowUturnLeftIcon } from "@heroicons/react/24/outline";
import { useTranslation } from "next-i18next";
import { ReactNode } from "react";

type BrowsingVersionBannerProps = {
  label: ReactNode;
  actions?: ReactNode;
  backLabel?: string;
  onBack: () => void;
};

const BrowsingVersionBanner = ({
  label,
  actions,
  backLabel,
  onBack,
}: BrowsingVersionBannerProps) => {
  const { t } = useTranslation();

  return (
    <div className="flex flex-none items-center gap-3 border-b border-amber-100 bg-amber-50 px-5 py-2 text-[13px]">
      <span className="text-amber-800">{label}</span>
      <div className="ml-auto flex items-center gap-3">
        {actions}
        <button
          onClick={onBack}
          className="inline-flex items-center gap-1.5 text-xs font-medium text-amber-800 hover:text-amber-900"
        >
          <ArrowUturnLeftIcon className="h-3.5 w-3.5" />
          {backLabel ?? t("Back to latest")}
        </button>
      </div>
    </div>
  );
};

export default BrowsingVersionBanner;
