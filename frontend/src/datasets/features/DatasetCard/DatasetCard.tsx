import { gql } from "@apollo/client";
import Card from "core/components/Card";
import Time from "core/components/Time";
import { DatasetCard_LinkFragment } from "datasets/features/DatasetCard/DatasetCard.generated";
import { Trans } from "next-i18next";

type DatasetCardProps = {
  link: DatasetCard_LinkFragment;
};

const DatasetCard = ({ link }: DatasetCardProps) => {
  const { dataset, workspace, id } = link;
  return (
    <Card
      href={{
        pathname: "/workspaces/[workspaceSlug]/datasets/[datasetSlug]",
        query: { workspaceSlug: workspace.slug, datasetSlug: dataset.slug },
      }}
      title={dataset.name}
      subtitle={dataset.workspace?.name}
    >
      <div className={"text-sm text-gray-400 mt-2 flex justify-between"}>
        <span>
          <Trans>
            Updated <Time datetime={dataset.updatedAt} relative />
          </Trans>
        </span>
      </div>
    </Card>
  );
};

DatasetCard.fragments = {
  link: gql`
    fragment DatasetCard_link on DatasetLink {
      dataset {
        name
        slug
        description
        updatedAt
        workspace {
          slug
          name
        }
      }
      id
      workspace {
        slug
        name
      }
    }
  `,
};

export default DatasetCard;
