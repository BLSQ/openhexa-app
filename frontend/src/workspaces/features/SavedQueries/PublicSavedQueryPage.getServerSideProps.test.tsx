import { getApolloClient } from "core/helpers/apollo";
import { SavedQueryVisibility } from "graphql/types";
import { getMe } from "identity/helpers/auth";
import { getServerSideProps } from "pages/queries/[querySlug]";

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

const buildCtx = (querySlug: string) =>
  ({
    params: { querySlug },
    req: { headers: {} },
    res: {},
    resolvedUrl: `/queries/${querySlug}`,
  }) as any;

const savedQuery = (visibility: SavedQueryVisibility) => ({
  id: "q1",
  slug: "my-query",
  name: "My query",
  description: "",
  visibility,
  // What the API returns: the workspace only to its members.
  workspace:
    visibility === SavedQueryVisibility.Public ? null : { slug: "ws-1" },
});

const mockClient = (savedQueryBySlug: any) => {
  const client = {
    query: jest.fn(() => Promise.resolve({ data: { savedQueryBySlug } })),
  };
  (getApolloClient as jest.Mock).mockReturnValue(client);
  return client;
};

const loggedIn = () =>
  (getMe as jest.Mock).mockResolvedValue({ user: { id: "u1" }, features: [] });
const anonymous = () =>
  (getMe as jest.Mock).mockResolvedValue({ user: null, features: [] });

describe("PublicSavedQueryPage getServerSideProps", () => {
  beforeEach(() => jest.clearAllMocks());

  it("renders a public query for an anonymous visitor", async () => {
    anonymous();
    mockClient(savedQuery(SavedQueryVisibility.Public));

    const result: any = await getServerSideProps(buildCtx("my-query"));

    expect(result.redirect).toBeUndefined();
    expect(result.props).toMatchObject({ querySlug: "my-query" });
  });

  // The query may exist but not be public: a login may be what is missing.
  it("sends an anonymous visitor of an unknown query to the login page", async () => {
    anonymous();
    mockClient(null);

    const result: any = await getServerSideProps(buildCtx("my-query"));

    expect(result.redirect).toEqual({
      permanent: false,
      destination: "/login?next=%2Fqueries%2Fmy-query",
    });
  });

  it("returns notFound to a logged-in user for an unknown query", async () => {
    loggedIn();
    mockClient(null);

    const result: any = await getServerSideProps(buildCtx("my-query"));

    expect(result.notFound).toBe(true);
  });

  // Only public queries have a permalink; whoever can see another one is a
  // member, and the Data Studio is where they work with it.
  it("sends a member to the Data Studio for a query that is not public", async () => {
    loggedIn();
    mockClient(savedQuery(SavedQueryVisibility.Workspace));

    const result: any = await getServerSideProps(buildCtx("my-query"));

    expect(result.redirect).toEqual({
      permanent: false,
      destination: "/workspaces/ws-1/data-studio/queries/my-query",
    });
  });
});
