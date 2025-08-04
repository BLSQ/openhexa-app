import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { useOrganizationMembersQuery } from "../OrganizationMembers.generated";
import { TestApp } from "core/helpers/testutils";
import OrganizationMembers from "../OrganizationMembers";
import { v4 } from "uuid";
import {
  OrganizationMembershipRole,
  WorkspaceMembershipRole,
} from "graphql/types";

const ORGANIZATION_ID = v4();

const MOCK_MEMBERS = [
  {
    id: v4(),
    role: OrganizationMembershipRole.Admin,
    createdAt: "2023-01-15T10:00:00Z",
    workspaceMemberships: [
      {
        id: v4(),
        role: WorkspaceMembershipRole.Editor,
        workspace: {
          slug: "workspace-1",
          name: "Test Workspace 1",
        },
      },
    ],
    user: {
      id: v4(),
      displayName: "John Doe",
      email: "john.doe@example.com",
      avatar: {
        initials: "JD",
        color: "blue",
      },
    },
  },
  {
    id: v4(),
    role: OrganizationMembershipRole.Member,
    createdAt: "2023-02-20T14:30:00Z",
    workspaceMemberships: [
      {
        id: v4(),
        role: WorkspaceMembershipRole.Viewer,
        workspace: {
          slug: "workspace-2",
          name: "Test Workspace 2",
        },
      },
    ],
    user: {
      id: v4(),
      displayName: "Jane Smith",
      email: "jane.smith@example.com",
      avatar: {
        initials: "JS",
        color: "green",
      },
    },
  },
];

const MOCK_ORGANIZATION_QUERY_RESULT = {
  organization: {
    id: ORGANIZATION_ID,
    permissions: {
      manageMembers: true,
    },
    members: {
      totalItems: 2,
      items: MOCK_MEMBERS,
    },
    workspaces: {
      items: [
        {
          slug: "workspace-1",
          name: "Test Workspace 1",
        },
        {
          slug: "workspace-2",
          name: "Test Workspace 2",
        },
      ],
    },
  },
};

const MOCK_ORGANIZATION_QUERY_NO_PERMISSIONS = {
  organization: {
    id: ORGANIZATION_ID,
    permissions: {
      manageMembers: false,
    },
    members: {
      totalItems: 2,
      items: MOCK_MEMBERS,
    },
    workspaces: {
      items: [
        {
          slug: "workspace-1",
          name: "Test Workspace 1",
        },
        {
          slug: "workspace-2",
          name: "Test Workspace 2",
        },
      ],
    },
  },
};

jest.mock("../OrganizationMembers.generated", () => ({
  ...jest.requireActual("../OrganizationMembers.generated"),
  useOrganizationMembersQuery: jest.fn(),
}));

jest.mock("next-i18next", () => ({
  useTranslation: () => ({
    t: (key: string) => key,
  }),
  Trans: ({ children }: { children: React.ReactNode }) => <>{children}</>,
  i18n: {
    t: (key: string) => key,
  },
}));

const useOrganizationMembersQueryMock =
  useOrganizationMembersQuery as jest.Mock;

describe("OrganizationMembers", () => {
  beforeEach(() => {
    useOrganizationMembersQueryMock.mockClear();
  });

  it("renders organization members list correctly", async () => {
    useOrganizationMembersQueryMock.mockReturnValue({
      data: MOCK_ORGANIZATION_QUERY_RESULT,
      loading: false,
      refetch: jest.fn(),
    });

    const { container } = render(
      <OrganizationMembers organizationId={ORGANIZATION_ID} />,
    );

    expect(screen.getByText("John Doe")).toBeInTheDocument();
    expect(screen.getByText("jane.smith@example.com")).toBeInTheDocument();
    expect(screen.getByText("Jane Smith")).toBeInTheDocument();

    expect(screen.getByText("Admin")).toBeInTheDocument();
    expect(screen.getByText("Member")).toBeInTheDocument();

    expect(container).toMatchSnapshot();
  });

  it("handles empty members list", async () => {
    useOrganizationMembersQueryMock.mockReturnValue({
      data: {
        organization: {
          id: ORGANIZATION_ID,
          permissions: { manageMembers: true },
          members: { totalItems: 0, items: [] },
        },
      },
      loading: false,
      refetch: jest.fn(),
    });

    render(<OrganizationMembers organizationId={ORGANIZATION_ID} />);

    expect(screen.getByText("User")).toBeInTheDocument();
    expect(screen.getByText("Organization Role")).toBeInTheDocument();
  });

  it("handles search functionality", async () => {
    let lastQueryVariables: any = {};
    const mockRefetch = jest.fn();

    useOrganizationMembersQueryMock.mockImplementation((options) => {
      lastQueryVariables = options.variables;
      return {
        data: MOCK_ORGANIZATION_QUERY_RESULT,
        loading: false,
        refetch: mockRefetch,
      };
    });

    const user = userEvent.setup();

    render(<OrganizationMembers organizationId={ORGANIZATION_ID} />);

    const searchInput = screen.getByPlaceholderText("Search members...");

    expect(lastQueryVariables).toEqual({
      id: ORGANIZATION_ID,
      page: 1,
      perPage: 10,
      term: "",
    });

    await user.type(searchInput, "John");

    await waitFor(
      () => {
        expect(lastQueryVariables).toEqual({
          id: ORGANIZATION_ID,
          page: 1,
          perPage: 10,
          term: "John",
        });
      },
      { timeout: 1000 },
    );

    expect(searchInput).toHaveValue("John");
  });

  it("shows edit and delete buttons when user has manage permissions", async () => {
    useOrganizationMembersQueryMock.mockReturnValue({
      data: MOCK_ORGANIZATION_QUERY_RESULT,
      loading: false,
      refetch: jest.fn(),
    });

    render(<OrganizationMembers organizationId={ORGANIZATION_ID} />);

    const editButtons = screen.getAllByLabelText("edit");
    const deleteButtons = screen.getAllByLabelText("delete");

    expect(editButtons).toHaveLength(2);
    expect(deleteButtons).toHaveLength(2);
  });

  it("hides edit and delete buttons when user lacks manage permissions", async () => {
    useOrganizationMembersQueryMock.mockReturnValue({
      data: MOCK_ORGANIZATION_QUERY_NO_PERMISSIONS,
      loading: false,
      refetch: jest.fn(),
    });

    render(<OrganizationMembers organizationId={ORGANIZATION_ID} />);

    const buttons = screen.queryAllByRole("button");
    expect(buttons).toHaveLength(0);
  });

  it("opens delete dialog when delete button is clicked", async () => {
    useOrganizationMembersQueryMock.mockReturnValue({
      data: MOCK_ORGANIZATION_QUERY_RESULT,
      loading: false,
      refetch: jest.fn(),
    });

    const user = userEvent.setup();

    render(
      <TestApp>
        <OrganizationMembers organizationId={ORGANIZATION_ID} />
      </TestApp>,
    );

    const deleteButton = screen.getAllByLabelText("delete")[0];
    await user.click(deleteButton);

    await waitFor(
      () => {
        expect(screen.getByRole("dialog")).toBeInTheDocument();
        expect(screen.getByText("Remove Member")).toBeInTheDocument();
      },
      { timeout: 3000 },
    );
  });

  it("opens update dialog when edit button is clicked", async () => {
    useOrganizationMembersQueryMock.mockReturnValue({
      data: MOCK_ORGANIZATION_QUERY_RESULT,
      loading: false,
      refetch: jest.fn(),
    });

    const user = userEvent.setup();

    render(
      <TestApp>
        <OrganizationMembers organizationId={ORGANIZATION_ID} />
      </TestApp>,
    );

    const editButton = screen.getAllByLabelText("edit")[0];
    await user.click(editButton);

    await waitFor(
      () => {
        expect(screen.getByRole("dialog")).toBeInTheDocument();
        expect(
          screen.getByText("Update Member Permissions"),
        ).toBeInTheDocument();
      },
      { timeout: 3000 },
    );
  });

  it("displays workspace roles correctly", async () => {
    useOrganizationMembersQueryMock.mockReturnValue({
      data: MOCK_ORGANIZATION_QUERY_RESULT,
      loading: false,
      refetch: jest.fn(),
    });

    render(
      <TestApp>
        <OrganizationMembers organizationId={ORGANIZATION_ID} />
      </TestApp>,
    );

    expect(
      screen.getByText((content) => {
        return content.includes("Test Workspace 1");
      }),
    ).toBeInTheDocument();
    expect(
      screen.getByText((content) => {
        return content.includes("Test Workspace 2");
      }),
    ).toBeInTheDocument();
  });
});
