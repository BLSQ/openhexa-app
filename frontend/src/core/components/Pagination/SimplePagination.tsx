import { ChevronLeftIcon, ChevronRightIcon } from "@heroicons/react/20/solid";
import clsx from "clsx";
import { useTranslation } from "next-i18next";
import Spinner from "../Spinner";
import SimpleSelect from "../forms/SimpleSelect";
import PaginationItem from "./PaginationItem";

type Props = {
  loading?: boolean;
  page: number;
  perPage?: number;
  perPageOptions?: number[];
  hasNextPage: boolean;
  hasPreviousPage: boolean;
  className?: string;
  children?: React.ReactNode;
  onChange(page: number, perPage?: number): void;
};

const SimplePagination = (props: Props) => {
  const {
    loading,
    page,
    perPage,
    perPageOptions,
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
          <PaginationItem onClick={() => onChange(page - 1, perPage)}>
            {t("Previous")}
          </PaginationItem>
        )}
        {hasNextPage && (
          <PaginationItem onClick={() => onChange(page + 1, perPage)}>
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
          {perPageOptions && perPage && (
            <SimpleSelect
              required
              onChange={(event) =>
                onChange(1, parseInt(event.currentTarget.value, 10))
              }
              className="h-[30px] w-fit py-0"
              value={perPage.toString()}
            >
              {perPageOptions.map((opt) => (
                <option key={opt} value={opt.toString()}>
                  {opt}
                </option>
              ))}
            </SimpleSelect>
          )}
          <nav
            className="relative z-0 inline-flex -space-x-px rounded-md shadow-xs"
            aria-label="Pagination"
          >
            <PaginationItem
              onClick={() => onChange(page - 1, perPage)}
              disabled={!hasPreviousPage}
            >
              <span className="sr-only">{t("Previous")}</span>
              <ChevronLeftIcon className="h-5 w-5" aria-hidden="true" />
            </PaginationItem>

            <PaginationItem
              onClick={() => onChange(page + 1, perPage)}
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
