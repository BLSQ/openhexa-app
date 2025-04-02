import { ChevronLeftIcon, ChevronRightIcon } from "@heroicons/react/20/solid";
import clsx from "clsx";
import { useTranslation } from "next-i18next";
import Spinner from "../Spinner";
import PaginationItem from "./PaginationItem";

type Props = {
  loading?: boolean;
  page: number;
  hasNextPage: boolean;
  hasPreviousPage: boolean;
  className?: string;
  children?: React.ReactNode;
  onChange(page: number): void;
};

const SimplePagination = (props: Props) => {
  const {
    loading,
    page,
    onChange,
    className,
    hasNextPage,
    hasPreviousPage,
    children,
  } = props;

  const { t } = useTranslation();

  return (
    <div className={clsx("flex items-center justify-between py-3", className)}>
      <div className="flex flex-1 justify-between sm:hidden">
        {hasPreviousPage && (
          <PaginationItem onClick={() => onChange(page - 1)}>
            {t("Previous")}
          </PaginationItem>
        )}
        {hasNextPage && (
          <PaginationItem onClick={() => onChange(page + 1)}>
            {t("Next")}
          </PaginationItem>
        )}
      </div>
      <div
        className={clsx(
          "hidden sm:flex sm:flex-1 sm:items-center",
          loading || children ? "sm:justify-between" : "sm:justify-end",
        )}
      >
        {loading && (
          <div className="inline-flex items-center">
            <Spinner size="xs" className="mr-2" />
            {t("Loading...")}
          </div>
        )}
        {!loading && children}
        <div className="flex items-center space-x-2">
          <nav
            className="relative z-0 inline-flex -space-x-px rounded-md shadow-xs"
            aria-label="Pagination"
          >
            <PaginationItem
              onClick={() => onChange(page - 1)}
              disabled={!hasPreviousPage}
            >
              <span className="sr-only">{t("Previous")}</span>
              <ChevronLeftIcon className="h-5 w-5" aria-hidden="true" />
            </PaginationItem>

            <PaginationItem
              onClick={() => onChange(page + 1)}
              disabled={!hasNextPage}
            >
              <span className="sr-only">{t("Next")}</span>
              <ChevronRightIcon className="h-5 w-5" aria-hidden="true" />
            </PaginationItem>
          </nav>
        </div>
      </div>
    </div>
  );
};

export default SimplePagination;
