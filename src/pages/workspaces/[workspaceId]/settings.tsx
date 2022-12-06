import Breadcrumbs from "core/components/Breadcrumbs";
import Page from "core/components/Page";
import Title from "core/components/Title";
import { createGetServerSideProps } from "core/helpers/page";
import { NextPageWithLayout } from "core/helpers/types";
import { useTranslation } from "next-i18next";

import { useRouter } from "next/router";
import { WORKSPACES } from "workspaces/helpers/fixtures";
import WorkspaceLayout from "workspaces/layouts/WorkspaceLayout";
import Tabs from "core/components/Tabs";
import DataGrid, { BaseColumn } from "core/components/DataGrid";
import { TextColumn } from "core/components/DataGrid/TextColumn";
import Button from "core/components/Button";
import DateColumn from "core/components/DataGrid/DateColumn";
import { DateTime } from "luxon";
import { PlusCircleIcon } from "@heroicons/react/24/outline";

type Props = {
  page: number;
  perPage: number;
};

const WorkspaceSettingsPage: NextPageWithLayout = (props: Props) => {
  const { t } = useTranslation();
  const router = useRouter();
  const workspace = WORKSPACES.find((w) => w.id === router.query.workspaceId);

  if (!workspace) {
    return null;
  }

  return (
    <Page title={t("Workspace")}>
      <WorkspaceLayout.Header>
        <Breadcrumbs withHome={false}>
          <Breadcrumbs.Part
            isFirst
            href={`/workspaces/${encodeURIComponent(workspace.id)}`}
          >
            {workspace.name}
          </Breadcrumbs.Part>
          <Breadcrumbs.Part>{t("Settings")}</Breadcrumbs.Part>
        </Breadcrumbs>
      </WorkspaceLayout.Header>
      <WorkspaceLayout.PageContent>
        <Title level={2}>{t("Settings")}</Title>
        <Tabs defaultIndex={0}>
          <Tabs.Tab className="mt-4" label={t("Members")}>
            <div className="mt-5 grid grid-cols-2 gap-5">
              <div className="col-span-2 flex justify-between">
                <Title level={4}>{t("Workspace members")}</Title>
                <Button>
                  <PlusCircleIcon className="mr-1 h-6 w-6" />
                  <span>{t("Invite member")}</span>
                </Button>
              </div>
              <div className="col-span-2">
                <DataGrid
                  className="bg-white shadow-md"
                  defaultPageSize={5}
                  totalItems={workspace.members.length}
                  fixedLayout={false}
                  data={workspace.members}
                >
                  <TextColumn
                    className="max-w-[50ch] py-3 "
                    accessor="name"
                    id="name"
                    label="Name"
                  />
                  <TextColumn
                    className="max-w-[50ch] py-3 "
                    accessor="email"
                    id="email"
                    label="Email"
                  />
                  <TextColumn
                    className="max-w-[50ch] py-3 "
                    accessor="role"
                    label="Role"
                    id="member_role"
                  />
                  <DateColumn
                    className="max-w-[50ch] py-3 "
                    accessor="createdAt"
                    id="createdAt"
                    label="Joined"
                    format={DateTime.DATE_FULL}
                  />
                  <BaseColumn>{() => <Button>Edit</Button>}</BaseColumn>
                </DataGrid>
              </div>
            </div>
          </Tabs.Tab>
          <Tabs.Tab
            className="mt-4 grid grid-cols-2 gap-5 sm:grid-cols-3"
            label={t("Environments")}
          >
            <div></div>
          </Tabs.Tab>
          <Tabs.Tab
            className="mt-4 grid grid-cols-2 gap-5 sm:grid-cols-3"
            label={t("Version Control")}
          >
            <div></div>
          </Tabs.Tab>
          <Tabs.Tab
            className="mt-4 grid grid-cols-2 gap-5 sm:grid-cols-3"
            label={t("Policies")}
          >
            <div></div>
          </Tabs.Tab>
        </Tabs>
      </WorkspaceLayout.PageContent>
    </Page>
  );
};

WorkspaceSettingsPage.getLayout = (page, pageProps) => {
  return <WorkspaceLayout pageProps={pageProps}>{page}</WorkspaceLayout>;
};

export const getServerSideProps = createGetServerSideProps({
  requireAuth: true,
});

export default WorkspaceSettingsPage;
