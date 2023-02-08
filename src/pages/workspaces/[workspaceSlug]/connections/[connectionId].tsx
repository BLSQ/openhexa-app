import Badge from "core/components/Badge";
import Block from "core/components/Block";
import Breadcrumbs from "core/components/Breadcrumbs";
import Button from "core/components/Button";
import CodeEditor from "core/components/CodeEditor";
import DescriptionList from "core/components/DescriptionList";
import Page from "core/components/Page";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
} from "core/components/Table";
import { createGetServerSideProps } from "core/helpers/page";
import { NextPageWithLayout } from "core/helpers/types";
import { useTranslation } from "next-i18next";
import { useRouter } from "next/router";
import ReactMarkdown from "react-markdown";
import {
  useWorkspaceConnectionPageQuery,
  WorkspaceConnectionsPageDocument,
} from "workspaces/graphql/queries.generated";
import { FAKE_WORKSPACE } from "workspaces/helpers/fixtures";
import WorkspaceLayout from "workspaces/layouts/WorkspaceLayout";

type Props = {
  page: number;
  perPage: number;
};

const WorkspacePipelinePage: NextPageWithLayout = (props: Props) => {
  const { t } = useTranslation();
  const router = useRouter();
  const { data } = useWorkspaceConnectionPageQuery({
    variables: { workspaceSlug: router.query.workspaceSlug as string },
  });

  if (!data?.workspace) {
    return null;
  }
  const { workspace } = data;

  const connection = FAKE_WORKSPACE.connections.find(
    (t) => t.id === router.query.connectionId
  );

  if (!connection) {
    return null;
  }

  return (
    <Page title={t("Workspace")}>
      <WorkspaceLayout.Header className="flex items-center justify-between">
        <Breadcrumbs withHome={false}>
          <Breadcrumbs.Part
            isFirst
            href={`/workspaces/${encodeURIComponent(workspace.slug)}`}
          >
            {workspace.name}
          </Breadcrumbs.Part>
          <Breadcrumbs.Part
            href={`/workspaces/${encodeURIComponent(
              workspace.slug
            )}/connections`}
          >
            {t("Connections")}
          </Breadcrumbs.Part>
          <Breadcrumbs.Part
            isLast
            href={`/workspaces/${encodeURIComponent(
              workspace.slug
            )}/pipelines/${encodeURIComponent(connection.id)}`}
          >
            {connection.name}
          </Breadcrumbs.Part>
        </Breadcrumbs>
        <Button>{t("Edit")}</Button>
      </WorkspaceLayout.Header>
      <WorkspaceLayout.PageContent>
        <Block className="divide-y-2 divide-gray-100">
          <Block.Content title={t("Information")} className="space-y-4">
            <DescriptionList>
              <DescriptionList.Item label={t("Type")}>
                <Badge className={connection.type.color}>
                  {connection.type?.label ?? "custom"}
                </Badge>
              </DescriptionList.Item>
            </DescriptionList>
            <ReactMarkdown className="prose text-sm">
              {connection.description}
            </ReactMarkdown>
          </Block.Content>
          <Block.Section title={t("Code samples")}>
            <CodeEditor
              readonly
              lang="json"
              value={FAKE_WORKSPACE.database.workspaceTables[0].codeSample[0]}
            />
          </Block.Section>
          <Block.Section title={t("Variables")}>
            <div className="overflow-hidden rounded border border-gray-100">
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell className="py-3">{t("Name")}</TableCell>
                    <TableCell className="py-3">{t("Value")}</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {connection.credentials.map((creds, index) => (
                    <TableRow key={index}>
                      <TableCell className="py-3 font-medium">
                        {creds.label}
                      </TableCell>
                      <TableCell className="py-3">
                        {creds.secret ? "***********" : creds.value}
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </div>
          </Block.Section>
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
  async getServerSideProps(ctx, client) {
    const { data } = await client.query({
      query: WorkspaceConnectionsPageDocument,
      variables: { workspaceSlug: ctx.params?.workspaceSlug },
    });

    if (!data.workspace) {
      return {
        notFound: true,
      };
    }
  },
});

export default WorkspacePipelinePage;
