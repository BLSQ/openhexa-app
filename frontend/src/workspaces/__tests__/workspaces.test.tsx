import { render, screen } from "@testing-library/react";
import { TestApp } from "core/helpers/testutils";
import WorkspacePage from "pages/workspaces/[workspaceSlug]";
import { SidebarMenuDocument } from "workspaces/features/SidebarMenu/SidebarMenu.generated";
import { WorkspacePageDocument } from "workspaces/graphql/queries.generated";

describe("Workspaces", () => {
  it("renders the workspace page", async () => {
    const slug = "test";
    const graphqlMocks = [
      {
        request: {
          query: SidebarMenuDocument,
          variables: {
            page: 1,
            perPage: 5,
          },
        },
        result: {
          data: {
            pendingWorkspaceInvitations: {
              totalItems: 0,
              items: [],
            },
            workspaces: {
              totalItems: 0,
              items: [],
            },
          },
        },
      },
      {
        request: {
          query: WorkspacePageDocument,
          variables: {
            slug,
          },
        },
        result: {
          data: {
            workspace: {
              slug,
              name: "Rwanda Workspace",
              description: "This is a description",
              countries: [],
              permissions: {
                update: false,
                delete: false,
                manageMembers: false,
              },
              members: {
                totalItems: 0,
                items: [],
              },
            },
          },
        },
      },
    ];

    const { container } = render(
      <TestApp mocks={graphqlMocks}>
        <WorkspacePage page={1} perPage={1} workspaceSlug={slug} />
      </TestApp>,
    );
    const elm = await screen.findByText("Rwanda Workspace", { selector: "a" });
    expect(elm).toBeInTheDocument();
    expect(container).toMatchSnapshot();
  });

  it("renders null as workspace doesn't exist", async () => {
    const slug = "a303ff37-644b-4080-83d9-a42bd2712f63";
    const graphqlMocks = [
      {
        request: {
          query: SidebarMenuDocument,
          variables: {
            page: 1,
            perPage: 5,
          },
        },
        result: {
          data: {
            pendingWorkspaceInvitations: {
              totalItems: 0,
              items: [],
            },
            workspaces: {
              totalItems: 0,
              items: [],
            },
          },
        },
      },
      {
        request: {
          query: WorkspacePageDocument,
          variables: {
            slug,
          },
        },
        result: {
          data: {
            workspace: null,
          },
        },
      },
    ];

    const { container } = render(
      <TestApp mocks={graphqlMocks}>
        <WorkspacePage page={1} perPage={1} workspaceSlug={slug} />
      </TestApp>,
    );

    expect(container.firstChild).toBeNull();
    expect(container).toMatchSnapshot();
  });

  it("hides the edit button when user have not update permission ", async () => {
    const slug = "a303ff37-644b-4080-83d9-a42bd2712f63";
    const graphqlMocks = [
      {
        request: {
          query: SidebarMenuDocument,
          variables: {
            page: 1,
            perPage: 5,
          },
        },
        result: {
          data: {
            pendingWorkspaceInvitations: {
              totalItems: 0,
              items: [],
            },
            workspaces: {
              totalItems: 0,
              items: [],
            },
          },
        },
      },
      {
        request: {
          query: WorkspacePageDocument,
          variables: {
            slug,
          },
        },
        result: {
          data: {
            workspace: {
              slug,
              name: "Rwanda Workspace",
              description: "This is a description",
              permissions: {
                update: false,
                delete: false,
                manageMembers: false,
              },
              countries: [],
              members: {
                totalItems: 0,
                items: [],
              },
            },
          },
        },
      },
    ];

    const { container } = render(
      <TestApp mocks={graphqlMocks}>
        <WorkspacePage page={1} perPage={1} workspaceSlug={slug} />
      </TestApp>,
    );
    const editButton = screen.queryByText("Edit");
    expect(editButton).toBeNull();
    expect(container).toMatchSnapshot();
  });

  it("shows the jupyterhub entry when user have the launchNotebookServer permission ", async () => {
    const slug = "a303ff37-644b-4080-83d9-a42bd2712f63";
    const graphqlMocks = [
      {
        request: {
          query: SidebarMenuDocument,
          variables: {
            page: 1,
            perPage: 5,
          },
        },
        result: {
          data: {
            pendingWorkspaceInvitations: {
              totalItems: 0,
              items: [],
            },
            workspaces: {
              totalItems: 0,
              items: [],
            },
          },
        },
      },
      {
        request: {
          query: WorkspacePageDocument,
          variables: {
            slug,
          },
        },
        result: {
          data: {
            workspace: {
              slug,
              name: "Rwanda Workspace",
              description: "This is a description",
              permissions: {
                launchNotebookServer: true,
                delete: false,
                manageMembers: false,
              },
              countries: [],
              members: {
                totalItems: 0,
                items: [],
              },
            },
          },
        },
      },
    ];

    const { container } = render(
      <TestApp mocks={graphqlMocks}>
        <WorkspacePage page={1} perPage={1} workspaceSlug={slug} />
      </TestApp>,
    );
    const elm = await screen.findByText("JupyterHub", { selector: "a" });
    expect(elm).toBeInTheDocument();
    expect(container).toMatchSnapshot();
  });
});
