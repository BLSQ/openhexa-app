import { useQuery } from "@apollo/client";
import { faker } from "@faker-js/faker";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import DatasetPicker from "./DatasetPicker";

jest.mock("@apollo/client", () => ({
  __esModule: true,
  useQuery: jest.fn(),
  gql: jest.fn(() => "GQL"),
}));

const useQueryMock = useQuery as jest.Mock;

const WORKSPACE = {
  slug: faker.string.uuid(),
  datasets: {
    items: [
      {
        id: faker.string.uuid(),
        dataset: {
          slug: faker.lorem.slug(5),
          name: "Dataset 1",
        },
      },
      {
        id: faker.string.uuid(),
        dataset: {
          slug: faker.lorem.slug(5),
          name: "Dataset 2",
        },
      },
    ],
  },
};

describe("DatasetPicker", () => {
  it("display all dataset", async () => {
    const user = userEvent.setup();
    useQueryMock.mockReturnValue({
      loading: true,
      data: {
        workspace: WORKSPACE,
      },
    });
    const onChange = jest.fn();

    const { container } = render(
      <DatasetPicker
        workspaceSlug={WORKSPACE.slug}
        onChange={onChange}
        value={""}
      />,
    );

    const items = WORKSPACE.datasets.items;

    await user.click(await screen.findByTestId("combobox-button"));
    const option = await screen.queryAllByRole("option");
    expect(option.length).toBe(items.length);

    expect(container).toMatchSnapshot();
  });
});
