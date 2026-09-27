import {
  ArrowTopRightOnSquareIcon,
  ArrowUturnLeftIcon,
  ClockIcon,
  CodeBracketIcon,
  Cog6ToothIcon,
  EyeIcon,
  GlobeAltIcon,
  SparklesIcon,
  TrashIcon,
} from "@heroicons/react/24/outline";
import AssistantProposalBanner from "assistant/features/AssistantProposalBanner";
import WebappEditChatPanel, {
  WebappConversation,
  WebappProposedFile,
} from "assistant/features/WebappEditChatPanel";
import { useResolveAssistantProposalMutation } from "assistant/graphql/mutations.generated";
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
import { DateTime } from "luxon";
import { useTranslation } from "next-i18next";
import {
  ChangeEvent,
  useCallback,
  useEffect,
  useMemo,
  useRef,
  useState,
} from "react";
import { toast } from "react-toastify";
import { useUpdateWebappMutation } from "webapps/graphql/mutations.generated";
import { useWebappVersionsQuery } from "webapps/graphql/queries.generated";
import CommitDiff from "webapps/features/CommitDiff/CommitDiff";
import WebappApiAccess from "webapps/features/WebappApiAccess";
import WebappFilesEditor from "webapps/features/WebappFilesEditor/WebappFilesEditor";
import WebappHistory from "webapps/features/WebappHistory/WebappHistory";
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
  monthlyLimitExceeded: boolean;
  isReviewing?: boolean;
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
  monthlyLimitExceeded,
  isReviewing = false,
  onRefetch,
  onDelete,
}: WebappDetailProps) => {
  const { t } = useTranslation();
  const isStatic = webapp.type === WebappType.Static;
  const canEdit = Boolean(webapp.permissions?.update);

  const [view, setView] = useState<View>(isStatic ? "code" : "preview");
  const [isSaving, setIsSaving] = useState(false);
  const [versionRef, setVersionRef] = useState<string | null>(null);
  const [diffCommitId, setDiffCommitId] = useState<string | null>(null);
  const [isPublishing, setIsPublishing] = useState(false);

  const [name, setName] = useState<string>(webapp.name ?? "");
  const [subdomain, setSubdomain] = useState<string>(webapp.subdomain ?? "");
  const [sourceUrl, setSourceUrl] = useState<string>(webapp.url ?? "");
  const [icon, setIcon] = useState<string | null>(webapp.icon ?? null);

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
  });
  const latestVersion = versionsData?.webapp?.versions?.items?.[0];
  const publishedVersionId =
    webapp.source?.__typename === "GitSource"
      ? webapp.source.publishedVersion
      : null;

  const browseCommit = useCallback((commitId: string) => {
    setDiffCommitId(null);
    setVersionRef(commitId);
    setView("code");
  }, []);

  const handlePublishVersion = async () => {
    if (!versionRef || isPublishing) return;
    setIsPublishing(true);
    try {
      const { data } = await updateWebapp({
        variables: { input: { id: webapp.id, publishedVersionId: versionRef } },
        refetchQueries: ["WebappVersions"],
      });
      if (data?.updateWebapp?.success) {
        toast.success(t("Version published successfully"));
        onRefetch();
      } else {
        toast.error(t("Failed to publish version"));
      }
    } catch {
      toast.error(t("Failed to publish version"));
    } finally {
      setIsPublishing(false);
    }
  };

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

  // ---- assistant / proposals ----
  const [resolveProposal] = useResolveAssistantProposalMutation();
  const [proposedFiles, setProposedFiles] = useState<
    WebappProposedFile[] | null
  >(null);
  const [proposedToolInvocationId, setProposedToolInvocationId] = useState<
    string | null
  >(null);

  const handleProposedFiles = useCallback(
    (files: WebappProposedFile[] | null, toolInvocationId?: string) => {
      setProposedFiles(files);
      if (toolInvocationId !== undefined) {
        setProposedToolInvocationId(toolInvocationId);
      } else if (files !== null) {
        setProposedToolInvocationId(null);
      }
      if (files) {
        // Proposals always apply to the latest version, never to a browsed commit.
        setVersionRef(null);
        setDiffCommitId(null);
        setView("code");
      }
    },
    [],
  );

  const handleDismiss = useCallback(async () => {
    setProposedFiles(null);
    const idToDismiss = proposedToolInvocationId;
    setProposedToolInvocationId(null);
    if (idToDismiss) {
      await resolveProposal({ variables: { toolInvocationId: idToDismiss } });
    }
  }, [proposedToolInvocationId, resolveProposal]);

  const handleSaveSuccess = useCallback(() => {
    onRefetch();
    const idToResolve = proposedToolInvocationId;
    setProposedFiles(null);
    setProposedToolInvocationId(null);
    if (idToResolve) {
      resolveProposal({ variables: { toolInvocationId: idToResolve } });
    }
  }, [proposedToolInvocationId, resolveProposal, onRefetch]);

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
    (isStatic ? webapp.previewUrl : null) ||
    webapp.url ||
    webapp.serveUrl ||
    "";

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
            {webapp.isPublic && (
              <DetailBadge
                color="emerald"
                icon={<GlobeAltIcon className="h-3 w-3" />}
              >
                {t("Public")}
              </DetailBadge>
            )}
            {isReviewing && (
              <DetailBadge color="amber" icon={<Spinner size="xs" />}>
                {t("Security review in progress")}
              </DetailBadge>
            )}
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
          latestVersion && (
            <span className="text-gray-500">
              {t("Latest")}{" "}
              <code className="font-mono text-gray-700">
                {latestVersion.id.substring(0, 7)}
              </code>{" "}
              &middot; {DateTime.fromISO(latestVersion.date).toRelative()}
            </span>
          ),
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
                {view === "preview" && (
                  <span className="inline-flex items-center gap-1.5 text-[11px] font-semibold text-emerald-600">
                    <span className="h-[7px] w-[7px] rounded-full bg-emerald-500" />
                    {t("Live")}
                  </span>
                )}
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
              {versionRef && (
                <BrowsingVersionBanner
                  label={
                    <>
                      {t("Browsing")}{" "}
                      <code className="font-mono text-amber-900">
                        {versionRef.substring(0, 7)}
                      </code>{" "}
                      &middot; {t("read-only")}
                    </>
                  }
                  actions={
                    canEdit &&
                    versionRef !== publishedVersionId && (
                      <button
                        onClick={handlePublishVersion}
                        disabled={isPublishing}
                        className="inline-flex items-center gap-1.5 rounded border border-amber-300 bg-white px-2.5 py-1 text-xs font-medium text-amber-900 hover:bg-amber-50 disabled:opacity-60"
                      >
                        {isPublishing && <Spinner size="xs" />}
                        {isPublishing ? t("Publishing...") : t("Publish")}
                      </button>
                    )
                  }
                  onBack={() => setVersionRef(null)}
                />
              )}
              {proposedFiles && (
                <AssistantProposalBanner
                  label={t("Proposed changes from AI assistant")}
                  onDismiss={handleDismiss}
                  className="mx-5 mt-4"
                />
              )}
              <div className="min-h-0 flex-1 p-5">
                <div className="h-full min-h-0 overflow-hidden rounded-[10px] border border-gray-200">
                  <WebappFilesEditor
                    key={versionRef ?? "latest"}
                    webappId={webapp.id}
                    workspaceSlug={workspaceSlug}
                    webappSlug={webappSlug}
                    isEditable={canEdit && !versionRef}
                    versionRef={versionRef ?? undefined}
                    proposedFiles={proposedFiles ?? undefined}
                    flush
                    onSaveSuccess={handleSaveSuccess}
                  />
                </div>
              </div>
            </div>
          )}

          {view === "preview" && (
            <DetailViewPane className="bg-gray-100 p-5">
              <div className="mx-auto h-full max-w-[900px] overflow-hidden rounded-[10px] border border-gray-200 bg-white shadow-sm">
                <WebappIframe
                  url={previewUrl}
                  type={webapp.type}
                  style={{ height: "100%" }}
                />
              </div>
            </DetailViewPane>
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
                            {t("Published URL")}
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

                {isStatic && <WebappApiAccess webapp={webapp} />}

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
              monthlyLimitExceeded={monthlyLimitExceeded}
              onProposedFiles={handleProposedFiles}
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
    </DetailShell>
  );
};

export default WebappDetail;
