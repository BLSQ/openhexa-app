import { ReactNode } from "react";
import { ChevronLeftIcon } from "@heroicons/react/20/solid";
import { useTranslation } from "next-i18next";
import Button from "core/components/Button";
import clsx from "clsx";

type BackLayoutProps = {
  title: string | ReactNode;
  children: ReactNode;
  onBack?: () => void;
  className?: string;
};

const BackLayout = ({
  children,
  title,
  onBack,
  className,
}: BackLayoutProps) => {
  const { t } = useTranslation();
  return (
    <div className="w-screen min-h-screen">
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
      <main
        className={clsx(
          "mt-8 w-full max-w-7xl mx-auto px-2 sm:px-6 lg:px-8",
          className,
        )}
      >
        {children}
      </main>
    </div>
  );
};

export default BackLayout;
