import { gql, useMutation } from "@apollo/client";
import { TrashIcon } from "@heroicons/react/24/outline";
import Badge from "core/components/Badge";
import Block from "core/components/Block";
import Button from "core/components/Button";
import DataCard from "core/components/DataCard";
import TextProperty from "core/components/DataCard/TextProperty";
import Time from "core/components/Time";
import { ItemProvider } from "core/hooks/useItemContext";
import { DateTime } from "luxon";
import { Trans, useTranslation } from "next-i18next";
import DeleteTemplateVersionTrigger from "workspaces/features/DeleteTemplateVersionTrigger";
import {
  TemplateVersionCard_VersionFragment,
  UpdateTemplateVersionMutation,
  UpdateTemplateVersionMutationVariables,
} from "./TemplateVersionCard.generated";
import { OnSaveFn } from "core/components/DataCard/FormSection";
import { UpdateTemplateVersionError } from "graphql/types";

type TemplateVersionCardProps = {
  version: TemplateVersionCard_VersionFragment;
  onClickRun?: () => void;
};

const TemplateVersionCard = (props: TemplateVersionCardProps) => {
  const { t } = useTranslation();
  const { version } = props;
  const [updateVersion] = useMutation<
    UpdateTemplateVersionMutation,
    UpdateTemplateVersionMutationVariables
  >(gql`
    mutation UpdateTemplateVersion($input: UpdateTemplateVersionInput!) {
      updateTemplateVersion(input: $input) {
        success
        errors
        templateVersion {
          ...TemplateVersionCard_version
        }
      }
    }
    ${TemplateVersionCard.fragments.version}
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
      data?.updateTemplateVersion.errors?.includes(
        UpdateTemplateVersionError.PermissionDenied,
      )
    ) {
      throw new Error("You cannot update this version.");
    } else if (!data?.updateTemplateVersion.success) {
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
              {t("Version")} {version.versionNumber}
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
          </div>
        </Block.Header>
        <DataCard.FormSection
          title={t("Details")}
          onSave={version.permissions.update ? onSave : undefined}
          collapsible={false}
        >
          <TextProperty
            id="changelog"
            label={t("Changelog")}
            accessor="changelog"
            sm
            markdown
          />
        </DataCard.FormSection>
        <Block.Section>
          <div className="flex justify-end items-center gap-2">
            <DeleteTemplateVersionTrigger version={version}>
              {({ onClick }) => (
                <Button
                  leadingIcon={<TrashIcon className="h-4 w-4" />}
                  variant="danger"
                  onClick={onClick}
                >
                  {t("Delete")}
                </Button>
              )}
            </DeleteTemplateVersionTrigger>
          </div>
        </Block.Section>
      </Block>
    </ItemProvider>
  );
};

TemplateVersionCard.fragments = {
  version: gql`
    fragment TemplateVersionCard_version on PipelineTemplateVersion {
      id
      versionNumber
      changelog
      createdAt
      isLatestVersion
      user {
        displayName
      }
      permissions {
        update
      }
      template {
        id
        code
      }
      ...DeleteTemplateVersionTrigger_version
    }
    ${DeleteTemplateVersionTrigger.fragments.version}
  `,
};

export default TemplateVersionCard;
