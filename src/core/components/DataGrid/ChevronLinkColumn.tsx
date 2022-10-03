import { ChevronRightIcon } from "@heroicons/react/20/solid";
import { useTranslation } from "next-i18next";
import LinkColumn, { LinkColumnProps } from "./LinkColumn";

type ChevronLinkColumnProps = LinkColumnProps;

const ChevronLinkColumn = (props: ChevronLinkColumnProps) => {
  const { t } = useTranslation();

  return (
    <div className="w-full">
      <LinkColumn {...props}>
        <div className="flex w-full items-center justify-end ">
          {t("View")}
          <ChevronRightIcon className="inline h-5" />
        </div>
      </LinkColumn>
    </div>
  );
};

export default ChevronLinkColumn;
