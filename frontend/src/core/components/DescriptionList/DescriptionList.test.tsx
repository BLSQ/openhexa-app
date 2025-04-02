import DescriptionList from "./DescriptionList";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { DescriptionListDisplayMode } from "./helpers";

describe("DescriptionList", () => {
  it("renders a list with one item", async () => {
    const { container } = render(
      <DescriptionList>
        <DescriptionList.Item label="label">value</DescriptionList.Item>
      </DescriptionList>,
    );

    expect(screen.getByText("label")).toBeInTheDocument();
    expect(screen.getByText("value")).toBeInTheDocument();

    expect(container).toMatchSnapshot();
  });

  it("renders the list on multiple columns", () => {
    const { container } = render(
      <DescriptionList columns={2}>
        <DescriptionList.Item label="label 1">value 1</DescriptionList.Item>
        <DescriptionList.Item label="label 2">value 2</DescriptionList.Item>
      </DescriptionList>,
    );

    const element = container.getElementsByTagName("dl")[0];

    expect(element).toHaveClass("grid-cols-2");
    expect(container).toMatchSnapshot();
  });

  it("renders the list with the label above the value", () => {
    const { container } = render(
      <DescriptionList
        columns={2}
        displayMode={DescriptionListDisplayMode.LABEL_ABOVE}
      >
        <DescriptionList.Item label="label 1">value 1</DescriptionList.Item>
        <DescriptionList.Item label="label 2">value 2</DescriptionList.Item>
      </DescriptionList>,
    );

    const element = container.getElementsByTagName("dl")[0];

    expect(element).toHaveClass("grid-cols-2");

    const items = container.getElementsByTagName("dt");
    Array.from(items).forEach((item) => {
      expect(item).toHaveClass("col-span-5");
    });
    expect(container).toMatchSnapshot();
  });
});
