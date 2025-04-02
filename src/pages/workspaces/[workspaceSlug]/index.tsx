import Block from "core/components/Block";
import Breadcrumbs from "core/components/Breadcrumbs";
import Button from "core/components/Button";
import MarkdownEditor from "core/components/MarkdownEditor/MarkdownEditor";
import MarkdownViewer from "core/components/MarkdownViewer";
import Page from "core/components/Page";
import Spinner from "core/components/Spinner";
import { createGetServerSideProps } from "core/helpers/page";
import { NextPageWithLayout } from "core/helpers/types";
import useCacheKey from "core/hooks/useCacheKey";
import { useTranslation } from "next-i18next";
import { useEffect, useState } from "react";
import { useUpdateWorkspaceMutation } from "workspaces/graphql/mutations.generated";
import {
  useWorkspacePageQuery,
  WorkspacePageDocument,
  WorkspacePageQuery,
} from "workspaces/graphql/queries.generated";
import WorkspaceLayout from "workspaces/layouts/WorkspaceLayout";

type Props = {
  workspaceSlug: string;
  page: number;
  perPage: number;
};

const WorkspaceHome: NextPageWithLayout = (props: Props) => {
  const { t } = useTranslation();

  useCacheKey("workspace", () => refetch());

  const [isEditing, setIsEditing] = useState(false);
  const [mutate, { loading }] = useUpdateWorkspaceMutation();
  const { data, refetch } = useWorkspacePageQuery({
    variables: { slug: props.workspaceSlug },
  });
  const [description, setDescription] = useState(
    data?.workspace?.description || "",
  );

  useEffect(() => {
    setIsEditing(false);
    setDescription(data?.workspace?.description || "");
  }, [data?.workspace?.description]);

  const onSave = async () => {
    await mutate({
      variables: {
        input: {
          slug: props.workspaceSlug,
          description: description.trim(),
        },
      },
    });
    setIsEditing(false);
  };

  if (!data?.workspace) {
    return null;
  }

  const { workspace } = data;
  return (
    <Page title={workspace.name}>
      <WorkspaceLayout
        workspace={workspace}
        helpLinks={[
          {
            href: "https://github.com/BLSQ/openhexa/wiki/User-manual#about-workspaces",
            label: t("About workspaces"),
          },
          {
            href: "https://github.com/BLSQ/openhexa/wiki/User-manual#editing-the-workspace-homepage",
            label: t("Editing the workspace homepage"),
          },
        ]}
        header={
          <>
            <Breadcrumbs withHome={false}>
              <Breadcrumbs.Part
                isFirst
                href={`/workspaces/${encodeURIComponent(workspace.slug)}`}
              >
                {workspace.name}
              </Breadcrumbs.Part>
            </Breadcrumbs>
            <div className="flex items-center gap-2">
              {workspace.permissions.update &&
                (isEditing ? (
                  <>
                    <Button
                      variant="secondary"
                      onClick={() => setIsEditing(false)}
                    >
                      {t("Cancel")}
                    </Button>
                    <Button
                      onClick={onSave}
                      leadingIcon={loading && <Spinner size="xs" />}
                    >
                      {t("Save")}
                    </Button>
                  </>
                ) : (
                  <Button onClick={() => setIsEditing(true)}>
                    {t("Edit")}
                  </Button>
                ))}
            </div>
          </>
        }
      >
        <WorkspaceLayout.PageContent>
          {isEditing ? (
            <div className="bg-white">
              <MarkdownEditor
                markdown={description || ""}
                onChange={(markdown) => {
                  setDescription(markdown);
                }}
              />
            </div>
          ) : (
            <Block>
              <Block.Content>
                <MarkdownViewer
                  key={data.workspace.slug} // Force re-render when slug changes, the markdown props is only read once and not triggering a re-render
                  markdown={workspace.description || ""}
                />
              </Block.Content>
            </Block>
          )}
        </WorkspaceLayout.PageContent>
      </WorkspaceLayout>
    </Page>
  );
};

WorkspaceHome.getLayout = (page) => page;

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
        workspaceSlug: ctx.params?.workspaceSlug,
      },
    };
  },
});

export default WorkspaceHome;
