import { getServerSideProps } from "pages/workspaces/[workspaceSlug]/webapps/create";
import { getApolloClient } from "core/helpers/apollo";
import { getMe } from "identity/helpers/auth";
import WorkspaceLayout from "workspaces/layouts/WorkspaceLayout";

jest.mock("core/helpers/apollo", () => ({
  ...jest.requireActual("core/helpers/apollo"),
  __esModule: true,
  getApolloClient: jest.fn(),
  addApolloState: jest.fn(() => ({ props: {} })),
}));

jest.mock("identity/helpers/auth", () => ({
  ...jest.requireActual("identity/helpers/auth"),
  __esModule: true,
  getMe: jest.fn(),
}));

jest.mock("next-i18next/serverSideTranslations", () => ({
  serverSideTranslations: jest.fn().mockResolvedValue({}),
}));

const buildCtx = () =>
  ({
    params: { workspaceSlug: "test-workspace" },
    req: { headers: {} },
    res: {},
    resolvedUrl: "/workspaces/test-workspace/webapps/create",
  }) as any;

const mockWorkspaceQuery = (workspace: any) => {
  const client = {
    query: jest.fn().mockResolvedValue({ data: { workspace } }),
  };
  (getApolloClient as jest.Mock).mockReturnValue(client);
  return client;
};

describe("WebappCreatePage getServerSideProps", () => {
  beforeEach(() => {
    jest.clearAllMocks();
    jest
      .spyOn(WorkspaceLayout, "prefetch")
      .mockResolvedValue(undefined as any);
    (getMe as jest.Mock).mockResolvedValue({
      user: { id: "user-1" },
      features: [],
    });
  });

  it("redirects users without the update permission to the webapps list", async () => {
    mockWorkspaceQuery({
      slug: "test-workspace",
      permissions: { update: false },
    });

    const result: any = await getServerSideProps(buildCtx());

    expect(result.redirect).toEqual({
      permanent: false,
      destination: "/workspaces/test-workspace/webapps",
    });
  });

  it("returns the workspace as props for users with the update permission", async () => {
    const workspace = {
      slug: "test-workspace",
      permissions: { update: true },
    };
    mockWorkspaceQuery(workspace);

    const result: any = await getServerSideProps(buildCtx());

    expect(result.redirect).toBeUndefined();
    expect(result.props.workspace).toEqual(workspace);
  });

  it("returns notFound when the workspace does not exist", async () => {
    mockWorkspaceQuery(null);

    const result: any = await getServerSideProps(buildCtx());

    expect(result.notFound).toBe(true);
  });
});
