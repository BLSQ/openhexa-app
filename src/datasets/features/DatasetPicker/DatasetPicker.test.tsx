import DatasetPicker from "./DatasetPicker";
import { queryByRole, render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MockedProvider } from "@apollo/client/testing";
import { faker } from "@faker-js/faker";
import { useQuery } from "@apollo/client";
import { ConnectionType } from "graphql-types";

jest.mock("@apollo/client", () => ({
  __esModule: true,
  useQuery: jest.fn(),
  gql: jest.fn(() => "GQL"),
}));

const useQueryMock = useQuery as jest.Mock;

const WORKSPACE = {
  slug: faker.datatype.uuid(),
  datasets: {
    items: [
      {
        id: faker.datatype.uuid(),
        dataset: {
          slug: faker.lorem.slug(5),
          name: faker.datatype.string(10),
        },
      },
      {
        id: faker.datatype.uuid(),
        dataset: {
          slug: faker.lorem.slug(5),
          name: faker.datatype.string(10),
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

    await user.click(await screen.findByText(items[0].dataset.name));
    expect(onChange).toHaveBeenCalledWith(items[0]);
    expect(container).toMatchSnapshot();
  });
});
