import { SparklesIcon } from "@heroicons/react/24/outline";
import clsx from "clsx";
import { useTranslation } from "next-i18next";
import Link from "next/link";

type AiDisabledBannerProps = {
  asCard?: boolean
};

const AiDisabledBanner = ({asCard}: AiDisabledBannerProps) => {
  const { t } = useTranslation();

  return (
    <div className={clsx(
      "flex flex-col items-center gap-4 p-10 text-center",
      asCard && "rounded-2xl bg-white shadow-md")}
    >
      <div className="flex rounded-full bg-amber-100 p-4">
        <SparklesIcon className="h-8 w-8 text-amber-600" />
      </div>
      <div>
        <h2 className="text-lg font-semibold text-gray-900">
          {t("AI features are not enabled")}
        </h2>
        <p className="mt-1 text-sm text-gray-500">
          {t("Enable AI features in your account settings to use the OpenHEXA assistant.")}
        </p>
      </div>
      <Link
        href="/user/account"
        className="rounded-md bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700"
      >
        {t("Go to account settings")}
      </Link>
    </div>
  )
}

export default AiDisabledBanner;
