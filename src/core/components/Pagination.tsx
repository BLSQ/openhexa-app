import { ChevronLeftIcon, ChevronRightIcon } from "@heroicons/react/solid";
import clsx from "clsx";
import { useTranslation } from "next-i18next";
import { ReactElement } from "react";
import SimpleSelect from "core/components/forms/SimpleSelect";
import Spinner from "./Spinner";

type Props = {
  loading?: boolean;
  page: number;
  perPage: number;
  perPageOptions?: number[];
  totalPages?: number;
  countItems: number;
  totalItems: number;
  className?: string;
  onChange: (page: number, perPage: number) => void;
};

const PaginationItem = (props: {
  children: ReactElement | string | ReactElement[];
  current?: boolean;
  disabled?: boolean;
  onClick?: () => void;
}) => {
  const { children, current, onClick, disabled = false } = props;
  return (
    <button
      onClick={onClick}
      aria-current="page"
      type="button"
      disabled={disabled}
      className={clsx(
        "relative inline-flex cursor-pointer items-center border border-gray-300 bg-white px-3 py-1 text-sm font-medium text-gray-500 hover:bg-gray-50 disabled:cursor-not-allowed disabled:opacity-50",
        current && "border-who-blue-main text-who-blue-main z-10 bg-indigo-50",
        "first:rounded-tl-md first:rounded-bl-md last:rounded-tr-md last:rounded-br-md"
      )}
    >
      {children}
    </button>
  );
};

const Pagination = (props: Props) => {
  const {
    loading,
    page,
    perPage,
    perPageOptions,
    countItems,
    totalItems,
    onChange,
    className,
  } = props;

  const { t } = useTranslation();
  const start = (page - 1) * perPage + 1;
  const end = (page - 1) * perPage + countItems;
  const totalPages = props.totalPages ?? Math.ceil(totalItems / perPage);

  if (totalPages < 2) {
    return null;
  }

  return (
    <div className={clsx("flex items-center justify-between py-3", className)}>
      <div className="flex flex-1 justify-between sm:hidden">
        {page > 1 && (
          <PaginationItem onClick={() => onChange(page - 1, perPage)}>
            {t("Previous")}
          </PaginationItem>
        )}
        {page < totalPages && (
          <PaginationItem onClick={() => onChange(page + 1, perPage)}>
            {t("Next")}
          </PaginationItem>
        )}
      </div>
      <div className="hidden sm:flex sm:flex-1 sm:items-center sm:justify-between">
        {loading && (
          <div className="inline-flex items-center">
            <Spinner size="xs" className="mr-2" />
            {t("Loading...")}
          </div>
        )}
        {!loading && totalPages > 1 && (
          <div>
            <p className="text-sm text-gray-700">
              {t(
                "Showing {{ start }} to {{ end }} of {{ totalItems }} results",
                {
                  totalItems,
                  start,
                  end,
                }
              )}
            </p>
          </div>
        )}
        {!loading && totalPages <= 1 && <div></div>}
        <div className="flex items-center space-x-2">
          {perPageOptions && (
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
          {totalPages > 1 && (
            <nav
              className="relative z-0 inline-flex -space-x-px rounded-md shadow-sm"
              aria-label="Pagination"
            >
              <PaginationItem
                onClick={() => onChange(page - 1, perPage)}
                disabled={page === 1}
              >
                <span className="sr-only">{t("Previous")}</span>
                <ChevronLeftIcon className="h-5 w-5" aria-hidden="true" />
              </PaginationItem>

              <PaginationItem
                onClick={() => onChange(page + 1, perPage)}
                disabled={page === totalPages}
              >
                <span className="sr-only">{t("Next")}</span>
                <ChevronRightIcon className="h-5 w-5" aria-hidden="true" />
              </PaginationItem>
            </nav>
          )}
        </div>
      </div>
    </div>
  );
};

export default Pagination;
