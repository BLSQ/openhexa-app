import Page from "core/components/Page";
import { createGetServerSideProps } from "core/helpers/page";
import { NextPageWithLayout } from "core/helpers/types";
import { useTranslation } from "next-i18next";
import { useRouter } from "next/router";
import {
  useWorkspaceWebappPageQuery,
  WorkspaceWebappPageDocument,
  WorkspaceWebappPageQuery,
  WorkspaceWebappPageQueryVariables,
} from "workspaces/graphql/queries.generated";
import WebappLayout from "workspaces/layouts/WebappLayout";
import WebappFilesEditor from "webapps/features/WebappFilesEditor/WebappFilesEditor";
import VersionPicker from "webapps/features/VersionPicker/VersionPicker";
import useCacheKey from "core/hooks/useCacheKey";
import DataCard from "core/components/DataCard";
import Button from "core/components/Button";
import { WebappType } from "graphql/types";
import { useState } from "react";
import { useUpdateWebappMutation } from "webapps/graphql/mutations.generated";
import { toast } from "react-toastify";
import { WebappVersion_VersionFragment } from "webapps/graphql/queries.generated";
import Spinner from "core/components/Spinner";

type Props = {
  webappSlug: string;
  workspaceSlug: string;
};

const WorkspaceWebappCodePage: NextPageWithLayout = (props: Props) => {
  const { webappSlug, workspaceSlug } = props;
  const { t } = useTranslation();
  const router = useRouter();
  const initialRef = router.query.ref as string | undefined;

  const { data, refetch } = useWorkspaceWebappPageQuery({
    variables: { workspaceSlug, webappSlug },
  });
  useCacheKey("webapps", refetch);

  const [selectedVersion, setSelectedVersion] =
    useState<WebappVersion_VersionFragment | null>(null);
  const [updateWebapp] = useUpdateWebappMutation();
  const [isPublishing, setIsPublishing] = useState(false);
  const [isEditorBusy, setIsEditorBusy] = useState(false);

  if (!data?.workspace || !data?.webapp) {
    return null;
  }

  const { workspace, webapp } = data;

  if (webapp.type !== WebappType.Static) {
    return null;
  }

  const source = webapp.source;
  const publishedVersionId =
    source?.__typename === "GitSource" ? source.publishedVersion : null;
  const isViewingPublished =
    !selectedVersion || selectedVersion.id === publishedVersionId;

  const handlePublish = async () => {
    if (!selectedVersion || isPublishing) return;
    setIsPublishing(true);
    try {
      const { data } = await updateWebapp({
        variables: {
          input: { id: webapp.id, publishedVersionId: selectedVersion.id },
        },
        refetchQueries: ["WebappVersions"],
      });
      if (data?.updateWebapp?.success) {
        toast.success(t("Version published successfully"));
        refetch().then();
      } else {
        toast.error(t("Failed to publish version"));
      }
    } catch {
      toast.error(t("Failed to publish version"));
    } finally {
      setIsPublishing(false);
    }
  };

  return (
    <Page title={webapp.name}>
      <WebappLayout
        workspace={workspace}
        webapp={webapp}
        currentTab="code"
        extraActions={
          webapp.permissions.update && !isViewingPublished && !isEditorBusy ? (
            <Button
              variant="primary"
              onClick={handlePublish}
              disabled={isPublishing}
              leadingIcon={isPublishing ? <Spinner size="xs" /> : undefined}
            >
              {isPublishing ? t("Publishing...") : t("Publish")}
            </Button>
          ) : undefined
        }
      >
        <DataCard.FormSection>
          <WebappFilesEditor
            webappId={webapp.id}
            workspaceSlug={workspace.slug}
            webappSlug={webapp.slug}
            isEditable={webapp.permissions.update}
            versionRef={selectedVersion?.id}
            onSaveSuccess={() => refetch()}
            onBusyChange={setIsEditorBusy}
            versionPicker={
              <VersionPicker
                workspaceSlug={workspace.slug}
                webappSlug={webapp.slug}
                initialVersionId={initialRef}
                onChange={setSelectedVersion}
              />
            }
          />
        </DataCard.FormSection>
      </WebappLayout>
    </Page>
  );
};

WorkspaceWebappCodePage.getLayout = (page) => page;

export const getServerSideProps = createGetServerSideProps({
  requireAuth: true,
  async getServerSideProps(ctx, client) {
    await WebappLayout.prefetch(ctx, client);
    const { data } = await client.query<
      WorkspaceWebappPageQuery,
      WorkspaceWebappPageQueryVariables
    >({
      query: WorkspaceWebappPageDocument,
      variables: {
        workspaceSlug: ctx.params!.workspaceSlug as string,
        webappSlug: ctx.params!.webappSlug as string,
      },
    });

    if (!data.workspace || !data.webapp) {
      return { notFound: true };
    }

    return {
      props: {
        workspaceSlug: ctx.params!.workspaceSlug,
        webappSlug: ctx.params!.webappSlug,
      },
    };
  },
});

export default WorkspaceWebappCodePage;
