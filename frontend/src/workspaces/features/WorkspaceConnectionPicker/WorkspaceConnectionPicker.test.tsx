import WorkspaceConnectionPicker from "./WorkspaceConnectionPicker";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { faker } from "@faker-js/faker";
import { useQuery } from "@apollo/client";
import { ConnectionType } from "graphql/types";

jest.mock("@apollo/client", () => ({
  __esModule: true,
  useQuery: jest.fn(),
  gql: jest.fn(() => "GQL"),
}));

const useQueryMock = useQuery as jest.Mock;

const WORKSPACE = {
  slug: faker.string.uuid(),
  connections: [
    {
      id: faker.string.uuid(),
      name: "dhis2-dev",
      slug: "dhis2-dev",
      type: ConnectionType.Dhis2,
    },
    {
      id: faker.string.uuid(),
      name: "dhis2-staging",
      slug: "dhis2-staging",
      type: ConnectionType.Dhis2,
    },
    {
      id: faker.string.uuid(),
      name: "iaso-dev",
      slug: "iaso-dev",
      type: ConnectionType.Iaso,
    },
  ],
};

describe("WorkspaceConnectionPicker", () => {
  it("display all connections", async () => {
    const user = userEvent.setup();

    useQueryMock.mockReturnValue({
      loading: true,
      data: {
        workspace: WORKSPACE,
      },
    });
    const onChange = jest.fn();

    const { container } = render(
      <WorkspaceConnectionPicker
        workspaceSlug={WORKSPACE.slug}
        onChange={onChange}
        value={""}
      />,
    );

    await user.click(await screen.findByTestId("combobox-button"));
    const option = await screen.queryAllByRole("option");
    expect(option.length).toBe(WORKSPACE.connections.length);
    expect(container).toMatchSnapshot();
  });

  it("display only connections with a given type", async () => {
    const user = userEvent.setup();

    useQueryMock.mockReturnValue({
      loading: true,
      data: {
        workspace: WORKSPACE,
      },
    });
    const onChange = jest.fn();

    render(
      <WorkspaceConnectionPicker
        workspaceSlug={WORKSPACE.slug}
        onChange={onChange}
        value={""}
        type={ConnectionType.Dhis2}
      />,
    );

    await user.click(await screen.findByTestId("combobox-button"));
    const option = screen.queryAllByRole("option");
    const dhis2Connections = WORKSPACE.connections.filter(
      (c) => c.type === ConnectionType.Dhis2,
    );

    expect(option.length).toBe(dhis2Connections.length);
  });
});
