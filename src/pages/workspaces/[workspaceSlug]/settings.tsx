import Breadcrumbs from "core/components/Breadcrumbs";
import Page from "core/components/Page";
import { createGetServerSideProps } from "core/helpers/page";
import { NextPageWithLayout } from "core/helpers/types";
import { useTranslation } from "next-i18next";

import WorkspaceLayout from "workspaces/layouts/WorkspaceLayout";
import Tabs from "core/components/Tabs";
import Button from "core/components/Button";
import { PlusCircleIcon, TrashIcon } from "@heroicons/react/24/outline";
import Block from "core/components/Block";
import {
  useWorkspacePageQuery,
  WorkspacePageDocument,
  WorkspacePageQuery,
} from "workspaces/graphql/queries.generated";
import DataCard from "core/components/DataCard";
import TextProperty from "core/components/DataCard/TextProperty";
import { OnSaveFn } from "core/components/DataCard/FormSection";
import { useUpdateWorkspaceMutation } from "workspaces/graphql/mutations.generated";
import { useState } from "react";
import InviteMemberDialog from "workspaces/features/InviteMemberDialog";
import WorkspaceMembers from "workspaces/features/WorkspaceMembers";
import CountryProperty from "core/components/DataCard/CountryProperty";
import { ensureArray } from "core/helpers/array";
import GenerateWorkspaceDatabasePasswordDialog from "workspaces/features/GenerateDatabasePasswordDialog";
import ArchiveWorkspaceDialog from "workspaces/features/ArchiveWorkspaceDialog";

type Props = {
  page: number;
  perPage: number;
  workspaceSlug: string;
};

const WorkspaceSettingsPage: NextPageWithLayout = (props: Props) => {
  const { t } = useTranslation();
  const { data, refetch } = useWorkspacePageQuery({
    variables: { slug: props.workspaceSlug },
  });

  const [mutate] = useUpdateWorkspaceMutation();
  const [isArchiveDialogOpen, setIsArchiveDialogOpen] = useState(false);
  const [isNewMemberDialogOpen, setIsNewMemberDialogOpen] = useState(false);
  const [isGeneratePwdDialogOpen, setIsGeneratePwdDialogOpen] = useState(false);

  const onSectionSave: OnSaveFn = async (values) => {
    await mutate({
      variables: {
        input: {
          slug: workspace.slug,
          name: values.name,
          countries: ensureArray(values.countries || workspace.countries).map(
            ({ code }) => ({
              code,
            })
          ),
        },
      },
    });
    await refetch();
  };

  if (!data?.workspace) {
    return null;
  }

  const { workspace } = data;

  return (
    <Page title={t("Workspace")}>
      <WorkspaceLayout workspace={workspace}>
        <WorkspaceLayout.Header className="flex justify-between">
          <Breadcrumbs withHome={false}>
            <Breadcrumbs.Part
              isFirst
              href={`/workspaces/${encodeURIComponent(workspace.slug)}`}
            >
              {workspace.name}
            </Breadcrumbs.Part>
            <Breadcrumbs.Part isLast>{t("Settings")}</Breadcrumbs.Part>
          </Breadcrumbs>
          {workspace.permissions.delete && (
            <Button
              size="sm"
              className="bg-red-700 hover:bg-red-700 focus:ring-red-500"
              onClick={() => setIsArchiveDialogOpen(true)}
              leadingIcon={<TrashIcon className="w-4" />}
            >
              {t("Archive")}
            </Button>
          )}
        </WorkspaceLayout.Header>
        <WorkspaceLayout.PageContent className="space-y-10">
          <div>
            <DataCard className="w-full" item={workspace}>
              <DataCard.FormSection
                onSave={onSectionSave}
                title={t("General settings")}
              >
                <TextProperty
                  required
                  id="name"
                  accessor="name"
                  label={t("Name")}
                  defaultValue="-"
                />
                <CountryProperty
                  id="countries"
                  accessor="countries"
                  multiple
                  visible={(value, isEditing) => isEditing || value?.length > 0}
                  label={t("Countries")}
                  defaultValue="-"
                />
              </DataCard.FormSection>
              <DataCard.Section title={t("Database")}>
                <Button
                  size="sm"
                  variant="secondary"
                  onClick={() => setIsGeneratePwdDialogOpen(true)}
                >
                  {t("Regenerate password")}
                </Button>
              </DataCard.Section>
            </DataCard>
          </div>

          <div>
            <Tabs defaultIndex={0}>
              <Tabs.Tab className="mt-4" label={t("Members")}>
                <div className="mb-4 flex justify-end">
                  <Button
                    onClick={() => setIsNewMemberDialogOpen(true)}
                    leadingIcon={<PlusCircleIcon className="mr-1 h-4 w-4" />}
                  >
                    {t("Invite member")}
                  </Button>
                </div>
                <Block>
                  <WorkspaceMembers workspaceSlug={workspace.slug} />
                </Block>
              </Tabs.Tab>
            </Tabs>
          </div>
          <ArchiveWorkspaceDialog
            workspace={workspace}
            open={isArchiveDialogOpen}
            onClose={() => {
              setIsArchiveDialogOpen(false);
            }}
          />
          <InviteMemberDialog
            open={isNewMemberDialogOpen}
            onClose={() => {
              setIsNewMemberDialogOpen(false);
            }}
            workspace={workspace}
          />
          <GenerateWorkspaceDatabasePasswordDialog
            open={isGeneratePwdDialogOpen}
            onClose={() => setIsGeneratePwdDialogOpen(false)}
            workspace={workspace}
          />
        </WorkspaceLayout.PageContent>
      </WorkspaceLayout>
    </Page>
  );
};

WorkspaceSettingsPage.getLayout = (page) => page;

export const getServerSideProps = createGetServerSideProps({
  requireAuth: true,
  async getServerSideProps(ctx, client) {
    const { data } = await client.query<WorkspacePageQuery>({
      query: WorkspacePageDocument,
      variables: {
        slug: ctx.params?.workspaceSlug,
      },
    });
    await WorkspaceLayout.prefetch(ctx, client);
    if (!data.workspace || !data.workspace.permissions.manageMembers) {
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

export default WorkspaceSettingsPage;
