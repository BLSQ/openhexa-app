import Block from "core/components/Block";
import Breadcrumbs from "core/components/Breadcrumbs";
import CodeEditor from "core/components/CodeEditor";
import DataGrid from "core/components/DataGrid";
import Page from "core/components/Page";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
} from "core/components/Table";
import Tabs from "core/components/Tabs";
import Title from "core/components/Title";
import { createGetServerSideProps } from "core/helpers/page";
import { NextPageWithLayout } from "core/helpers/types";
import { capitalize } from "lodash";
import { useTranslation } from "next-i18next";
import { useRouter } from "next/router";
import { WORKSPACES } from "workspaces/helpers/fixtures";
import WorkspaceLayout from "workspaces/layouts/WorkspaceLayout";

type Props = {
  page: number;
  perPage: number;
};

const WorkspacePipelinePage: NextPageWithLayout = (props: Props) => {
  const { t } = useTranslation();
  const router = useRouter();
  const workspace = WORKSPACES.find((w) => w.id === router.query.workspaceId);

  if (!workspace) {
    return null;
  }

  const connection = workspace.connections.find(
    (c) => c.id === router.query.connectionId
  );
  if (!connection) {
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
          <Breadcrumbs.Part
            href={`/workspaces/${encodeURIComponent(workspace.id)}/connections`}
          >
            {t("Connections")}
          </Breadcrumbs.Part>
          <Breadcrumbs.Part
            href={`/workspaces/${encodeURIComponent(
              workspace.id
            )}/pipelines/${encodeURIComponent(connection.id)}`}
          >
            {connection.name}
          </Breadcrumbs.Part>
        </Breadcrumbs>
      </WorkspaceLayout.Header>
      <WorkspaceLayout.PageContent>
        <div className="space-y-1">
          <div
            className="text-lg font-medium text-gray-900"
            title={connection.name}
          >
            {capitalize(connection.name)}
          </div>
          <div className="text-sm text-gray-700">
            <span>{connection.type}</span>
          </div>
          <div className="h-10 text-sm italic text-gray-600">
            <span>
              {t("This Data source is owned by ")}
              {connection.owner}
            </span>
          </div>
        </div>
        <Block className="mt-2 p-4">
          <Tabs defaultIndex={0}>
            <Tabs.Tab className="mt-4" label={t("Information")}>
              <div>
                <Title level={5} className="font-medium ">
                  {t("Usage")}
                </Title>
                <p className="text-sm text-gray-600">
                  {connection.description}
                </p>
              </div>
            </Tabs.Tab>
            <Tabs.Tab className="mt-4 " label={t("Code samples")}>
              <div className="mt-5">
                <CodeEditor
                  readonly
                  lang="json"
                  value={workspace.database.workspaceTables[0].codeSample[0]}
                />
              </div>
            </Tabs.Tab>
            <Tabs.Tab className="mt-4" label={t("Variables")}>
              <div className="mt-5">
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell> {t("Name")} </TableCell>
                      <TableCell>{t("Value")}</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {Object.entries(connection.credentials).map(
                      ([key, value]) => (
                        <TableRow key={key}>
                          <TableCell className="font-medium text-gray-800">
                            {key}
                          </TableCell>
                          <TableCell>{value}</TableCell>
                        </TableRow>
                      )
                    )}
                  </TableBody>
                </Table>
              </div>
            </Tabs.Tab>
          </Tabs>
        </Block>
      </WorkspaceLayout.PageContent>
    </Page>
  );
};

WorkspacePipelinePage.getLayout = (page, pageProps) => {
  return <WorkspaceLayout pageProps={pageProps}>{page}</WorkspaceLayout>;
};

export const getServerSideProps = createGetServerSideProps({
  requireAuth: true,
});

export default WorkspacePipelinePage;
