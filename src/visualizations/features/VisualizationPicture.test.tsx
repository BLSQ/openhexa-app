import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import VisualizationPicture from "../features/VisualizationPicture";
import { VisualizationPicture_VisualizationFragment } from "./VisualizationPicture.generated";

describe("VisualizationPicture", () => {
  const visualization = {
    pictureUrl:
      "https://www.bluesquarehub.com/wp-content/uploads/2021/07/logosvg-white.svg",
  };
  it("renders properly", () => {
    const { container: visualizationComponent } = render(
      <VisualizationPicture visualization={visualization} />,
    );
    expect(visualizationComponent).toMatchSnapshot();
  });
});
