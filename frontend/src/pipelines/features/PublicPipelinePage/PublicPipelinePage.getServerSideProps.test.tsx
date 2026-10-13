import { getApolloClient } from "core/helpers/apollo";
import { getMe } from "identity/helpers/auth";
import { getServerSideProps } from "pages/run/[pipelineId]";
import {
  PublicPipelinePageDocument,
  PublicPipelineRedirectDocument,
} from "pipelines/graphql/queries.generated";

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

const buildCtx = (pipelineId: string) =>
  ({
    params: { pipelineId },
    req: { headers: {} },
    res: {},
    resolvedUrl: `/run/${pipelineId}`,
  }) as any;

const mockClient = ({
  publicPipeline = null,
  pipeline = null,
}: {
  publicPipeline?: any;
  pipeline?: any;
}) => {
  const client = {
    query: jest.fn(({ query }) => {
      if (query === PublicPipelinePageDocument) {
        return Promise.resolve({ data: { publicPipeline } });
      }
      if (query === PublicPipelineRedirectDocument) {
        return Promise.resolve({ data: { pipeline } });
      }
      throw new Error("Unexpected query");
    }),
  };
  (getApolloClient as jest.Mock).mockReturnValue(client);
  return client;
};

const loggedIn = () =>
  (getMe as jest.Mock).mockResolvedValue({ user: { id: "u1" }, features: [] });
const anonymous = () =>
  (getMe as jest.Mock).mockResolvedValue({ user: null, features: [] });

describe("PublicPipelinePage getServerSideProps", () => {
  beforeEach(() => jest.clearAllMocks());

  it("renders a public pipeline for an anonymous visitor", async () => {
    anonymous();
    const client = mockClient({ publicPipeline: { id: "p1", name: "P" } });

    const result: any = await getServerSideProps(buildCtx("p1"));

    expect(result.redirect).toBeUndefined();
    expect(result.props).toMatchObject({ pipelineId: "p1" });
    // The member-only lookup is never attempted for a public pipeline.
    expect(client.query).toHaveBeenCalledTimes(1);
  });

  // The pipeline may exist but not be public: a login may be what is missing.
  it("sends an anonymous visitor of an unknown pipeline to the login page", async () => {
    anonymous();
    mockClient({});

    const result: any = await getServerSideProps(buildCtx("p1"));

    expect(result.redirect).toEqual({
      permanent: false,
      destination: "/login?next=%2Frun%2Fp1",
    });
  });

  it("returns notFound to a logged-in user for an unknown pipeline", async () => {
    loggedIn();
    mockClient({});

    const result: any = await getServerSideProps(buildCtx("p1"));

    expect(result.notFound).toBe(true);
  });

  // Whoever can see a pipeline that is not public is a member of its workspace.
  it("sends a member to the workspace page of a pipeline that is not public", async () => {
    loggedIn();
    mockClient({
      pipeline: { id: "p1", code: "my-pipeline", workspace: { slug: "ws-1" } },
    });

    const result: any = await getServerSideProps(buildCtx("p1"));

    expect(result.redirect).toEqual({
      permanent: false,
      destination: "/workspaces/ws-1/pipelines/my-pipeline",
    });
  });
});
