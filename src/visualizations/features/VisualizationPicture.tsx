import { gql } from "@apollo/client";
import { VisualizationPicture_VisualizationFragment } from "./VisualizationPicture.generated";

type VisualizationPictureProps = {
  visualization: VisualizationPicture_VisualizationFragment;
};

const VisualizationPicture = (props: VisualizationPictureProps) => {
  const { visualization } = props;
  return (
    <div className="flex h-10 w-10 flex-shrink-0 items-center">
      <img
        className="h-10 w-10 rounded-full"
        alt=""
        src={visualization.pictureUrl}
      />
    </div>
  );
};

VisualizationPicture.fragments = {
  visualization: gql`
    fragment VisualizationPicture_visualization on ExternalDashboard {
      pictureUrl
    }
  `,
};

export default VisualizationPicture;
