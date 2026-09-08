import { CodeBracketIcon } from "@heroicons/react/24/outline";
import Badge from "core/components/Badge";
import Button from "core/components/Button";
import Spinner from "core/components/Spinner";
import Tooltip from "core/components/Tooltip";
import { DateTime } from "luxon";
import { useTranslation } from "next-i18next";
import { useWorkspacePipelineHistoryQuery } from "workspaces/graphql/queries.generated";
import { WorkspacePipelineHistoryQuery } from "workspaces/graphql/queries.generated";
import React, {
  useCallback,
  useEffect,
  useMemo,
  useRef,
  useState,
} from "react";

const PER_PAGE = 20;

type PipelineVersion = NonNullable<
  WorkspacePipelineHistoryQuery["pipeline"]
>["versions"]["items"][number];

type PipelineHistoryProps = {
  workspaceSlug: string;
  pipelineCode: string;
  onSelectVersion: (version: PipelineVersion) => void;
  onBrowseVersion: (versionId: string) => void;
};

const PipelineHistory = ({
  workspaceSlug,
  pipelineCode,
  onSelectVersion,
  onBrowseVersion,
}: PipelineHistoryProps) => {
  const { t } = useTranslation();
  const [extraVersions, setExtraVersions] = useState<PipelineVersion[]>([]);
  const [hasMore, setHasMore] = useState(true);
  const [loadingMore, setLoadingMore] = useState(false);
  const pageRef = useRef(1);

  const { data, loading, refetch } = useWorkspacePipelineHistoryQuery({
    variables: { workspaceSlug, pipelineCode, page: 1, perPage: PER_PAGE },
  });

  const firstPageVersions = useMemo(
    () => data?.pipeline?.versions?.items ?? [],
    [data],
  );

  useEffect(() => {
    setExtraVersions([]);
    setHasMore(firstPageVersions.length >= PER_PAGE);
    pageRef.current = 1;
  }, [firstPageVersions]);

  const scheduledVersionId = data?.pipeline?.scheduledPipelineVersion?.id;

  const allVersions = useMemo(
    () => [...firstPageVersions, ...extraVersions],
    [firstPageVersions, extraVersions],
  );

  const groupedByDate = useMemo(() => {
    const groups: { date: string; versions: PipelineVersion[] }[] = [];
    const map = new Map<string, PipelineVersion[]>();

    for (const version of allVersions) {
      const dateKey = DateTime.fromISO(version.createdAt).toLocaleString(
        DateTime.DATE_FULL,
      );
      if (!map.has(dateKey)) {
        const items: PipelineVersion[] = [];
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
    refetch({
      workspaceSlug,
      pipelineCode,
      page: nextPage,
      perPage: PER_PAGE,
    }).then(({ data: d }) => {
      const items = d?.pipeline?.versions?.items ?? [];
      setExtraVersions((prev) => [...prev, ...items]);
      setHasMore(items.length >= PER_PAGE);
      setLoadingMore(false);
    });
  }, [hasMore, loadingMore, refetch, workspaceSlug, pipelineCode]);

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <Spinner size="sm" />
      </div>
    );
  }

  if (allVersions.length === 0) {
    return (
      <div className="py-12 text-center text-sm text-gray-500">
        {t("No version yet. Edit the code and save to create one.")}
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
              {t("Versions created on {{date}}", { date })}
            </span>
            <div className="h-px flex-1 bg-gray-200" />
          </div>
          <div className="overflow-hidden rounded-md border border-gray-200">
            {versions.map((version, idx) => {
              const dt = DateTime.fromISO(version.createdAt);
              const diffSeconds = -dt.diffNow("seconds").seconds;
              const relative =
                diffSeconds < 60 ? t("Just now") : dt.toRelative();
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
                        onClick={() => onSelectVersion(version)}
                        className="truncate text-left text-sm font-medium text-gray-900 hover:underline"
                      >
                        {version.name || version.versionName}
                      </button>
                      {version.isLatestVersion && (
                        <Badge className="shrink-0 bg-green-50 text-green-700 ring-green-600/20">
                          {t("Latest")}
                        </Badge>
                      )}
                      {version.id === scheduledVersionId && (
                        <Badge className="shrink-0 bg-blue-50 text-blue-700 ring-blue-600/20">
                          {t("Scheduled")}
                        </Badge>
                      )}
                    </div>
                    <div className="mt-0.5 text-xs text-gray-500">
                      {version.user?.displayName ?? t("someone")} &middot;{" "}
                      {relative}
                    </div>
                  </div>
                  <div className="flex shrink-0 items-center gap-2">
                    <Tooltip
                      label={t("Browse the code at this version")}
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
                    <code className="rounded bg-gray-100 px-2 py-0.5 font-mono text-xs text-gray-600">
                      {version.versionName}
                    </code>
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

export default PipelineHistory;
