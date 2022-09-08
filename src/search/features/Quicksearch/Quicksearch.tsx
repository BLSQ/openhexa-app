import { SearchIcon } from "@heroicons/react/outline";
import axios from "axios";
import clsx from "clsx";
import Dialog from "core/components/Dialog";
import Input from "core/components/forms/Input";
import Link from "core/components/Link";
import Spinner from "core/components/Spinner";
import useDebounce from "core/hooks/useDebounce";
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

  return [data, { isLoading }] as const;
}

const Quicksearch = (props: QuicksearchProps) => {
  const { open = false, onClose, renderActions } = props;
  const [queryString, setQueryString] = useState("");
  const { t } = useTranslation();
  const debouncedQueryString = useDebounce(queryString, 120);
  const [data, { isLoading }] = useQuicksearch(debouncedQueryString);

  useEffect(() => {
    if (!open) {
      setQueryString("");
    }
  }, [open]);

  return (
    <Dialog open={open} onClose={onClose} maxWidth="max-w-2xl">
      <Dialog.Content>
        <Input
          value={queryString}
          onChange={(e) => setQueryString(e.target.value)}
          trailingIcon={
            isLoading ? <Spinner size="xs" /> : <SearchIcon className="h-4" />
          }
          placeholder={t("Search for elements...")}
        />

        <>
          <span
            className={clsx(
              "text-sm text-gray-500 transition-all",
              !data.length && "invisible"
            )}
          >
            {t("Showing top 10 results")}
          </span>
          <div className="mt-4">
            <div className="-mx-6 h-52 overflow-y-auto">
              {data.length === 0 && (
                <div className="mt-4 w-full text-center text-sm italic text-gray-500">
                  {queryString
                    ? t("No results to display")
                    : t("Type what you are looking for here above")}
                </div>
              )}
              {data.map((result) => (
                <div
                  className="flex items-center gap-3 py-2.5 px-7 text-sm hover:bg-gray-50"
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
          </div>
        </>
      </Dialog.Content>
    </Dialog>
  );
};

export default Quicksearch;
