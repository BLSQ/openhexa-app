import { gql } from "@apollo/client";
import ShareButton from "core/features/Sharing/ShareButton";
import useDatasetShareDialog from "datasets/features/DatasetSharing/useDatasetShareDialog";
import { DatasetShareButton_DatasetFragment } from "./DatasetShareButton.generated";

type DatasetShareButtonProps = {
  dataset: DatasetShareButton_DatasetFragment;
};

const DatasetShareButton = ({ dataset }: DatasetShareButtonProps) => {
  const dialog = useDatasetShareDialog(dataset);
  return dataset.permissions.update ? <ShareButton {...dialog} /> : null;
};

DatasetShareButton.fragments = {
  dataset: gql`
    fragment DatasetShareButton_dataset on Dataset {
      id
      slug
      publicSlug
      visibility
      permissions {
        update
        share
      }
    }
  `,
};

export default DatasetShareButton;
