import React, {
  useCallback,
  useEffect,
  useMemo,
  useRef,
  useState,
} from "react";
import { CodeBracketIcon } from "@heroicons/react/24/outline";
import { useTranslation } from "next-i18next";
import { DateTime } from "luxon";
import Spinner from "core/components/Spinner";
import Clipboard from "core/components/Clipboard";
import Button from "core/components/Button";
import Tooltip from "core/components/Tooltip";
import {
  SavedQueryVersion_VersionFragment,
  useSavedQueryVersionsQuery,
} from "./SavedQueryDetail.generated";

const PER_PAGE = 20;

type SavedQueryHistoryProps = {
  slug: string;
  onSelectVersion: (versionId: string) => void;
  onBrowseVersion: (versionId: string) => void;
};

// The versions of a saved query, newest first and grouped by day. Mirrors the
// web app history: a version is a commit of the query's repository.
const SavedQueryHistory = ({
  slug,
  onSelectVersion,
  onBrowseVersion,
}: SavedQueryHistoryProps) => {
  const { t } = useTranslation();
  const [extraVersions, setExtraVersions] = useState<
    SavedQueryVersion_VersionFragment[]
  >([]);
  const [hasMore, setHasMore] = useState(true);
  const [loadingMore, setLoadingMore] = useState(false);
  const pageRef = useRef(1);

  const { data, loading, refetch } = useSavedQueryVersionsQuery({
    variables: { slug, page: 1, perPage: PER_PAGE },
    fetchPolicy: "cache-and-network",
    nextFetchPolicy: "cache-first",
  });

  const firstPageVersions = useMemo(
    () => data?.savedQueryBySlug?.versions?.items ?? [],
    [data],
  );

  useEffect(() => {
    setExtraVersions([]);
    setHasMore(firstPageVersions.length >= PER_PAGE);
    pageRef.current = 1;
  }, [firstPageVersions]);

  const allVersions = useMemo(
    () => [...firstPageVersions, ...extraVersions],
    [firstPageVersions, extraVersions],
  );

  const groupedByDate = useMemo(() => {
    const groups: {
      date: string;
      versions: SavedQueryVersion_VersionFragment[];
    }[] = [];
    const map = new Map<string, SavedQueryVersion_VersionFragment[]>();

    for (const version of allVersions) {
      const dateKey = DateTime.fromISO(version.date).toLocaleString(
        DateTime.DATE_FULL,
      );
      if (!map.has(dateKey)) {
        const items: SavedQueryVersion_VersionFragment[] = [];
        map.set(dateKey, items);
        groups.push({ date: dateKey, versions: items });
      }
      map.get(dateKey)!.push(version);
    }
    return groups;
  }, [allVersions]);

  const handleLoadMore = useCallback(() => {
    if (!hasMore || loadingMore) return;
    setLoadingMore(true);
    const nextPage = pageRef.current + 1;
    pageRef.current = nextPage;
    refetch({ slug, page: nextPage, perPage: PER_PAGE }).then(({ data: d }) => {
      const items = d?.savedQueryBySlug?.versions?.items ?? [];
      setExtraVersions((prev) => [...prev, ...items]);
      setHasMore(items.length >= PER_PAGE);
      setLoadingMore(false);
    });
  }, [hasMore, loadingMore, refetch, slug]);

  if (loading && allVersions.length === 0) {
    return (
      <div className="flex items-center justify-center py-12">
        <Spinner size="sm" />
      </div>
    );
  }

  if (allVersions.length === 0) {
    return (
      <div className="py-12 text-center text-sm text-gray-500">
        {t("No versions yet. Save a change to the query to record one.")}
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {groupedByDate.map(({ date, versions }) => (
        <div key={date}>
          <div className="mb-2 flex items-center gap-3">
            <div className="h-px flex-1 bg-gray-200" />
            <span className="text-xs font-semibold uppercase tracking-wide text-gray-500">
              {t("Versions on {{date}}", { date })}
            </span>
            <div className="h-px flex-1 bg-gray-200" />
          </div>
          <div className="overflow-hidden rounded-md border border-gray-200">
            {versions.map((version, idx) => {
              const dt = DateTime.fromISO(version.date);
              const diffSeconds = -dt.diffNow("seconds").seconds;
              const relative =
                diffSeconds < 60 ? t("Just now") : dt.toRelative();
              const isLatest = version.id === allVersions[0]?.id;
              return (
                <div
                  key={version.id}
                  className={`flex items-center justify-between gap-4 px-4 py-3 ${
                    idx < versions.length - 1 ? "border-b border-gray-200" : ""
                  }`}
                >
                  <div className="min-w-0 flex-1">
                    <div className="flex items-center gap-2">
                      <button
                        onClick={() => onSelectVersion(version.id)}
                        className="truncate text-left text-sm font-medium text-gray-900 hover:underline"
                      >
                        {version.message}
                      </button>
                      {isLatest && (
                        <span className="shrink-0 rounded bg-green-50 px-1.5 py-0.5 text-[11px] font-medium text-green-700 ring-1 ring-green-600/20">
                          {t("Latest")}
                        </span>
                      )}
                    </div>
                    <div className="mt-0.5 text-xs text-gray-500">
                      {version.authorName} &middot; {relative}
                    </div>
                  </div>
                  <div className="flex shrink-0 items-center gap-2">
                    <Tooltip
                      label={t("Open this version in the editor")}
                      renderTrigger={(ref) => (
                        <button
                          ref={ref as React.Ref<HTMLButtonElement>}
                          onClick={() => onBrowseVersion(version.id)}
                          className="rounded p-1 text-gray-400 hover:bg-gray-100 hover:text-gray-600"
                        >
                          <CodeBracketIcon className="h-4 w-4" />
                        </button>
                      )}
                    />
                    <Clipboard value={version.id}>
                      <code className="rounded bg-gray-100 px-2 py-0.5 font-mono text-xs text-gray-600">
                        {version.id.substring(0, 7)}
                      </code>
                    </Clipboard>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      ))}
      {hasMore && (
        <div className="flex justify-center pt-2">
          <Button
            variant="secondary"
            onClick={handleLoadMore}
            disabled={loadingMore}
          >
            {loadingMore ? <Spinner size="xs" /> : t("Load more")}
          </Button>
        </div>
      )}
    </div>
  );
};

export default SavedQueryHistory;
