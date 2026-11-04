import {
  ArrowTopRightOnSquareIcon,
  ArrowUturnLeftIcon,
  ClockIcon,
  CodeBracketIcon,
  Cog6ToothIcon,
  EyeIcon,
  GlobeAltIcon,
  LockClosedIcon,
  SparklesIcon,
  TrashIcon,
} from "@heroicons/react/24/outline";
import WebappEditChatPanel, {
  WebappConversation,
} from "assistant/features/WebappEditChatPanel";
import Button from "core/components/Button";
import DetailShell, {
  AssistantDock,
  BrowsingVersionBanner,
  DetailBadge,
  DetailHeader,
  DetailViewPane,
  Segment,
  SegmentedViewSwitcher,
  SettingsCard,
  useAssistantDock,
} from "core/components/DetailShell";
import Spinner from "core/components/Spinner";
import { resizeImage } from "core/helpers/image";
import { isRequestTooLargeError } from "core/helpers/errors";
import useCacheKey from "core/hooks/useCacheKey";
import { WebappType } from "graphql/types";
import { Trans, useTranslation } from "next-i18next";
import {
  ChangeEvent,
  useCallback,
  useEffect,
  useMemo,
  useRef,
  useState,
} from "react";
import { toast } from "react-toastify";
import { useApolloClient } from "@apollo/client";
import { useUpdateWebappMutation } from "webapps/graphql/mutations.generated";
import {
  useWebappPreviewUrlQuery,
  useWebappVersionsQuery,
} from "webapps/graphql/queries.generated";
import CommitDiff from "webapps/features/CommitDiff/CommitDiff";
import WebappApiAccess from "webapps/features/WebappApiAccess";
import WebappFilesEditor from "webapps/features/WebappFilesEditor/WebappFilesEditor";
import WebappHistory from "webapps/features/WebappHistory/WebappHistory";
import RestoreWebappVersionDialog from "webapps/features/RestoreWebappVersionDialog/RestoreWebappVersionDialog";
import WebappIframe from "webapps/features/WebappIframe";
import { getWebappTypeLabel } from "webapps/helpers";

const PLACEHOLDER_ICON = "/images/placeholder.svg";
const ASSISTANT_STORAGE_KEY = "webapp-assistant";

type View = "preview" | "code" | "history" | "settings";

type WebappDetailProps = {
  workspaceSlug: string;
  webappSlug: string;
  webapp: any;
  showAssistant: boolean;
  onRefetch: () => void;
  onDelete?: () => void;
};

const splitServeUrl = (serveUrl?: string | null, subdomain?: string | null) => {
  if (!serveUrl || !subdomain) return null;
  try {
    const url = new URL(serveUrl);
    return {
      prefix: `${url.protocol}//`,
      suffix: url.host.substring(subdomain.length),
    };
  } catch {
    return null;
  }
};

const WebappDetail = ({
  workspaceSlug,
  webappSlug,
  webapp,
  showAssistant,
  onRefetch,
  onDelete,
}: WebappDetailProps) => {
  const { t } = useTranslation();
  const isStatic = webapp.type === WebappType.Static;
  const canEdit = Boolean(webapp.permissions?.update);

  const [view, setView] = useState<View>("preview");
  const [isSaving, setIsSaving] = useState(false);
  const [versionRef, setVersionRef] = useState<string | null>(null);
  const [diffCommitId, setDiffCommitId] = useState<string | null>(null);
  const [isPublishing, setIsPublishing] = useState(false);
  const [restoreTarget, setRestoreTarget] = useState<string | null>(null);

  const [name, setName] = useState<string>(webapp.name ?? "");
  const [subdomain, setSubdomain] = useState<string>(webapp.subdomain ?? "");
  const [sourceUrl, setSourceUrl] = useState<string>(webapp.url ?? "");
  const [icon, setIcon] = useState<string | null>(webapp.icon ?? null);

  const client = useApolloClient();
  const [updateWebapp] = useUpdateWebappMutation();
  const clearCache = useCacheKey("webapps");

  useEffect(() => {
    setName(webapp.name ?? "");
    setSubdomain(webapp.subdomain ?? "");
    setSourceUrl(webapp.url ?? "");
    setIcon(webapp.icon ?? null);
  }, [webapp]);

  const { data: versionsData } = useWebappVersionsQuery({
    variables: { workspaceSlug, webappSlug, page: 1, perPage: 1 },
    skip: !isStatic,
    fetchPolicy: "cache-and-network",
  });
  const latestVersion = versionsData?.webapp?.versions?.items?.[0];
  const latestVersionId: string | null = latestVersion?.id ?? null;
  const publishedVersionId: string | null =
    versionsData?.webapp?.source?.__typename === "GitSource"
      ? versionsData.webapp.source.publishedVersion
      : webapp.source?.__typename === "GitSource"
        ? webapp.source.publishedVersion
        : null;
  const isLiveLatest =
    latestVersionId !== null && latestVersionId === publishedVersionId;

  // The preview renders the browsed version, or the latest one by default. The
  // ref lives in the preview session on the backend, so the URL itself does not
  // change: the iframe is keyed on the ref to reload when it does, and it is
  // only mounted once the query storing the ref has resolved, otherwise the
  // iframe would fetch the previous ref from the session.
  const previewRef = versionRef ?? latestVersionId;
  const { data: previewData, loading: previewLoading } =
    useWebappPreviewUrlQuery({
      variables: { workspaceSlug, webappSlug, ref: previewRef },
      skip: !isStatic || !previewRef,
      fetchPolicy: "network-only",
    });
  const previewReady = !isStatic || !previewRef || !previewLoading;

  const browseCommit = useCallback((commitId: string) => {
    setDiffCommitId(null);
    setVersionRef(commitId);
    setView("code");
  }, []);

  const previewCommit = useCallback((commitId: string) => {
    setDiffCommitId(null);
    setVersionRef(commitId);
    setView("preview");
  }, []);

  // Reloads the webapp and every mounted versions list: the header pill, the
  // History tab and the version picker all observe the same query under
  // different variables, so they are refetched by name rather than one by one.
  const refreshVersions = useCallback(() => {
    onRefetch();
    client.refetchQueries({ include: ["WebappVersions"] }).then();
  }, [onRefetch, client]);

  const handlePublishLatest = async () => {
    if (!latestVersionId || isPublishing) return;
    setIsPublishing(true);
    try {
      const { data } = await updateWebapp({
        variables: {
          input: { id: webapp.id, publishedVersionId: latestVersionId },
        },
      });
      if (data?.updateWebapp?.success) {
        toast.success(t("Version is now live"));
        refreshVersions();
      } else {
        toast.error(t("Failed to put the version live"));
      }
    } catch {
      toast.error(t("Failed to put the version live"));
    } finally {
      setIsPublishing(false);
    }
  };

  // The restored version shows up as the latest one, so the preview and the
  // editor follow it again.
  const handleRestored = useCallback(() => {
    setVersionRef(null);
    setDiffCommitId(null);
    refreshVersions();
  }, [refreshVersions]);

  const urlParts = useMemo(
    () => splitServeUrl(webapp.serveUrl, webapp.subdomain),
    [webapp.serveUrl, webapp.subdomain],
  );

  const displayUrl = useMemo(() => {
    const raw = webapp.serveUrl || webapp.url;
    if (!raw) return null;
    try {
      const url = new URL(raw);
      return `${url.host}${url.pathname === "/" ? "" : url.pathname}`;
    } catch {
      return raw;
    }
  }, [webapp.serveUrl, webapp.url]);

  const handleIconChange = async (event: ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      setIcon(await resizeImage(file, 64, 64));
    }
  };

  const handleSave = async () => {
    setIsSaving(true);
    try {
      const { data } = await updateWebapp({
        variables: {
          input: {
            id: webapp.id,
            name,
            icon,
            ...(isStatic && subdomain ? { subdomain } : {}),
            ...(webapp.type === WebappType.Iframe
              ? { source: { iframe: { url: sourceUrl } } }
              : {}),
          },
        },
      });
      if (data?.updateWebapp?.errors?.length) {
        toast.error(t("An error occurred while updating the web app"));
        return;
      }
      toast.success(t("Web app updated successfully"));
      clearCache();
      onRefetch();
    } catch (error) {
      if (isRequestTooLargeError(error)) {
        toast.error(t("Web app is too large to save."));
      } else {
        toast.error(t("An error occurred while updating the web app"));
      }
    } finally {
      setIsSaving(false);
    }
  };

  const handleCancel = () => {
    setName(webapp.name ?? "");
    setSubdomain(webapp.subdomain ?? "");
    setSourceUrl(webapp.url ?? "");
    setIcon(webapp.icon ?? null);
  };

  const isDirty =
    name !== (webapp.name ?? "") ||
    icon !== (webapp.icon ?? null) ||
    (isStatic
      ? subdomain !== (webapp.subdomain ?? "")
      : sourceUrl !== (webapp.url ?? ""));

  // A new version was committed, by the assistant or from the editor: the
  // preview and the editor follow the latest version again.
  const handleVersionSaved = useCallback(() => {
    setVersionRef(null);
    setDiffCommitId(null);
    refreshVersions();
  }, [refreshVersions]);

  const [conversations, setConversations] = useState<WebappConversation[]>([]);
  const [activeConversationId, setActiveConversationId] = useState<
    string | null
  >(null);
  const seededRef = useRef(false);

  useEffect(() => {
    if (seededRef.current || !webapp) return;
    seededRef.current = true;
    const convs = webapp.assistantConversations ?? [];
    setConversations(convs);
    setActiveConversationId(convs[0]?.id ?? null);
  }, [webapp?.id]);

  const { isOpen: isAssistantOpen, toggle: toggleAssistant } = useAssistantDock(
    ASSISTANT_STORAGE_KEY,
  );
  const assistantAvailable = showAssistant && isStatic;

  const segments: Segment<View>[] = [
    { id: "preview", label: t("Preview"), icon: EyeIcon },
    ...(isStatic
      ? [
          { id: "code" as const, label: t("Code"), icon: CodeBracketIcon },
          { id: "history" as const, label: t("History"), icon: ClockIcon },
        ]
      : []),
    { id: "settings", label: t("Settings"), icon: Cog6ToothIcon },
  ];

  const previewUrl =
    (isStatic ? previewData?.webapp?.previewUrl || webapp.previewUrl : null) ||
    webapp.url ||
    webapp.serveUrl ||
    "";

  const shortRef = (ref: string) => ref.substring(0, 7);

  // Both axes in one line: the public/private state visitors already know
  // from the other pages, followed by which version they get.
  const liveSha = publishedVersionId ? shortRef(publishedVersionId) : null;
  const accessWord = webapp.isPublic ? t("Public") : t("Private");
  const accessSentence = !isStatic ? (
    accessWord
  ) : liveSha ? (
    <>
      {accessWord} &middot;{" "}
      {webapp.isPublic ? (
        <Trans>
          anyone with the link sees version{" "}
          <code className="font-mono text-gray-700">{liveSha}</code>
        </Trans>
      ) : (
        <Trans>
          workspace members see version{" "}
          <code className="font-mono text-gray-700">{liveSha}</code>
        </Trans>
      )}
    </>
  ) : (
    <>
      {accessWord} &middot; {t("no version is live yet")}
    </>
  );

  const versionPill = !isStatic ? (
    <span className="inline-flex items-center gap-1.5 text-[11px] font-semibold text-emerald-600">
      <span className="h-[7px] w-[7px] rounded-full bg-emerald-500" />
      {t("Live version")}
    </span>
  ) : versionRef ? (
    <span className="inline-flex items-center gap-1.5 text-[11px] font-semibold text-gray-600">
      <span className="h-[7px] w-[7px] rounded-full bg-gray-400" />
      {t("Version")}{" "}
      <code className="font-mono text-gray-700">{shortRef(versionRef)}</code>
    </span>
  ) : isLiveLatest ? (
    <span className="inline-flex items-center gap-1.5 text-[11px] font-semibold text-emerald-600">
      <span className="h-[7px] w-[7px] rounded-full bg-emerald-500" />
      {t("Live version")}
    </span>
  ) : latestVersionId ? (
    <span className="inline-flex items-center gap-1.5 text-[11px] font-semibold text-amber-700">
      <span className="h-[7px] w-[7px] rounded-full bg-amber-500" />
      {t("Draft changes, not live")}
    </span>
  ) : null;

  const publishButton = canEdit && (
    <button
      onClick={handlePublishLatest}
      disabled={isPublishing}
      className="inline-flex items-center gap-1.5 rounded border border-amber-300 bg-white px-2.5 py-1 text-xs font-medium text-amber-900 hover:bg-amber-50 disabled:opacity-60"
    >
      {isPublishing && <Spinner size="xs" />}
      {isPublishing ? t("Publishing...") : t("Publish draft")}
    </button>
  );

  const rollbackButton = (ref: string) =>
    canEdit &&
    ref !== latestVersionId && (
      <button
        onClick={() => setRestoreTarget(ref)}
        className="inline-flex items-center gap-1.5 rounded border border-amber-300 bg-white px-2.5 py-1 text-xs font-medium text-amber-900 hover:bg-amber-50"
      >
        {t("Restore this version")}
      </button>
    );

  // Shown above the code and preview panes whenever what is displayed is not
  // the live version: an older version being browsed, or unpublished changes.
  const versionBanner = !isStatic ? null : versionRef ? (
    <BrowsingVersionBanner
      label={
        <>
          {view === "code" ? t("Browsing version") : t("Previewing version")}{" "}
          <code className="font-mono text-amber-900">
            {shortRef(versionRef)}
          </code>{" "}
          &middot; {t("read-only")}
          {publishedVersionId && versionRef !== publishedVersionId && (
            <>
              {" "}
              &middot; {t("visitors see")}{" "}
              <code className="font-mono text-amber-900">
                {shortRef(publishedVersionId)}
              </code>
            </>
          )}
        </>
      }
      actions={rollbackButton(versionRef)}
      onBack={() => setVersionRef(null)}
    />
  ) : latestVersionId && !isLiveLatest ? (
    <div className="flex flex-none items-center gap-3 border-b border-amber-100 bg-amber-50 px-5 py-2 text-[13px]">
      <span className="text-amber-800">
        {publishedVersionId ? (
          <>
            {t("Visitors see version")}{" "}
            <code className="font-mono text-amber-900">
              {shortRef(publishedVersionId)}
            </code>{" "}
            &middot;{" "}
            {view === "code"
              ? t("you are editing the newer draft")
              : t("you are previewing the newer draft")}{" "}
            <code className="font-mono text-amber-900">
              {shortRef(latestVersionId)}
            </code>
          </>
        ) : (
          t("No version is live yet")
        )}
      </span>
      <div className="ml-auto flex items-center gap-3">{publishButton}</div>
    </div>
  ) : null;

  return (
    <DetailShell>
      <DetailHeader
        icon={
          <img
            src={webapp.icon || PLACEHOLDER_ICON}
            alt=""
            className="h-full w-full object-cover"
          />
        }
        title={webapp.name}
        badges={
          <>
            <DetailBadge color="indigo">
              {t("{{type}} app", { type: getWebappTypeLabel(webapp.type) })}
            </DetailBadge>
          </>
        }
        meta={[
          displayUrl && (
            <span className="inline-flex items-center gap-1.5 text-gray-500">
              <ArrowTopRightOnSquareIcon className="h-3.5 w-3.5" />
              <a
                href={webapp.serveUrl ?? webapp.url ?? "#"}
                target="_blank"
                rel="noopener noreferrer"
                className="text-blue-600 hover:text-blue-700"
              >
                {displayUrl}
              </a>
            </span>
          ),
          <span
            key="access"
            className="inline-flex items-center gap-1.5 text-gray-500"
          >
            {webapp.isPublic ? (
              <GlobeAltIcon className="h-3.5 w-3.5" />
            ) : (
              <LockClosedIcon className="h-3.5 w-3.5" />
            )}
            {accessSentence}
          </span>,
        ]}
      />

      <DetailShell.Body>
        <DetailShell.Main>
          <SegmentedViewSwitcher
            segments={segments}
            value={view}
            onChange={setView}
            actions={
              <>
                {(view === "preview" || view === "code") && versionPill}
                {assistantAvailable && !isAssistantOpen && (
                  <div className="ml-auto flex-none">
                    <Button
                      onClick={toggleAssistant}
                      variant="secondary"
                      size="md"
                      leadingIcon={<SparklesIcon className="h-4 w-4" />}
                    >
                      {t("AI Assistant")}
                    </Button>
                  </div>
                )}
              </>
            }
          />

          {view === "code" && isStatic && (
            <div className="flex min-h-0 flex-1 flex-col">
              {versionBanner}
              <div className="min-h-0 flex-1 p-5">
                <div className="h-full min-h-0 overflow-hidden rounded-[10px] border border-gray-200">
                  <WebappFilesEditor
                    key={versionRef ?? latestVersionId ?? "latest"}
                    webappId={webapp.id}
                    workspaceSlug={workspaceSlug}
                    webappSlug={webappSlug}
                    isEditable={canEdit && !versionRef}
                    versionRef={versionRef ?? undefined}
                    flush
                    onSaveSuccess={handleVersionSaved}
                  />
                </div>
              </div>
            </div>
          )}

          {view === "preview" && (
            <div className="flex min-h-0 flex-1 flex-col">
              {versionBanner}
              <DetailViewPane className="bg-gray-100 p-5">
                <div className="mx-auto h-full max-w-[900px] overflow-hidden rounded-[10px] border border-gray-200 bg-white shadow-sm">
                  {previewReady ? (
                    <WebappIframe
                      key={`${previewUrl}:${previewRef ?? ""}`}
                      url={previewUrl}
                      type={webapp.type}
                      style={{ height: "100%" }}
                    />
                  ) : (
                    <div className="flex h-full items-center justify-center">
                      <Spinner size="md" />
                    </div>
                  )}
                </div>
              </DetailViewPane>
            </div>
          )}

          {view === "history" && isStatic && (
            <DetailViewPane className="px-5 py-4">
              {diffCommitId ? (
                <div className="space-y-4">
                  <button
                    onClick={() => setDiffCommitId(null)}
                    className="inline-flex items-center gap-1.5 text-sm text-gray-500 hover:text-gray-700 hover:underline"
                  >
                    <ArrowUturnLeftIcon className="h-3.5 w-3.5" />
                    {t("Back to history")}
                  </button>
                  <CommitDiff
                    workspaceSlug={workspaceSlug}
                    webappSlug={webappSlug}
                    commitId={diffCommitId}
                    onBrowse={browseCommit}
                  />
                </div>
              ) : (
                <WebappHistory
                  workspaceSlug={workspaceSlug}
                  webappSlug={webappSlug}
                  onSelectCommit={setDiffCommitId}
                  onBrowseCommit={browseCommit}
                  onPreviewCommit={previewCommit}
                  onRollbackCommit={setRestoreTarget}
                  canEdit={canEdit}
                />
              )}
            </DetailViewPane>
          )}

          {view === "settings" && (
            <DetailViewPane className="bg-gray-50 px-5 py-4">
              <div className="mx-auto max-w-4xl space-y-4">
                <SettingsCard
                  title={t("Details")}
                  footer={
                    canEdit && (
                      <>
                        <button
                          onClick={handleCancel}
                          disabled={!isDirty || isSaving}
                          className="rounded border border-gray-300 bg-white px-3.5 py-2 text-[13px] font-medium text-gray-800 hover:bg-gray-50 disabled:opacity-60"
                        >
                          {t("Cancel")}
                        </button>
                        <button
                          onClick={handleSave}
                          disabled={!isDirty || isSaving}
                          className="inline-flex items-center gap-1.5 rounded border-none bg-blue-600 px-3.5 py-2 text-[13px] font-medium text-white hover:bg-blue-700 disabled:opacity-60"
                        >
                          {isSaving && <Spinner size="xs" />}
                          {t("Save")}
                        </button>
                      </>
                    )
                  }
                >
                  <div className="flex items-start gap-6">
                    <div className="flex w-22 flex-none flex-col items-center gap-2">
                      <img
                        src={icon || PLACEHOLDER_ICON}
                        alt=""
                        className="h-14 w-14 rounded-[10px] border border-gray-100 object-cover"
                      />
                      {canEdit && (
                        <label
                          htmlFor="webapp-icon-upload"
                          className="cursor-pointer text-xs font-medium text-indigo-600 underline hover:text-indigo-500"
                        >
                          <input
                            id="webapp-icon-upload"
                            type="file"
                            accept="image/png,image/jpeg,image/jpg"
                            className="sr-only"
                            onChange={handleIconChange}
                          />
                          {t("Change icon")}
                        </label>
                      )}
                    </div>
                    <div className="grid flex-1 grid-cols-2 gap-x-5 gap-y-3.5">
                      <div className="flex flex-col gap-1.5">
                        <label className="text-xs font-medium text-gray-700">
                          {t("Name")}
                        </label>
                        <input
                          type="text"
                          value={name}
                          disabled={!canEdit}
                          onChange={(e) => setName(e.target.value)}
                          className="w-full rounded-md border border-gray-300 px-2.5 py-2 text-[13px] text-gray-900 outline-hidden focus:border-blue-600 focus:ring-1 focus:ring-blue-600 disabled:bg-gray-50 disabled:text-gray-500"
                        />
                      </div>

                      {isStatic ? (
                        <div className="flex flex-col gap-1.5">
                          <label className="text-xs font-medium text-gray-700">
                            {t("Web app link")}
                          </label>
                          <div className="flex items-center overflow-hidden rounded-md border border-gray-300 text-[13px] focus-within:border-blue-600 focus-within:ring-1 focus-within:ring-blue-600">
                            <span className="py-2 pl-2.5 text-gray-400">
                              {urlParts?.prefix ?? "https://"}
                            </span>
                            <input
                              type="text"
                              value={subdomain}
                              disabled={!canEdit}
                              onChange={(e) => setSubdomain(e.target.value)}
                              className="min-w-0 flex-1 border-none px-1 py-2 font-mono text-[13px] text-gray-900 outline-hidden disabled:text-gray-500"
                            />
                            <span className="whitespace-nowrap py-2 pr-2.5 text-gray-400">
                              {urlParts?.suffix ?? ""}
                            </span>
                          </div>
                        </div>
                      ) : (
                        <div className="flex flex-col gap-1.5">
                          <label className="text-xs font-medium text-gray-700">
                            {t("Source URL")}
                          </label>
                          <input
                            type="text"
                            value={sourceUrl}
                            disabled={!canEdit}
                            onChange={(e) => setSourceUrl(e.target.value)}
                            className="w-full rounded-md border border-gray-300 px-2.5 py-2 text-[13px] text-gray-900 outline-hidden focus:border-blue-600 focus:ring-1 focus:ring-blue-600 disabled:bg-gray-50 disabled:text-gray-500"
                          />
                        </div>
                      )}
                    </div>
                  </div>
                </SettingsCard>

                {isStatic && !webapp.isPublic && (
                  <WebappApiAccess webapp={webapp} />
                )}

                {onDelete && (
                  <SettingsCard
                    title={t("Danger zone")}
                    className="border-red-200"
                  >
                    <div className="flex items-center justify-between gap-4">
                      <div className="text-sm">
                        <div className="font-medium text-gray-900">
                          {t("Delete this web app")}
                        </div>
                        <div className="text-gray-500">
                          {t("Once deleted, this web app cannot be recovered.")}
                        </div>
                      </div>
                      <Button
                        variant="danger"
                        onClick={onDelete}
                        leadingIcon={<TrashIcon className="h-4 w-4" />}
                        className="whitespace-nowrap"
                      >
                        {t("Delete")}
                      </Button>
                    </div>
                  </SettingsCard>
                )}
              </div>
            </DetailViewPane>
          )}
        </DetailShell.Main>

        {assistantAvailable && isAssistantOpen && (
          <AssistantDock storageKey={ASSISTANT_STORAGE_KEY}>
            <WebappEditChatPanel
              webappId={webapp.id}
              workspaceSlug={workspaceSlug}
              onVersionSaved={handleVersionSaved}
              conversations={conversations}
              activeConversationId={activeConversationId}
              onConversationChange={setActiveConversationId}
              onNewConversation={() => setActiveConversationId(null)}
              onConversationCreated={(conversation) => {
                setConversations((prev) => [conversation, ...prev]);
                setActiveConversationId(conversation.id);
              }}
              onConversationNameChange={(id, conversationName) =>
                setConversations((prev) =>
                  prev.map((c) =>
                    c.id === id ? { ...c, name: conversationName } : c,
                  ),
                )
              }
              flush
              onClose={toggleAssistant}
            />
          </AssistantDock>
        )}
      </DetailShell.Body>
      {isStatic && (
        <RestoreWebappVersionDialog
          open={restoreTarget !== null}
          onClose={() => setRestoreTarget(null)}
          webappId={webapp.id}
          versionId={restoreTarget}
          onRestored={handleRestored}
        />
      )}
    </DetailShell>
  );
};

export default WebappDetail;
