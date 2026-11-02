import React, {
  useCallback,
  useEffect,
  useMemo,
  useRef,
  useState,
} from "react";
import {
  ArrowUturnLeftIcon,
  CodeBracketIcon,
  EyeIcon,
} from "@heroicons/react/24/outline";
import { useTranslation } from "next-i18next";
import { DateTime } from "luxon";
import Link from "next/link";
import {
  useWebappVersionsQuery,
  WebappVersion_VersionFragment,
} from "webapps/graphql/queries.generated";
import Spinner from "core/components/Spinner";
import Badge from "core/components/Badge";
import Clipboard from "core/components/Clipboard";
import Button from "core/components/Button";
import Tooltip from "core/components/Tooltip";

const PER_PAGE = 20;

type WebappHistoryProps = {
  workspaceSlug: string;
  webappSlug: string;
  onSelectCommit?: (commitId: string) => void;
  onBrowseCommit?: (commitId: string) => void;
  onPreviewCommit?: (commitId: string) => void;
  // Brings an older version back as the new latest one and publishes it.
  onRollbackCommit?: (commitId: string) => void;
  canEdit?: boolean;
};

const ICON_BUTTON_CLASS =
  "rounded p-1 text-gray-400 hover:bg-gray-100 hover:text-gray-600 disabled:cursor-not-allowed disabled:opacity-50";

const WebappHistory = ({
  workspaceSlug,
  webappSlug,
  onSelectCommit,
  onBrowseCommit,
  onPreviewCommit,
  onRollbackCommit,
  canEdit = false,
}: WebappHistoryProps) => {
  const { t } = useTranslation();
  const [extraVersions, setExtraVersions] = useState<
    WebappVersion_VersionFragment[]
  >([]);
  const [hasMore, setHasMore] = useState(true);
  const [loadingMore, setLoadingMore] = useState(false);
  const pageRef = useRef(1);

  const { data, loading, fetchMore } = useWebappVersionsQuery({
    variables: { workspaceSlug, webappSlug, page: 1, perPage: PER_PAGE },
    fetchPolicy: "cache-and-network",
  });

  const firstPageVersions = useMemo(
    () => data?.webapp?.versions?.items ?? [],
    [data],
  );

  useEffect(() => {
    setExtraVersions([]);
    setHasMore(firstPageVersions.length >= PER_PAGE);
    pageRef.current = 1;
  }, [firstPageVersions]);

  const source = data?.webapp?.source;
  const publishedVersionId =
    source?.__typename === "GitSource" ? source.publishedVersion : null;
  const latestVersionId = firstPageVersions[0]?.id ?? null;

  const allVersions = useMemo(
    () => [...firstPageVersions, ...extraVersions],
    [firstPageVersions, extraVersions],
  );

  const groupedByDate = useMemo(() => {
    const groups: {
      date: string;
      versions: WebappVersion_VersionFragment[];
    }[] = [];
    const map = new Map<string, WebappVersion_VersionFragment[]>();

    for (const version of allVersions) {
      const dateKey = DateTime.fromISO(version.date).toLocaleString(
        DateTime.DATE_FULL,
      );
      if (!map.has(dateKey)) {
        const items: WebappVersion_VersionFragment[] = [];
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
    // fetchMore leaves the query on page 1, so a later refetch (after a save or
    // a roll back) reloads the first page instead of the last one loaded.
    fetchMore({
      variables: {
        workspaceSlug,
        webappSlug,
        page: nextPage,
        perPage: PER_PAGE,
      },
    }).then(({ data: d }) => {
      const items = d?.webapp?.versions?.items ?? [];
      setExtraVersions((prev) => [...prev, ...items]);
      setHasMore(items.length >= PER_PAGE);
      setLoadingMore(false);
    });
  }, [hasMore, loadingMore, fetchMore, workspaceSlug, webappSlug]);

  if (loading && !data) {
    return (
      <div className="flex items-center justify-center py-12">
        <Spinner size="sm" />
      </div>
    );
  }

  if (allVersions.length === 0) {
    return (
      <div className="py-12 text-center text-sm text-gray-500">
        {t("No commits yet. Edit files and save to get started.")}
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
              {t("Commits on {{date}}", { date })}
            </span>
            <div className="h-px flex-1 bg-gray-200" />
          </div>
          <div className="overflow-hidden rounded-md border border-gray-200">
            {versions.map((version, idx) => {
              const isPublished = version.id === publishedVersionId;
              const isLatest = version.id === latestVersionId;
              const dt = DateTime.fromISO(version.date);
              const diffSeconds = -dt.diffNow("seconds").seconds;
              const relative =
                diffSeconds < 60 ? t("Just now") : dt.toRelative();
              const shortId = version.id.substring(0, 7);
              return (
                <div
                  key={version.id}
                  data-testid={`webapp-version-${version.id}`}
                  className={`flex items-center justify-between gap-4 px-4 py-3 ${
                    idx < versions.length - 1 ? "border-b border-gray-200" : ""
                  }`}
                >
                  <div className="min-w-0 flex-1">
                    <div className="flex items-center gap-2">
                      {onSelectCommit ? (
                        <button
                          onClick={() => onSelectCommit(version.id)}
                          className="truncate text-left text-sm font-medium text-gray-900 hover:underline"
                        >
                          {version.message}
                        </button>
                      ) : (
                        <Link
                          href={`/workspaces/${encodeURIComponent(workspaceSlug)}/webapps/${encodeURIComponent(webappSlug)}/commits/${version.id}`}
                          className="truncate text-sm font-medium text-gray-900 hover:underline"
                        >
                          {version.message}
                        </Link>
                      )}
                      {isLatest && (
                        <Badge className="shrink-0 bg-blue-50 text-blue-700 ring-blue-600/20">
                          {t("Latest")}
                        </Badge>
                      )}
                      {isPublished && (
                        <Badge className="shrink-0 bg-green-50 text-green-700 ring-green-600/20">
                          {t("Published")}
                        </Badge>
                      )}
                    </div>
                    <div className="mt-0.5 text-xs text-gray-500">
                      {version.authorName} &middot; {relative}
                    </div>
                  </div>
                  <div className="flex shrink-0 items-center gap-2">
                    {onPreviewCommit && (
                      <Tooltip
                        label={t("Preview this version")}
                        renderTrigger={(ref) => (
                          <button
                            ref={ref as React.Ref<HTMLButtonElement>}
                            onClick={() => onPreviewCommit(version.id)}
                            aria-label={t("Preview this version")}
                            className={ICON_BUTTON_CLASS}
                          >
                            <EyeIcon className="h-4 w-4" />
                          </button>
                        )}
                      />
                    )}
                    <Tooltip
                      label={t("Browse at this point")}
                      renderTrigger={(ref) =>
                        onBrowseCommit ? (
                          <button
                            ref={ref as React.Ref<HTMLButtonElement>}
                            onClick={() => onBrowseCommit(version.id)}
                            aria-label={t("Browse at this point")}
                            className={ICON_BUTTON_CLASS}
                          >
                            <CodeBracketIcon className="h-4 w-4" />
                          </button>
                        ) : (
                          <Link
                            ref={ref as React.Ref<HTMLAnchorElement>}
                            href={`/workspaces/${encodeURIComponent(workspaceSlug)}/webapps/${encodeURIComponent(webappSlug)}/code?ref=${version.id}`}
                            aria-label={t("Browse at this point")}
                            className={ICON_BUTTON_CLASS}
                          >
                            <CodeBracketIcon className="h-4 w-4" />
                          </Link>
                        )
                      }
                    />
                    {onRollbackCommit && canEdit && !isLatest && (
                      <Tooltip
                        label={t("Roll back to this version")}
                        renderTrigger={(ref) => (
                          <button
                            ref={ref as React.Ref<HTMLButtonElement>}
                            onClick={() => onRollbackCommit(version.id)}
                            aria-label={t("Roll back to this version")}
                            className={ICON_BUTTON_CLASS}
                          >
                            <ArrowUturnLeftIcon className="h-4 w-4" />
                          </button>
                        )}
                      />
                    )}
                    <Clipboard value={version.id}>
                      <code className="rounded bg-gray-100 px-2 py-0.5 font-mono text-xs text-gray-600">
                        {shortId}
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

export default WebappHistory;
