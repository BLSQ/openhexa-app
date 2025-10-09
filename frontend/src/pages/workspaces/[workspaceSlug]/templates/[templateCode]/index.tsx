import DataCard from "core/components/DataCard";
import TextProperty from "core/components/DataCard/TextProperty";
import TagProperty from "core/components/DataCard/TagProperty";
import SelectProperty from "core/components/DataCard/SelectProperty";
import Page from "core/components/Page";
import { createGetServerSideProps } from "core/helpers/page";
import { NextPageWithLayout } from "core/helpers/types";
import { useTranslation } from "next-i18next";
import { useWorkspaceTemplatePageQuery } from "workspaces/graphql/queries.generated";
import TemplateLayout from "workspaces/layouts/TemplateLayout";
import { updateTemplate } from "workspaces/helpers/templates";
import Link from "core/components/Link";
import RenderProperty from "core/components/DataCard/RenderProperty";
import MarkdownProperty from "core/components/DataCard/MarkdownProperty";
import { createTemplatePageServerSideProps } from "workspaces/helpers/templatePages";
import { PipelineFunctionalType } from "graphql/types";
import { formatPipelineFunctionalType } from "workspaces/helpers/pipelines";

type Props = {
  templateCode: string;
  workspaceSlug: string;
};

const WorkspaceTemplatePage: NextPageWithLayout = (props: Props) => {
  const { templateCode, workspaceSlug } = props;
  const { t } = useTranslation();

  const { data } = useWorkspaceTemplatePageQuery({
    variables: {
      workspaceSlug,
      templateCode,
    },
  });

  if (!data?.workspace || !data?.template) {
    return null;
  }

  const { workspace, template } = data;

  const onSaveTemplate = async (values: any) => {
    await updateTemplate(template.id, {
      name: values.name,
      description: values.description,
      tags: values.tags?.map((tag: any) => tag.name) || [],
      functionalType: values.functionalType,
    });
  };

  return (
    <Page title={template.name}>
      <TemplateLayout workspace={workspace} template={template}>
        <DataCard.FormSection
          title={t("Information")}
          onSave={template.permissions.update ? onSaveTemplate : undefined}
          collapsible={false}
        >
          <TextProperty
            id="name"
            accessor={"name"}
            label={t("Name")}
            visible={(value, isEditing) => isEditing}
          />
          <MarkdownProperty
            id="description"
            label="Description"
            accessor={"description"}
          />
          <TagProperty
            id="tags"
            accessor="tags"
            label={t("Tags")}
            defaultValue={t("Not set")}
          />
          <SelectProperty
            id="functionalType"
            accessor="functionalType"
            label={t("Type")}
            help={t("The functional purpose of this template")}
            options={Object.values(PipelineFunctionalType)}
            getOptionLabel={(option) => option ? formatPipelineFunctionalType(option) : t("Not set")}
            nullable
            defaultValue={t("Not set")}
            className="max-w-xs"
          />
          <RenderProperty
            id="version_name"
            accessor={"currentVersion"}
            label={t("Version")}
            readonly
          >
            {(property) => (
              <div className="flex items-center gap-3">
                <Link
                  href={`/workspaces/${encodeURIComponent(
                    workspace.slug,
                  )}/templates/${encodeURIComponent(template.code)}/versions`}
                >
                  {property.displayValue
                    ? property.displayValue.versionNumber
                    : t("No version yet")}
                </Link>
              </div>
            )}
          </RenderProperty>
        </DataCard.FormSection>
      </TemplateLayout>
    </Page>
  );
};

WorkspaceTemplatePage.getLayout = (page) => page;

export const getServerSideProps = createGetServerSideProps(
  createTemplatePageServerSideProps(),
);

export default WorkspaceTemplatePage;
