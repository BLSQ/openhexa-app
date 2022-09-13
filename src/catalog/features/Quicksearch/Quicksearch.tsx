import { ArrowRightIcon } from "@heroicons/react/24/outline";
import useSearch from "catalog/hooks/useSearch";
import Dialog from "core/components/Dialog";
import Link from "core/components/Link";
import useDebounce from "core/hooks/useDebounce";
import { useTranslation } from "next-i18next";
import { useRouter } from "next/router";
import { useEffect, useState } from "react";
import SearchInput from "../SearchInput";
import SearchResult, { SearchResultProps } from "../SearchResult";

type QuicksearchProps = {
  open?: boolean;
  onClose(): void;
} & Pick<SearchResultProps, "renderActions">;

const Quicksearch = (props: QuicksearchProps) => {
  const { open = false, onClose, renderActions } = props;
  const [queryString, setQueryString] = useState("");
  const { t } = useTranslation();
  const router = useRouter();
  const debouncedQueryString = useDebounce(queryString, 120);

  const { results, loading } = useSearch({
    query: debouncedQueryString,
    perPage: 10,
    skip: !open,
  });

  useEffect(() => {
    if (open) {
      onClose();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [router.pathname, open]);

  useEffect(() => {
    if (!open) {
      setQueryString("");
    }
  }, [open]);

  return (
    <Dialog
      open={open}
      onClose={onClose}
      maxWidth="max-w-2xl"
      centered={false}
      padding="py-2"
    >
      <Dialog.Content className="space-y-2 divide-y divide-gray-100">
        <SearchInput
          value={queryString}
          loading={loading}
          className="border-none px-4 outline-none focus:ring-0"
          onChange={(e) => setQueryString(e.target.value)}
        />
        {results?.length === 0 && queryString && (
          <div className="p-4 text-sm text-gray-500">
            {t("No results to display.")}
          </div>
        )}

        {results && results.length !== 0 && (
          <div className="overflow-y-auto">
            {results.map((result) => (
              <SearchResult
                key={result.object.id}
                result={result}
                renderActions={renderActions}
              />
            ))}
          </div>
        )}

        <div className="flex justify-between px-4 pt-3 pb-1 text-xs text-gray-500 transition-all">
          {results && (
            <span>{results.length > 0 && t("Showing top 10 results")}</span>
          )}
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
      </Dialog.Content>
    </Dialog>
  );
};

export default Quicksearch;
