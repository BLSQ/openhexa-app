import { gql } from "@apollo/client";
import { ArrowDownTrayIcon } from "@heroicons/react/24/outline";
import Badge from "core/components/Badge";
import Block from "core/components/Block";
import Button from "core/components/Button";
import DescriptionList from "core/components/DescriptionList";
import Spinner from "core/components/Spinner";
import Time from "core/components/Time";
import { DateTime } from "luxon";
import { Trans, useTranslation } from "next-i18next";
import DownloadPipelineVersion from "../DownloadPipelineVersion";
import PipelineVersionParametersTable from "../PipelineVersionParametersTable";
import { PipelineVersionCard_VersionFragment } from "./PipelineVersionCard.generated";

type PipelineVersionCardProps = {
  version: PipelineVersionCard_VersionFragment;
  onClickRun?: () => void;
};

const PipelineVersionCard = ({
  version,
  onClickRun,
}: PipelineVersionCardProps) => {
  const { t } = useTranslation();
  return (
    <Block className="mb-4 divide-y-2 divide-gray-100">
      <Block.Header className="flex">
        <div className="flex-1">
          <span className="font-bold text-xl">
            {t("Version")} {version.number}
          </span>{" "}
          <span className="text-gray-400">
            <Trans>
              on{" "}
              <span>
                <Time datetime={version.createdAt} format={DateTime.DATE_MED} />
              </span>
            </Trans>
          </span>
        </div>
        {version.isLatestVersion && (
          <Badge
            className="ml-2 text-gray-500 text-sm"
            borderColor="border-gray-300"
          >
            {t("Latest version")}
          </Badge>
        )}
      </Block.Header>
      <Block.Content>
        <DescriptionList>
          <DescriptionList.Item label={t("Identifier")}>
            <code>{version.number}</code>
          </DescriptionList.Item>
          <DescriptionList.Item label={t("Created at")}>
            <Time datetime={version.createdAt} />
          </DescriptionList.Item>
          <DescriptionList.Item label={t("Created by")}>
            {version.user?.displayName ?? "-"}
          </DescriptionList.Item>
        </DescriptionList>
      </Block.Content>
      {version.parameters.length > 0 && (
        <Block.Section title={t("Parameters")} collapsible={false}>
          <div className="rounded-md overflow-hidden border border-gray-100">
            <PipelineVersionParametersTable version={version} />
          </div>
        </Block.Section>
      )}
      <Block.Section>
        <div className="flex justify-end items-center gap-2">
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
  );
};

PipelineVersionCard.fragments = {
  version: gql`
    fragment PipelineVersionCard_version on PipelineVersion {
      id
      number
      isLatestVersion
      createdAt

      user {
        displayName
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
      ...DownloadPipelineVersion_version
    }
    ${DownloadPipelineVersion.fragments.version}
  `,
};

export default PipelineVersionCard;
