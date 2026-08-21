import { getApolloClient } from "core/helpers/apollo";
import { getMe } from "identity/helpers/auth";
import { getServerSideProps } from "pages/workspaces/[workspaceSlug]/data-studio/queries/[querySlug]";
import DataStudioLayout from "workspaces/layouts/DataStudioLayout";

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

const WORKSPACE = { slug: "ws-1", permissions: { createSavedQuery: true } };
// A real v4 UUID: the page validates the id with `isValidUuid`, which checks the
// version and variant nibbles rather than the hex shape alone.
const UUID = "11111111-2222-4333-8444-555555555555";

const buildCtx = (querySlug: string) =>
  ({
    params: { workspaceSlug: "ws-1", querySlug },
    req: { headers: {} },
    res: {},
    resolvedUrl: `/workspaces/ws-1/data-studio/queries/${querySlug}`,
  }) as any;

/** Answers each query by operation name, so order does not matter. */
const mockClient = (responses: Record<string, any>) => {
  const client = {
    query: jest.fn(({ query }) => {
      const name = query.definitions[0].name.value;
      return Promise.resolve({ data: responses[name] ?? {} });
    }),
  };
  (getApolloClient as jest.Mock).mockReturnValue(client);
  return client;
};

describe("SavedQueryPage getServerSideProps", () => {
  beforeEach(() => {
    jest.clearAllMocks();
    jest
      .spyOn(DataStudioLayout, "prefetch")
      .mockResolvedValue(undefined as any);
    (getMe as jest.Mock).mockResolvedValue({
      user: { id: "u1" },
      features: [],
    });
  });

  it("renders the query found by slug", async () => {
    mockClient({
      WorkspaceSavedQueryPage: {
        workspace: WORKSPACE,
        savedQueryBySlug: { id: "q1", slug: "my-query" },
      },
    });

    const result: any = await getServerSideProps(buildCtx("my-query"));

    expect(result.redirect).toBeUndefined();
    expect(result.props).toMatchObject({
      workspaceSlug: "ws-1",
      querySlug: "my-query",
    });
  });

  it("redirects a legacy id URL to the slug URL", async () => {
    mockClient({
      WorkspaceSavedQueryPage: { workspace: WORKSPACE, savedQueryBySlug: null },
      WorkspaceSavedQuerySlugById: {
        savedQuery: { id: UUID, slug: "my-query" },
      },
    });

    const result: any = await getServerSideProps(buildCtx(UUID));

    expect(result.redirect).toEqual({
      permanent: false,
      destination: "/workspaces/ws-1/data-studio/queries/my-query",
    });
  });

  it("returns notFound for an unknown slug without looking it up by id", async () => {
    const client = mockClient({
      WorkspaceSavedQueryPage: { workspace: WORKSPACE, savedQueryBySlug: null },
    });

    const result: any = await getServerSideProps(buildCtx("no-such-query"));

    expect(result.notFound).toBe(true);
    // A slug is not an id, so the fallback lookup must not run for one.
    expect(client.query).toHaveBeenCalledTimes(1);
  });

  it("returns notFound for an id that no longer exists", async () => {
    mockClient({
      WorkspaceSavedQueryPage: { workspace: WORKSPACE, savedQueryBySlug: null },
      WorkspaceSavedQuerySlugById: { savedQuery: null },
    });

    const result: any = await getServerSideProps(buildCtx(UUID));

    expect(result.notFound).toBe(true);
  });
});
