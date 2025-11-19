import DataCard from "core/components/DataCard";
import TextProperty from "core/components/DataCard/TextProperty";
import TagProperty from "core/components/DataCard/TagProperty";
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
import Listbox from "core/components/Listbox";
import TemplateBadge from "pipelines/features/TemplateBadge";

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

  const pipelineFunctionalTypeOptions = [
    { value: null, label: t("Not set") },
    ...Object.values(PipelineFunctionalType).map((type) => ({
      value: type,
      label: formatPipelineFunctionalType(type),
    })),
  ];

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
          <RenderProperty
            id="organization"
            accessor="organization.name"
            label={t("Publisher")}
            readonly
          >
            {() => (
              <TemplateBadge
                organization={template.organization}
                validatedAt={template.validatedAt}
              />
            )}
          </RenderProperty>
          <TagProperty
            id="tags"
            accessor="tags"
            label={t("Tags")}
            defaultValue={t("Not set")}
          />
          <RenderProperty
            id="functionalType"
            accessor="functionalType"
            label={t("Type")}
            help={t("The functional purpose of this template")}
          >
            {(property, section) =>
              section.isEdited ? (
                <div className="w-50">
                  <Listbox
                    value={
                      pipelineFunctionalTypeOptions.find(
                        (opt) => opt.value === property.formValue,
                      ) || pipelineFunctionalTypeOptions[0]
                    }
                    options={pipelineFunctionalTypeOptions}
                    onChange={(option) => property.setValue(option.value)}
                    getOptionLabel={(opt) => opt.label}
                    by="value"
                  />
                </div>
              ) : (
                <span>
                  {property.displayValue
                    ? formatPipelineFunctionalType(property.displayValue)
                    : t("Not set")}
                </span>
              )
            }
          </RenderProperty>
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
