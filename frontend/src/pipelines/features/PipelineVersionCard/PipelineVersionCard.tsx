import { gql, useMutation } from "@apollo/client";
import { ArrowDownTrayIcon, TrashIcon } from "@heroicons/react/24/outline";
import Badge from "core/components/Badge";
import Block from "core/components/Block";
import Button from "core/components/Button";
import DataCard from "core/components/DataCard";
import { OnSaveFn } from "core/components/DataCard/FormSection";
import RenderProperty from "core/components/DataCard/RenderProperty";
import TextProperty from "core/components/DataCard/TextProperty";
import Link from "core/components/Link";
import Spinner from "core/components/Spinner";
import Time from "core/components/Time";
import Input from "core/components/forms/Input";
import { isValidUrl } from "core/helpers";
import { ItemProvider } from "core/hooks/useItemContext";
import { UpdatePipelineVersionError } from "graphql/types";
import { DateTime } from "luxon";
import { Trans, useTranslation } from "next-i18next";
import DeletePipelineVersionTrigger from "workspaces/features/DeletePipelineVersionTrigger";
import DownloadPipelineVersion from "../DownloadPipelineVersion";
import PipelineVersionParametersTable from "../PipelineVersionParametersTable";
import {
  PipelineVersionCard_VersionFragment,
  UpdatePipelineVersionMutation,
  UpdatePipelineVersionMutationVariables,
} from "./PipelineVersionCard.generated";
import useFeature from "identity/hooks/useFeature";

type PipelineVersionCardProps = {
  version: PipelineVersionCard_VersionFragment;
  onClickRun?: () => void;
};

const PipelineVersionCard = (props: PipelineVersionCardProps) => {
  const { t } = useTranslation();
  const { version } = props;
  const [isPipelineTemplateFeatureEnabled] = useFeature("pipeline_templates");
  const [updateVersion] = useMutation<
    UpdatePipelineVersionMutation,
    UpdatePipelineVersionMutationVariables
  >(gql`
    mutation UpdatePipelineVersion($input: UpdatePipelineVersionInput!) {
      updatePipelineVersion(input: $input) {
        success
        errors
        pipelineVersion {
          ...PipelineVersionCard_version
        }
      }
    }
    ${PipelineVersionCard.fragments.version}
  `);

  const onSave: OnSaveFn = async (values) => {
    const { data } = await updateVersion({
      variables: {
        input: {
          id: version.id,
          ...values,
        },
      },
    });
    if (
      data?.updatePipelineVersion.errors?.includes(
        UpdatePipelineVersionError.PermissionDenied,
      )
    ) {
      throw new Error("You cannot update this version.");
    } else if (!data?.updatePipelineVersion.success) {
      throw new Error("An error occurred while updating the version.");
    }
  };

  const name = version.user?.displayName ?? t("someone");

  return (
    <ItemProvider item={version}>
      <Block className="divide-y-2 divide-gray-100">
        <Block.Header className="flex gap-4 items-center ">
          <div className="flex-1">
            <span className="font-bold text-xl">
              {t("Version")} {version.versionName}
            </span>{" "}
            <span className="text-gray-500">
              <Trans>
                created by {{ name }} on{" "}
                <Time datetime={version.createdAt} format={DateTime.DATE_MED} />
              </Trans>
            </span>
          </div>
          <div>
            {version.isLatestVersion && (
              <Badge className="ml-2 text-gray-500 text-sm ring-gray-300">
                {t("Latest version")}
              </Badge>
            )}
            {isPipelineTemplateFeatureEnabled && version.templateVersion && (
              <Badge className="ml-2 text-gray-500 text-sm ring-gray-300">
                {t("Template {{template}} (v{{version}})", {
                  template: version.templateVersion.template.name,
                  version: version.templateVersion.versionNumber,
                })}
              </Badge>
            )}
          </div>
        </Block.Header>
        <DataCard.FormSection
          title={t("Details")}
          onSave={version.permissions.update ? onSave : undefined}
          collapsible={false}
        >
          <TextProperty
            id="name"
            visible={(_, isEditing) => isEditing}
            label={t("Name")}
            accessor="name"
          />
          <RenderProperty
            id="externalLink"
            label={t("Link")}
            accessor="externalLink"
            visible={(value, isEditing) => Boolean(value) || isEditing}
            validate={(value) =>
              value && !isValidUrl(value) && t("Invalid URL")
            }
          >
            {(property, section) => (
              <>
                {section.isEdited ? (
                  <Input
                    name="externalLink"
                    fullWidth
                    type="url"
                    value={property.formValue}
                    onChange={(e) => property.setValue(e.target.value)}
                  />
                ) : (
                  <Link href={property.displayValue} target="_blank">
                    {property.displayValue}
                  </Link>
                )}
              </>
            )}
          </RenderProperty>
          <TextProperty
            id="description"
            label={t("Description")}
            accessor="description"
            sm
            markdown
          />
        </DataCard.FormSection>
        {version.parameters.length > 0 && (
          <Block.Section
            title={t("Parameters")}
            collapsible
            defaultOpen={false}
          >
            <div className="rounded-md overflow-hidden border border-gray-100">
              <PipelineVersionParametersTable version={version} />
            </div>
          </Block.Section>
        )}
        <Block.Section>
          <div className="flex justify-end items-center gap-2">
            <DeletePipelineVersionTrigger version={version}>
              {({ onClick }) => (
                <Button
                  leadingIcon={<TrashIcon className="h-4 w-4" />}
                  variant="danger"
                  onClick={onClick}
                >
                  {t("Delete")}
                </Button>
              )}
            </DeletePipelineVersionTrigger>
            <DownloadPipelineVersion version={version}>
              {({ isDownloading, onClick }) => (
                <Button
                  leadingIcon={<ArrowDownTrayIcon className="w-4 h-4" />}
                  onClick={onClick}
                >
                  {isDownloading && <Spinner size="xs" className="mr-1" />}
                  {t("Download")}
                </Button>
              )}
            </DownloadPipelineVersion>
          </div>
        </Block.Section>
      </Block>
    </ItemProvider>
  );
};

PipelineVersionCard.fragments = {
  version: gql`
    fragment PipelineVersionCard_version on PipelineVersion {
      id
      versionName
      name
      description
      externalLink
      isLatestVersion
      createdAt
      user {
        displayName
      }
      permissions {
        update
      }
      parameters {
        code
        name
        type
        multiple
        required
        help
      }
      pipeline {
        id
        code
      }
      templateVersion {
        id
        versionNumber
        template {
          id
          name
        }
      }
      ...DownloadPipelineVersion_version
      ...DeletePipelineVersionTrigger_version
    }
    ${DownloadPipelineVersion.fragments.version}
    ${DeletePipelineVersionTrigger.fragments.version}
  `,
};

export default PipelineVersionCard;
