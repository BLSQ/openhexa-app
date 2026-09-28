import {
  EyeIcon,
  GlobeAltIcon,
  LockClosedIcon,
} from "@heroicons/react/24/outline";
import Breadcrumbs from "core/components/Breadcrumbs";
import Button from "core/components/Button";
import Page from "core/components/Page";
import Spinner from "core/components/Spinner";
import { createGetServerSideProps } from "core/helpers/page";
import { NextPageWithLayout } from "core/helpers/types";
import useCacheKey from "core/hooks/useCacheKey";
import { WebappType } from "graphql/types";
import { useTranslation } from "next-i18next";
import Link from "next/link";
import { useEffect, useRef, useState } from "react";
import { toast } from "react-toastify";
import MakeWebappPrivateDialog from "webapps/features/MakeWebappPrivateDialog";
import MakeWebappPublicDialog from "webapps/features/MakeWebappPublicDialog";
import WebappDetail from "webapps/features/WebappDetail/WebappDetail";
import GitClonePopover from "webapps/features/GitClonePopover/GitClonePopover";
import { useUpdateWebappMutation } from "webapps/graphql/mutations.generated";
import DeleteWebappDialog from "workspaces/features/DeleteWebappDialog/DeleteWebappDialog";
import {
  useWorkspaceWebappPageQuery,
  WorkspaceWebappPageDocument,
  WorkspaceWebappPageQuery,
  WorkspaceWebappPageQueryVariables,
} from "workspaces/graphql/queries.generated";
import WebappLayout from "workspaces/layouts/WebappLayout";
import WorkspaceLayout from "workspaces/layouts/WorkspaceLayout";

type Props = {
  webappSlug: string;
  workspaceSlug: string;
};

// Frontend-only stand-in: the real review will be driven by the backend, which
// will report its own progress and outcome. Until then the page fakes the wait
// so the surrounding flow can be evaluated.
const MOCK_REVIEW_DURATION = 3000;

const WorkspaceWebappPage: NextPageWithLayout = (props: Props) => {
  const { webappSlug, workspaceSlug } = props;
  const { t } = useTranslation();
  const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false);
  const [isTogglingVisibility, setIsTogglingVisibility] = useState(false);
  const [isPublicDialogOpen, setIsPublicDialogOpen] = useState(false);
  const [isPrivateDialogOpen, setIsPrivateDialogOpen] = useState(false);
  const [isReviewing, setIsReviewing] = useState(false);
  const reviewTimeout = useRef<ReturnType<typeof setTimeout> | null>(null);
  const [updateWebapp] = useUpdateWebappMutation();

  useEffect(
    () => () => {
      if (reviewTimeout.current) clearTimeout(reviewTimeout.current);
    },
    [],
  );

  const { data, refetch } = useWorkspaceWebappPageQuery({
    variables: { workspaceSlug, webappSlug },
  });
  useCacheKey("webapps", refetch);

  if (!data?.workspace || !data?.webapp) {
    return null;
  }

  const { workspace, webapp } = data;
  const source = webapp.source;
  const repositoryUrl =
    source?.__typename === "GitSource" ? source.repositoryUrl : null;
  const showAssistant = workspace.organization?.aiSettings?.enabled ?? false;

  const setVisibility = async (isPublic: boolean) => {
    setIsTogglingVisibility(true);
    try {
      const { data: updated } = await updateWebapp({
        variables: { input: { id: webapp.id, isPublic } },
      });
      if (updated?.updateWebapp?.errors?.length) {
        toast.error(t("An error occurred while updating the web app"));
        return false;
      }
      refetch().then();
      return true;
    } finally {
      setIsTogglingVisibility(false);
    }
  };

  const handleToggleVisibility = () => {
    if (webapp.isPublic) {
      setIsPrivateDialogOpen(true);
    } else if (webapp.type === WebappType.Static) {
      setIsPublicDialogOpen(true);
    } else {
      setVisibility(true).then();
    }
  };

  const handleConfirmPrivate = async () => {
    await setVisibility(false);
    setIsPrivateDialogOpen(false);
  };

  const handleConfirmPublic = () => {
    setIsPublicDialogOpen(false);
    setIsReviewing(true);
    reviewTimeout.current = setTimeout(async () => {
      const published = await setVisibility(true);
      setIsReviewing(false);
      if (published) {
        toast.success(t("Security review passed. This web app is now public."));
      }
    }, MOCK_REVIEW_DURATION);
  };

  return (
    <Page title={webapp.name}>
      <WorkspaceLayout
        workspace={workspace}
        withMarginBottom={false}
        className="h-screen"
        header={
          <Breadcrumbs withHome={false} className="flex-1">
            <Breadcrumbs.Part
              isFirst
              href={`/workspaces/${encodeURIComponent(workspace.slug)}/webapps`}
            >
              {t("Web Apps")}
            </Breadcrumbs.Part>
            <Breadcrumbs.Part
              isLast
              href={`/workspaces/${encodeURIComponent(workspace.slug)}/webapps/${encodeURIComponent(webapp.slug)}`}
            >
              {webapp.name}
            </Breadcrumbs.Part>
          </Breadcrumbs>
        }
        headerActions={
          <div className="flex items-center gap-2">
            {repositoryUrl && webapp.type === WebappType.Static && (
              <GitClonePopover repositoryUrl={repositoryUrl} />
            )}
            {webapp.permissions.update && (
              <Button
                variant="white"
                onClick={handleToggleVisibility}
                disabled={isTogglingVisibility || isReviewing}
                leadingIcon={
                  isReviewing ? (
                    <Spinner size="xs" />
                  ) : webapp.isPublic ? (
                    <LockClosedIcon className="h-4 w-4" />
                  ) : (
                    <GlobeAltIcon className="h-4 w-4" />
                  )
                }
              >
                {isReviewing
                  ? t("Reviewing...")
                  : webapp.isPublic
                    ? t("Make private")
                    : t("Make public")}
              </Button>
            )}
            <Link href={webapp.serveUrl ?? webapp.url ?? "#"} target="_blank">
              <Button
                variant="primary"
                leadingIcon={<EyeIcon className="h-4 w-4" />}
              >
                {t("View")}
              </Button>
            </Link>
          </div>
        }
      >
        <div className="h-full min-h-0">
          <WebappDetail
            workspaceSlug={workspaceSlug}
            webappSlug={webappSlug}
            webapp={webapp}
            showAssistant={showAssistant}
            monthlyLimitExceeded={
              data?.me?.assistantMonthlyLimitExceeded ?? false
            }
            isReviewing={isReviewing}
            onRefetch={() => {
              refetch().then();
            }}
            onDelete={
              webapp.permissions.delete
                ? () => setIsDeleteDialogOpen(true)
                : undefined
            }
          />
        </div>
      </WorkspaceLayout>
      <MakeWebappPublicDialog
        open={isPublicDialogOpen}
        onClose={() => setIsPublicDialogOpen(false)}
        onConfirm={handleConfirmPublic}
        webapp={webapp}
      />
      <MakeWebappPrivateDialog
        open={isPrivateDialogOpen}
        onClose={() => setIsPrivateDialogOpen(false)}
        onConfirm={handleConfirmPrivate}
        webapp={webapp}
      />
      <DeleteWebappDialog
        open={isDeleteDialogOpen}
        onClose={() => setIsDeleteDialogOpen(false)}
        webapp={webapp}
        workspace={workspace}
      />
    </Page>
  );
};

WorkspaceWebappPage.getLayout = (page) => page;

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
        workspace: data.workspace,
        webapp: data.webapp,
      },
    };
  },
});

export default WorkspaceWebappPage;
