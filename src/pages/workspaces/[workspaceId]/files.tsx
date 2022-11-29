import SearchInput from "catalog/features/SearchInput";
import Block from "core/components/Block";
import Breadcrumbs from "core/components/Breadcrumbs";
import DataGrid, { BaseColumn } from "core/components/DataGrid";
import DateColumn from "core/components/DataGrid/DateColumn";
import { TextColumn } from "core/components/DataGrid/TextColumn";
import Filesize from "core/components/Filesize";
import Page from "core/components/Page";
import Title from "core/components/Title";
import { createGetServerSideProps } from "core/helpers/page";
import { NextPageWithLayout } from "core/helpers/types";
import { useTranslation } from "next-i18next";
import { useRouter } from "next/router";
import { WORKSPACES } from "workspaces/helpers/fixtures";
import WorkspaceLayout from "workspaces/layouts/WorkspaceLayout";

type Props = {
  page: number;
  perPage: number;
};

const WorkspaceFilesPage: NextPageWithLayout = (props: Props) => {
  const { t } = useTranslation();
  const router = useRouter();
  const workspace = WORKSPACES.find((w) => w.id === router.query.workspaceId);

  if (!workspace) {
    return null;
  }
  console.log(workspace);

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
            href={`/workspaces/${encodeURIComponent(workspace.id)}/files`}
          >
            {t("Files")}
          </Breadcrumbs.Part>
        </Breadcrumbs>
      </WorkspaceLayout.Header>
      <WorkspaceLayout.PageContent className="space-y-8">
        <div className="flex flex-1 items-center justify-between">
          <Title level={2} className="mb-0">
            Files
          </Title>
          <div>
            <SearchInput className="w-72" onChange={() => {}} />
          </div>
        </div>
        <div>
          <Title level={5}>Workspace files</Title>
          <DataGrid
            className="bg-white shadow"
            data={workspace.files}
            defaultPageSize={5}
            sortable
            totalItems={workspace.files.length}
            fixedLayout={false}
          >
            <TextColumn
              className="max-w-[50ch] py-3 "
              textClassName="font-medium text-gray-600 cursor-pointer"
              accessor="name"
              id="name"
              label="Name"
            />
            <TextColumn
              className="py-3"
              accessor="type"
              id="type"
              label="Type"
            />
            <BaseColumn accessor="size" id="size" label="Size" className="py-3">
              {(value) => <Filesize size={value} />}
            </BaseColumn>
            <DateColumn
              className="py-3"
              relative
              accessor="updatedAt"
              id="updatedAt"
              label="Last modified"
            />
          </DataGrid>
        </div>

        <div>
          <Title level={5}>Shared files</Title>
          <DataGrid
            className="bg-white shadow-md"
            data={workspace.sharedFiles}
            defaultPageSize={5}
            sortable
            totalItems={workspace.sharedFiles.length}
            fixedLayout={false}
          >
            <TextColumn
              textClassName="font-medium text-gray-600 cursor-pointer"
              className="max-w-[50ch] py-3"
              accessor="name"
              id="name"
              label="Name"
            />
            <TextColumn
              accessor="type"
              className="py-3"
              id="type"
              label="Type"
            />
            <BaseColumn accessor="size" id="size" label="Size" className="py-3">
              {(value) => <Filesize size={value} />}
            </BaseColumn>
            <DateColumn
              className="py-3"
              relative
              accessor="updatedAt"
              id="updatedAt"
              label="Last modified"
            />
            <TextColumn
              accessor="origin"
              id="origin"
              label="Origin"
              className="py-3"
            />
          </DataGrid>
        </div>
      </WorkspaceLayout.PageContent>
    </Page>
  );
};

WorkspaceFilesPage.getLayout = (page, pageProps) => {
  return <WorkspaceLayout pageProps={pageProps}>{page}</WorkspaceLayout>;
};

export const getServerSideProps = createGetServerSideProps({
  requireAuth: true,
});

export default WorkspaceFilesPage;
