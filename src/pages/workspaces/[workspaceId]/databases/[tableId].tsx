import { EyeIcon } from "@heroicons/react/24/outline";
import Block from "core/components/Block";
import Breadcrumbs from "core/components/Breadcrumbs";
import Button from "core/components/Button";
import CodeEditor from "core/components/CodeEditor";
import DataGrid from "core/components/DataGrid";
import { TextColumn } from "core/components/DataGrid/TextColumn";
import DescriptionList from "core/components/DescriptionList";
import Dialog from "core/components/Dialog";
import Page from "core/components/Page";
import Tabs from "core/components/Tabs";
import Time from "core/components/Time";
import { createGetServerSideProps } from "core/helpers/page";
import { NextPageWithLayout } from "core/helpers/types";
import { capitalize } from "lodash";
import { useTranslation } from "next-i18next";
import { useRouter } from "next/router";
import { ReactNode, useState } from "react";
import {
  useWorkspaceDatabaseTablePageQuery,
  WorkspaceDatabaseTablePageDocument,
} from "workspaces/graphql/queries.generated";
import { FAKE_WORKSPACE } from "workspaces/helpers/fixtures";
import WorkspaceLayout from "workspaces/layouts/WorkspaceLayout";

const DataPreviewModal = ({
  open,
  content,
  onClose,
}: {
  open: boolean;
  content: ReactNode;
  onClose: () => void;
}) => {
  const { t } = useTranslation();
  return (
    <Dialog open={open} onClose={onClose} maxWidth="max-w-3xl" centered={false}>
      <Dialog.Title>{t("Preview Data")}</Dialog.Title>
      <Dialog.Content>{content}</Dialog.Content>
      <Dialog.Actions>
        <Button onClick={onClose}>{t("Close")}</Button>
      </Dialog.Actions>
    </Dialog>
  );
};

type Props = {
  page: number;
  perPage: number;
};

const WorkspaceDatabaseTableViewPage: NextPageWithLayout = (props: Props) => {
  const { t } = useTranslation();
  const [openModal, setOpenModal] = useState(false);
  const router = useRouter();
  const { data } = useWorkspaceDatabaseTablePageQuery({
    variables: { workspaceId: router.query.workspaceId as string },
  });

  if (!data?.workspace) {
    return null;
  }
  const { workspace } = data;

  const table = FAKE_WORKSPACE.database.workspaceTables.find(
    (t) => t.id === router.query.tableId
  );
  if (!table) {
    return null;
  }

  const handleOpenModal = () => {
    setOpenModal(!openModal);
  };

  return (
    <Page title={t("Workspace")}>
      <WorkspaceLayout.Header className="flex items-center justify-between">
        <Breadcrumbs withHome={false}>
          <Breadcrumbs.Part
            isFirst
            href={`/workspaces/${encodeURIComponent(workspace.id)}`}
          >
            {workspace.name}
          </Breadcrumbs.Part>
          <Breadcrumbs.Part
            href={`/workspaces/${encodeURIComponent(workspace.id)}/databases`}
          >
            {t("Database")}
          </Breadcrumbs.Part>
          <Breadcrumbs.Part
            isLast
            href={`/workspaces/${encodeURIComponent(workspace.id)}/databases/${
              router.query.tableId
            }`}
          >
            {capitalize(table.name)}
          </Breadcrumbs.Part>
        </Breadcrumbs>
        <div className="flex items-center gap-2">
          <Button
            onClick={handleOpenModal}
            leadingIcon={<EyeIcon className="w-4" />}
          >
            {t("Preview data")}
          </Button>
        </div>
      </WorkspaceLayout.Header>
      <WorkspaceLayout.PageContent className="space-y-4">
        <Block className="divide-y-2 divide-gray-100">
          <Block.Content title={t("Definition")}>
            <DataGrid
              data={table.schema}
              fixedLayout={false}
              className="w-3/4 max-w-lg rounded-md border"
            >
              <TextColumn
                className="py-3 font-mono"
                textClassName="bg-gray-50 py-1 px-2"
                name="field"
                label="Field"
                accessor="fieldName"
              />
              <TextColumn
                className="py-3"
                name="type"
                label="Type"
                accessor="type"
              />
            </DataGrid>
          </Block.Content>
          <Block.Content>
            <DescriptionList>
              <DescriptionList.Item label={t("Created at")}>
                <Time datetime={table.createdAt} />
              </DescriptionList.Item>
            </DescriptionList>
          </Block.Content>
          <Block.Section title={"Usage"}>
            <Tabs defaultIndex={0}>
              <Tabs.Tab label={t("Code")}>
                <CodeEditor readonly lang="json" value={table.codeSample[0]} />
              </Tabs.Tab>
              <Tabs.Tab label={t("Use in BI tools")}>
                <CodeEditor readonly lang="json" value={table.codeSample[1]} />
              </Tabs.Tab>
            </Tabs>
          </Block.Section>
          <DataPreviewModal
            open={openModal}
            onClose={() => setOpenModal(!openModal)}
            content={
              <DataGrid
                data={table.schema}
                fixedLayout={false}
                className="mt-4"
              >
                {table.schema.map((s, index) => (
                  <TextColumn
                    key={index}
                    className="py-3 font-medium"
                    name={s.fieldName}
                    label={s.fieldName}
                    accessor="sample"
                  />
                ))}
              </DataGrid>
            }
          />
        </Block>
      </WorkspaceLayout.PageContent>
    </Page>
  );
};

WorkspaceDatabaseTableViewPage.getLayout = (page, pageProps) => {
  return <WorkspaceLayout pageProps={pageProps}>{page}</WorkspaceLayout>;
};

export const getServerSideProps = createGetServerSideProps({
  requireAuth: true,
  async getServerSideProps(ctx, client) {
    const { data } = await client.query({
      query: WorkspaceDatabaseTablePageDocument,
      variables: { workspaceId: ctx.params?.workspaceId },
    });

    if (!data.workspace) {
      return {
        notFound: true,
      };
    }
  },
});

export default WorkspaceDatabaseTableViewPage;
