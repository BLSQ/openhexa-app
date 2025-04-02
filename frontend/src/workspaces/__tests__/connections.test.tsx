import { render, screen } from "@testing-library/react";
import { TestApp, waitForDialog } from "core/helpers/testutils";
import ConnectionsPage from "pages/workspaces/[workspaceSlug]/connections";
import ConnectionPage from "pages/workspaces/[workspaceSlug]/connections/[connectionId]";
import {
  ConnectionPageDocument,
  ConnectionsPageDocument,
} from "workspaces/graphql/queries.generated";
import userEvent from "@testing-library/user-event";
import router from "next/router";
import { faker } from "@faker-js/faker";
import { deleteConnection } from "workspaces/helpers/connections/utils";

jest.mock("core/components/CodeEditor/CodeEditor", () => ({
  __esModule: true,
  default: () => "CODE_EDITOR",
}));

jest.mock("workspaces/helpers/connections/utils", () => ({
  __esModule: true,
  ...jest.requireActual("workspaces/helpers/connections/utils"),
  deleteConnection: jest.fn(),
}));

describe("Connections", () => {
  const WORKSPACE = {
    __typename: "Workspace",
    slug: faker.string.uuid(),
    name: faker.company.name(),
    description: faker.company.catchPhrase(),
    countries: [],
    permissions: {
      update: true,
      delete: true,
      createConnection: true,
      manageMembers: true,
    },
    connections: [],
    members: {
      totalItems: 0,
      items: [],
    },
  };

  const CONNECTION = {
    __typename: "Connection",
    id: faker.string.uuid(),
    description: faker.commerce.productDescription(),
    name: faker.commerce.productName(),
    slug: "MY_SLUG",
    type: "CUSTOM",
    updatedAt: "2022-02-01T10:00:00",
    user: null,
    permissions: {
      update: true,
      delete: true,
    },
    fields: [
      {
        code: "field_1",
        value: "Value field 1",
        secret: false,
      },
      {
        code: "secret_field",
        value: "secret_value",
        secret: true,
      },
    ],
  };
  it("does not display the 'add connection' to non-admins", async () => {
    const graphqlMocks = [
      {
        request: {
          query: ConnectionsPageDocument,
          variables: {
            workspaceSlug: WORKSPACE.slug,
          },
        },
        result: {
          data: {
            workspace: {
              ...WORKSPACE,
              permissions: {
                ...WORKSPACE.permissions,
                createConnection: false,
              },
            },
          },
        },
      },
    ];
    render(
      <TestApp mocks={graphqlMocks}>
        <ConnectionsPage workspaceSlug={WORKSPACE.slug} />
      </TestApp>,
    );

    const btn = await screen.queryByText("Add connection", {
      selector: "button",
    }); // Wait for page rendering
    expect(btn).not.toBeInTheDocument();
  });

  it("renders the page without connections", async () => {
    const graphqlMocks = [
      {
        request: {
          query: ConnectionsPageDocument,
          variables: {
            workspaceSlug: WORKSPACE.slug,
          },
        },
        result: {
          data: {
            workspace: WORKSPACE,
          },
        },
      },
    ];
    render(
      <TestApp mocks={graphqlMocks}>
        <ConnectionsPage workspaceSlug={WORKSPACE.slug} />
      </TestApp>,
    );
    const elm = await screen.findByText(
      "This workspace does not have any connection.",
    );
    expect(elm).toBeInTheDocument();
  });

  it("opens the connection creation dialog on click", async () => {
    const user = userEvent.setup();
    const graphqlMocks = [
      {
        request: {
          query: ConnectionsPageDocument,
          variables: {
            workspaceSlug: WORKSPACE.slug,
          },
        },
        result: {
          data: {
            workspace: WORKSPACE,
          },
        },
      },
    ];
    render(
      <TestApp mocks={graphqlMocks}>
        <ConnectionsPage workspaceSlug={WORKSPACE.slug} />
      </TestApp>,
    );
    const btn = await screen.findByText("Add connection", {
      selector: "button",
    }); // Wait for page rendering
    expect(btn).toBeInTheDocument();

    await user.click(btn);

    const dialog = await waitForDialog();
    expect(dialog).toBeInTheDocument();

    expect(
      await screen.findByText(
        "You can create a connection based on our supported integrations",
      ),
    ).toBeInTheDocument();
  });

  it("displays the list of connections", async () => {
    const user = userEvent.setup();
    const pushSpy = jest.spyOn(router, "push");
    const CONNECTION = {
      __typename: "Connection",
      id: faker.string.uuid(),
      description: faker.commerce.productDescription(),
      name: faker.commerce.productName(),
      slug: "MY_SLUG",
      type: "CUSTOM",
      createdAt: "2022-02-01T10:00:00",
      permissions: {
        update: true,
        delete: true,
      },
    };
    const graphqlMocks = [
      {
        request: {
          query: ConnectionsPageDocument,
          variables: {
            workspaceSlug: WORKSPACE.slug,
          },
        },
        result: {
          data: {
            workspace: {
              ...WORKSPACE,
              permissions: { update: false },
              connections: [CONNECTION],
            },
          },
        },
      },
    ];
    const { debug } = render(
      <TestApp mocks={graphqlMocks}>
        <ConnectionsPage workspaceSlug={WORKSPACE.slug} />
      </TestApp>,
    );
    const elm = await screen.findByText(CONNECTION.name);

    expect(elm).toBeInTheDocument();

    expect(pushSpy).not.toHaveBeenCalled();
    await user.click(elm);
    expect(pushSpy).toHaveBeenCalled();

    expect(
      screen.queryByText("Add connection", {
        selector: "button",
      }),
    ).not.toBeInTheDocument();
  });

  it("displays the button to add a connection", async () => {
    const user = userEvent.setup();
    const CONNECTION = {
      __typename: "Connection",
      id: faker.string.uuid(),
      description: faker.commerce.productDescription(),
      name: faker.commerce.productName(),
      slug: "MY_SLUG",
      type: "CUSTOM",
      createdAt: "2022-02-01T10:00:00",
      permissions: {
        update: true,
        delete: true,
      },
    };
    const graphqlMocks = [
      {
        request: {
          query: ConnectionsPageDocument,
          variables: {
            workspaceSlug: WORKSPACE.slug,
          },
        },
        result: {
          data: {
            workspace: {
              ...WORKSPACE,
              permissions: {
                ...WORKSPACE.permissions,
                update: true,
              },
              connections: [CONNECTION],
            },
          },
        },
      },
    ];
    const { debug } = render(
      <TestApp mocks={graphqlMocks}>
        <ConnectionsPage workspaceSlug={WORKSPACE.slug} />
      </TestApp>,
    );
    const elm = await screen.findByText("Add connection");
    expect(elm).toBeInTheDocument();
  });

  it("renders a connection page", async () => {
    const user = userEvent.setup();
    const graphqlMocks = [
      {
        request: {
          query: ConnectionPageDocument,
          variables: {
            workspaceSlug: WORKSPACE.slug,
            connectionId: CONNECTION.id,
          },
        },
        result: {
          data: {
            workspace: WORKSPACE,
            connection: CONNECTION,
          },
        },
      },
    ];
    const { debug } = render(
      <TestApp mocks={graphqlMocks}>
        <ConnectionPage
          workspaceSlug={WORKSPACE.slug}
          connectionId={CONNECTION.id}
        />
      </TestApp>,
    );
    expect(await screen.findByText("Information")).toBeInTheDocument();
    expect(screen.queryAllByText("Edit").length).toBe(2);

    expect(screen.getByText("Value field 1")).toBeInTheDocument();
    expect(screen.queryByText("secret_value")).not.toBeInTheDocument();
  });

  it("displays the button to delete the connection", async () => {
    const deleteConnectionMock = deleteConnection as jest.Mock;
    deleteConnectionMock.mockReturnValue(true);
    const graphqlMocks = [
      {
        request: {
          query: ConnectionPageDocument,
          variables: {
            workspaceSlug: WORKSPACE.slug,
            connectionId: CONNECTION.id,
          },
        },
        result: {
          data: {
            workspace: WORKSPACE,
            connection: CONNECTION,
          },
        },
      },
    ];
    const { debug } = render(
      <TestApp mocks={graphqlMocks}>
        <ConnectionPage
          workspaceSlug={WORKSPACE.slug}
          connectionId={CONNECTION.id}
        />
      </TestApp>,
    );
    expect(await screen.findByText("Delete")).toBeInTheDocument();
  });
});
