import { render, screen } from "@testing-library/react";
import PipelineRunFavoriteIcon from "./PipelineRunFavoriteIcon";

describe("PipelineRunFavoriteIcon", () => {
  it("renders the icon in yellow when it is favorite", async () => {
    const { container, baseElement } = render(
      <PipelineRunFavoriteIcon
        run={{
          isFavorite: true,
        }}
      />,
    );

    expect(screen.getByTestId("favorite-icon")).toHaveClass("fill-yellow-300");
    expect(screen.getByTestId("favorite-icon")).not.toHaveClass(
      "stroke-gray-300",
    );
  });

  it("renders the icon in gray when it is not favorite", async () => {
    const { container, baseElement } = render(
      <PipelineRunFavoriteIcon
        run={{
          isFavorite: false,
        }}
      />,
    );

    expect(screen.getByTestId("favorite-icon")).not.toHaveClass(
      "fill-yellow-300",
    );
    expect(screen.getByTestId("favorite-icon")).toHaveClass("stroke-gray-300");
  });

  it("accepts a different size", async () => {
    const { container, baseElement } = render(
      <PipelineRunFavoriteIcon
        sizeClassName="w-12 h-12"
        run={{
          isFavorite: false,
        }}
      />,
    );

    expect(screen.getByTestId("favorite-icon")).not.toHaveClass("h-6 w-6");
    expect(screen.getByTestId("favorite-icon")).toHaveClass("w-12 h-12");
  });

  it("adds classes when animated", async () => {
    const { container } = render(
      <PipelineRunFavoriteIcon
        animate
        run={{
          isFavorite: false,
        }}
      />,
    );
    expect(container).toMatchSnapshot();
  });
});
