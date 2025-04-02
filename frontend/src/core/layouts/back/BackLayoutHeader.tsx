import { ChevronLeftIcon } from "@heroicons/react/24/outline";
import Button from "core/components/Button";
import { FC, ReactNode } from "react";
import { useTranslation } from "react-i18next";

type Props = {
  title: string | ReactNode;
  onBack?: () => void;
};

const BackLayoutHeader: FC<Props> = ({ onBack, title }) => {
  const { t } = useTranslation();
  return (
    <div className={"w-full sticky top-0 bg-gray-800"}>
      <div
        className={
          "text-white px-2 sm:px-6 lg:px-8 flex max-w-7xl mx-auto items-center gap-6  h-16"
        }
      >
        <Button
          onClick={onBack}
          variant={"custom"}
          className={"text-white border-none hover:bg-gray-600"}
          leadingIcon={<ChevronLeftIcon className={"w-6 h-6 -my-2"} />}
        >
          {t("Back")}
        </Button>
        <div className={"flex-1 font-medium text-gray-50"}>{title}</div>
      </div>
    </div>
  );
};

export default BackLayoutHeader;
