import { useTranslation } from "next-i18next";
import {
  useWebappVersionsQuery,
  WebappVersion_VersionFragment,
} from "webapps/graphql/queries.generated";
import Spinner from "core/components/Spinner";
import Button from "core/components/Button";
import { DateTime } from "luxon";
import { useState, useCallback, useRef } from "react";
import { ChevronRightIcon } from "@heroicons/react/24/outline";
import clsx from "clsx";
import Link from "next/link";

const PER_PAGE = 30;

type CommitRowProps = {
  version: WebappVersion_VersionFragment;
  publishedVersionId: string | null;
  workspaceSlug: string;
  webappSlug: string;
};

const CommitRow = ({
  version,
  publishedVersionId,
  workspaceSlug,
  webappSlug,
}: CommitRowProps) => {
  const { t } = useTranslation();
  const [expanded, setExpanded] = useState(false);
  const isPublished = version.id === publishedVersionId;
  const shortId = version.id.substring(0, 7);
  const dt = DateTime.fromISO(version.date);
  const diffSeconds = -dt.diffNow("seconds").seconds;
  const relativeDate = diffSeconds < 60 ? t("Just now") : dt.toRelative();
  const codeHref = `/workspaces/${encodeURIComponent(workspaceSlug)}/webapps/${encodeURIComponent(webappSlug)}/code?ref=${version.id}`;

  return (
    <div className="border-b border-gray-100 last:border-0">
      <div className="flex w-full items-center gap-3 px-4 py-3 transition-colors hover:bg-gray-50">
        <button
          className="shrink-0"
          onClick={() => setExpanded((v) => !v)}
          aria-label={expanded ? t("Collapse") : t("Expand")}
        >
          <ChevronRightIcon
            className={clsx(
              "h-4 w-4 text-gray-400 transition-transform",
              expanded && "rotate-90",
            )}
          />
        </button>
        <div className="min-w-0 flex-1">
          <div className="flex flex-wrap items-center gap-2">
            <code className="rounded bg-gray-100 px-1.5 py-0.5 font-mono text-xs text-gray-600">
              {shortId}
            </code>
            <Link
              href={codeHref}
              className="truncate text-sm font-medium text-gray-900 hover:underline"
            >
              {version.message}
            </Link>
            {isPublished && (
              <span className="inline-flex shrink-0 items-center rounded-full bg-green-100 px-2 py-0.5 text-xs font-medium text-green-700">
                {t("Published")}
              </span>
            )}
          </div>
          <div className="mt-0.5 text-xs text-gray-500">
            {version.authorName} &middot; {relativeDate}
          </div>
        </div>
      </div>
      {expanded && (
        <div className="border-t border-gray-100 bg-gray-50 px-4 py-3 pl-11">
          <dl className="grid grid-cols-[auto_1fr] gap-x-4 gap-y-1 text-sm">
            <dt className="font-medium text-gray-500">{t("Full hash")}</dt>
            <dd>
              <code className="font-mono text-xs text-gray-700">
                {version.id}
              </code>
            </dd>
            <dt className="font-medium text-gray-500">{t("Author")}</dt>
            <dd className="text-gray-700">
              {version.authorName}{" "}
              <span className="text-gray-500">&lt;{version.authorEmail}&gt;</span>
            </dd>
            <dt className="font-medium text-gray-500">{t("Date")}</dt>
            <dd className="text-gray-700">
              {dt.toLocaleString(DateTime.DATETIME_FULL)}
            </dd>
            {version.message && (
              <>
                <dt className="font-medium text-gray-500">{t("Message")}</dt>
                <dd className="whitespace-pre-wrap text-gray-700">
                  {version.message}
                </dd>
              </>
            )}
          </dl>
        </div>
      )}
    </div>
  );
};

type WebappHistoryProps = {
  workspaceSlug: string;
  webappSlug: string;
};

const WebappHistory = ({ workspaceSlug, webappSlug }: WebappHistoryProps) => {
  const { t } = useTranslation();
  const [extraVersions, setExtraVersions] = useState<
    WebappVersion_VersionFragment[]
  >([]);
  const [hasMore, setHasMore] = useState(true);
  const pageRef = useRef(1);

  const { data, loading, refetch } = useWebappVersionsQuery({
    variables: { workspaceSlug, webappSlug, page: 1, perPage: PER_PAGE },
  });

  const firstPageVersions = data?.webapp?.versions?.items ?? [];
  const allVersions = [...firstPageVersions, ...extraVersions];
  const source = data?.webapp?.source;
  const publishedVersionId =
    source?.__typename === "GitSource" ? source.publishedVersion : null;

  const handleLoadMore = useCallback(() => {
    const nextPage = pageRef.current + 1;
    pageRef.current = nextPage;
    refetch({ workspaceSlug, webappSlug, page: nextPage, perPage: PER_PAGE }).then(
      ({ data: d }) => {
        const items = d?.webapp?.versions?.items ?? [];
        setExtraVersions((prev) => [...prev, ...items]);
        setHasMore(items.length >= PER_PAGE);
      },
    );
  }, [refetch, workspaceSlug, webappSlug]);

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
        {t("No history yet. Edit files and save to get started.")}
      </div>
    );
  }

  const grouped = allVersions.reduce<
    { date: string; versions: WebappVersion_VersionFragment[] }[]
  >((acc, version) => {
    const dateKey = DateTime.fromISO(version.date).toFormat("yyyy-MM-dd");
    const existing = acc.find((g) => g.date === dateKey);
    if (existing) {
      existing.versions.push(version);
    } else {
      acc.push({ date: dateKey, versions: [version] });
    }
    return acc;
  }, []);

  return (
    <div className="space-y-6">
      {grouped.map(({ date, versions }) => (
        <div key={date}>
          <div className="mb-2 flex items-center gap-2 pl-4">
            <h3 className="text-sm font-normal text-gray-400">
              {t("Commits on")}{" "}
              {DateTime.fromISO(date).toLocaleString(DateTime.DATE_FULL)}
            </h3>
            <div className="h-px flex-1 bg-gray-200" />
          </div>
          <div className="overflow-hidden rounded-md border border-gray-200 bg-white shadow-sm">
            {versions.map((version) => (
              <CommitRow
                key={version.id}
                version={version}
                publishedVersionId={publishedVersionId ?? null}
                workspaceSlug={workspaceSlug}
                webappSlug={webappSlug}
              />
            ))}
          </div>
        </div>
      ))}
      {hasMore && firstPageVersions.length >= PER_PAGE && (
        <div className="flex justify-center">
          <Button variant="outlined" onClick={handleLoadMore}>
            {t("Load more")}
          </Button>
        </div>
      )}
    </div>
  );
};

export default WebappHistory;
