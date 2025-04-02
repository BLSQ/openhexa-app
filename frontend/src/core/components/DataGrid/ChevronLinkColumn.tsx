import { ChevronRightIcon } from "@heroicons/react/20/solid";
import clsx from "clsx";
import { useTranslation } from "next-i18next";
import LinkColumn, { LinkColumnProps } from "./LinkColumn";

type ChevronLinkColumnProps = LinkColumnProps;

const ChevronLinkColumn = ({
  className,
  customStyle,
  noStyle,
  url,
}: ChevronLinkColumnProps) => {
  const { t } = useTranslation();

  return (
    <div className="w-full">
      <LinkColumn
        customStyle={customStyle}
        noStyle={noStyle}
        url={url}
        className={clsx(
          className,
          "flex w-full cursor-pointer items-center justify-end outline-hidden",
        )}
      >
        {t("View")}
        <ChevronRightIcon className="inline h-5" />
      </LinkColumn>
    </div>
  );
};

export default ChevronLinkColumn;
