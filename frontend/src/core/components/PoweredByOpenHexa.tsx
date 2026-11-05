import useOpenhexaWebsiteUrl from "core/hooks/useOpenhexaWebsiteUrl";
import { useTranslation } from "next-i18next";
import Image from "next/image";
import logo from "public/images/logo.svg";

type PoweredByOpenHexaProps = {
  // Groups the banner traffic of one kind of public page
  utmSource?: string;
  // The surface within that kind (iframe, static…)
  utmContent?: string;
};

const PoweredByOpenHexa = ({
  utmSource,
  utmContent,
}: PoweredByOpenHexaProps) => {
  const { t } = useTranslation();
  const href = useOpenhexaWebsiteUrl(
    utmSource && utmContent
      ? {
          source: utmSource,
          campaign: "powered-by-openhexa-banner",
          content: utmContent,
        }
      : undefined,
  );

  return (
    <div className="flex items-center justify-center border-t bg-gray-50 py-2 text-xs text-gray-500">
      {t("Powered by")}{" "}
      <a
        href={href}
        target="_blank"
        rel="nofollow noopener noreferrer"
        className="ml-1 flex items-center gap-1 font-medium text-blue-600 hover:text-blue-500"
      >
        <Image
          src={logo}
          alt="OpenHEXA"
          className="h-4 w-4"
          width={16}
          height={16}
        />
        OpenHEXA
      </a>
    </div>
  );
};

export default PoweredByOpenHexa;
