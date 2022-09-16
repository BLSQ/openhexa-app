import { ArrowRightIcon, SearchIcon } from "@heroicons/react/outline";
import axios from "axios";
import clsx from "clsx";
import Dialog from "core/components/Dialog";
import Input from "core/components/forms/Input";
import Link from "core/components/Link";
import Spinner from "core/components/Spinner";
import useDebounce from "core/hooks/useDebounce";
import usePrevious from "core/hooks/usePrevious";
import { useTranslation } from "next-i18next";
import { ReactElement, useEffect, useState } from "react";

export type QuickSearchResult = {
  id: string;
  object_id: string;
  app_label: string;
  display_name: string;
  content_type_model: string;
  content_type_name: string;
  datasource_name: string;
  datasource_id: string;
  description: string;
  rank: number;
  url: string;
  symbol: string;
};
type QuicksearchProps = {
  open?: boolean;
  onClose(): void;
  renderActions?: (element: QuickSearchResult) => ReactElement;
};

function useQuicksearch(query: string) {
  const [isLoading, setLoading] = useState(false);
  const [data, setData] = useState<QuickSearchResult[]>([]);
  const prevData = usePrevious(data);

  async function fetchResults(query: string) {
    setLoading(true);
    try {
      const response = await axios.get("/catalog/quick-search/", {
        params: { query },
      });
      setData(response.data.results);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    if (!query && data) {
      setData([]);
    }
    if (query) {
      fetchResults(query);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [query]);

  return [data, { isLoading, prevData }] as const;
}

const Quicksearch = (props: QuicksearchProps) => {
  const { open = false, onClose, renderActions } = props;
  const [queryString, setQueryString] = useState("");
  const { t } = useTranslation();
  const debouncedQueryString = useDebounce(queryString, 120);
  const [data, { isLoading, prevData }] = useQuicksearch(debouncedQueryString);

  useEffect(() => {
    if (!open) {
      setQueryString("");
    }
  }, [open]);

  const items = data ?? prevData;

  return (
    <Dialog
      open={open}
      onClose={onClose}
      maxWidth="max-w-2xl"
      centered={false}
      padding="py-2"
    >
      <Dialog.Content className="space-y-2 divide-y divide-gray-100">
        <div className="flex items-center px-4">
          <SearchIcon className="h-5 text-gray-500" />
          <div className="flex-1">
            <Input
              trailingIcon={isLoading && <Spinner size="xs" />}
              className="text-md border-0 outline-none focus:ring-0"
              placeholder={t("Search...")}
              value={queryString}
              onChange={(e) => setQueryString(e.target.value)}
            />
          </div>
        </div>
        {data.length === 0 && queryString && (
          <div className="p-4 text-sm text-gray-500">
            {t("No results to display.")}
          </div>
        )}
        {items?.length > 0 && (
          <div className="overflow-y-auto">
            {items.map((result) => (
              <div
                className="flex items-center gap-3 py-2.5 px-4 text-sm hover:bg-gray-50"
                key={result.id}
              >
                {result.symbol && (
                  <div className="w-5">
                    <img
                      className="h-5 w-5 flex-shrink-0"
                      src={result.symbol}
                      alt={result.display_name}
                    />
                  </div>
                )}
                <div className="flex-1 truncate">
                  <Link className="font-medium" href={result.url}>
                    {result.display_name}
                  </Link>
                  <span className="ml-2 font-sans text-xs text-gray-300">
                    #{Math.round(result.rank * 100) / 100}
                  </span>
                  <div className="mt-1 text-xs text-gray-500">
                    {result.content_type_name}{" "}
                    {result.datasource_name && `/ ${result.datasource_name}`}
                  </div>
                </div>
                {renderActions && renderActions(result)}
              </div>
            ))}
          </div>
        )}
        {(items.length > 0 || queryString) && (
          <div className="flex justify-between px-4 pt-3 pb-1 text-xs text-gray-500 transition-all">
            <span>{items.length > 0 && t("Showing top 10 results")}</span>
            <Link
              href={{
                pathname: "/catalog/search",
                query: { query: queryString },
              }}
              className="flex items-center gap-1"
            >
              {t("Go to advanced search")}
              <ArrowRightIcon className="w-3" />
            </Link>
          </div>
        )}
      </Dialog.Content>
    </Dialog>
  );
};

export default Quicksearch;
