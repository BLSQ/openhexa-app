import { PlusIcon } from "@heroicons/react/24/outline";
import Breadcrumbs from "core/components/Breadcrumbs";
import Button from "core/components/Button";
import Page from "core/components/Page";
import { createGetServerSideProps } from "core/helpers/page";
import { NextPageWithLayout } from "core/helpers/types";
import { useTranslation } from "next-i18next";
import {
  WorkspacePageDocument,
  WorkspacePageQuery,
} from "workspaces/graphql/queries.generated";
import { useRouter } from "next/router";
import WorkspaceLayout from "workspaces/layouts/WorkspaceLayout";
import React, { useState } from "react";
import Tabs from "core/components/Tabs";
import useFeature from "identity/hooks/useFeature";
import PipelineTemplates from "pipelines/features/PipelineTemplates";
import Pipelines from "pipelines/features/Pipelines/Pipelines";
import CreatePipelineDialog from "workspaces/features/CreatePipelineDialog";
import { WorkspaceLayout_WorkspaceFragment } from "workspaces/layouts/WorkspaceLayout/WorkspaceLayout.generated";

type Props = {
  workspace: WorkspaceLayout_WorkspaceFragment;
};

const WorkspacePipelinesPage: NextPageWithLayout = ({ workspace }: Props) => {
  const { t } = useTranslation();
  const router = useRouter();
  const [pipelineTemplateFeatureEnabled] = useFeature("pipeline_templates");
  const [isDialogOpen, setDialogOpen] = useState(false);

  const tab = router.query.tab === "templates" ? "templates" : "pipelines";

  if (!workspace) {
    return null;
  }
  return (
    <Page title={workspace.name}>
      <WorkspaceLayout
        workspace={workspace}
        helpLinks={[
          {
            label: t("About pipelines"),
            href: "https://github.com/BLSQ/openhexa/wiki/User-manual#using-pipelines",
          },
          {
            label: t("Writing OpenHEXA pipelines"),
            href: "https://github.com/BLSQ/openhexa/wiki/Writing-OpenHEXA-pipelines",
          },
        ]}
        header={
          <>
            <Breadcrumbs withHome={false} className="flex-1">
              <Breadcrumbs.Part
                isFirst
                href={`/workspaces/${encodeURIComponent(workspace.slug)}`}
              >
                {workspace.name}
              </Breadcrumbs.Part>
              <Breadcrumbs.Part
                isLast
                href={`/workspaces/${encodeURIComponent(
                  workspace.slug,
                )}/pipelines/?tab=${tab}`}
              >
                {tab === "pipelines" ? t("Pipelines") : t("Templates")}
              </Breadcrumbs.Part>
            </Breadcrumbs>
            <Button
              leadingIcon={<PlusIcon className="h-4 w-4" />}
              onClick={() => setDialogOpen(true)}
            >
              {t("Create")}
            </Button>
          </>
        }
      >
        <WorkspaceLayout.PageContent className="divide divide-y-2">
          <Tabs
            onChange={(newIndex) =>
              router.push(
                {
                  pathname: router.pathname,
                  query: {
                    ...router.query,
                    tab: newIndex === 1 ? "templates" : "pipelines",
                  },
                },
                undefined,
                { shallow: true },
              )
            }
            defaultIndex={tab === "templates" ? 1 : 0}
          >
            <Tabs.Tab label={t("Pipelines")} className={"space-y-2 pt-2"}>
              <Pipelines workspace={workspace} />
            </Tabs.Tab>
            {pipelineTemplateFeatureEnabled && (
              <Tabs.Tab
                label={t("Available Templates")}
                className={"space-y-2 pt-2"}
              >
                <PipelineTemplates workspace={workspace} />
              </Tabs.Tab>
            )}
          </Tabs>
        </WorkspaceLayout.PageContent>
      </WorkspaceLayout>
      <CreatePipelineDialog
        workspace={workspace}
        open={isDialogOpen}
        onClose={() => setDialogOpen(false)}
      />
    </Page>
  );
};

WorkspacePipelinesPage.getLayout = (page) => page;

export const getServerSideProps = createGetServerSideProps({
  requireAuth: true,
  async getServerSideProps(ctx, client) {
    await WorkspaceLayout.prefetch(ctx, client);
    const { data } = await client.query<WorkspacePageQuery>({
      query: WorkspacePageDocument,
      variables: {
        slug: ctx.params?.workspaceSlug,
      },
    });

    if (!data.workspace) {
      return {
        notFound: true,
      };
    }
    return {
      props: {
        workspace: data.workspace,
      },
    };
  },
});

export default WorkspacePipelinesPage;
