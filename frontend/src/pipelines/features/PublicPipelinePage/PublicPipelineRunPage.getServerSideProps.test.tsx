import { getApolloClient } from "core/helpers/apollo";
import { getMe } from "identity/helpers/auth";
import { getServerSideProps } from "pages/run/[pipelineId]/[runId]";

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

const buildCtx = (pipelineId: string, runId: string) =>
  ({
    params: { pipelineId, runId },
    req: { headers: {} },
    res: {},
    resolvedUrl: `/run/${pipelineId}/${runId}`,
  }) as any;

const mockClient = (publicPipelineRun: any) => {
  const client = {
    query: jest.fn(() => Promise.resolve({ data: { publicPipelineRun } })),
  };
  (getApolloClient as jest.Mock).mockReturnValue(client);
  return client;
};

const loggedIn = () =>
  (getMe as jest.Mock).mockResolvedValue({ user: { id: "u1" }, features: [] });
const anonymous = () =>
  (getMe as jest.Mock).mockResolvedValue({ user: null, features: [] });

describe("PublicPipelineRunPage getServerSideProps", () => {
  beforeEach(() => jest.clearAllMocks());

  it("renders a public run for an anonymous visitor", async () => {
    anonymous();
    mockClient({ id: "r1", pipeline: { id: "p1" } });

    const result: any = await getServerSideProps(buildCtx("p1", "r1"));

    expect(result.redirect).toBeUndefined();
    expect(result.props).toMatchObject({ pipelineId: "p1", runId: "r1" });
  });

  // The run id is the credential; the pipeline id in the path still has to be
  // the run's own, so a link cannot present one pipeline's run as another's.
  it("does not serve a run under another pipeline's path", async () => {
    loggedIn();
    mockClient({ id: "r1", pipeline: { id: "p1" } });

    const result: any = await getServerSideProps(buildCtx("p2", "r1"));

    expect(result.notFound).toBe(true);
  });

  it("sends an anonymous visitor of an unknown run to the login page", async () => {
    anonymous();
    mockClient(null);

    const result: any = await getServerSideProps(buildCtx("p1", "r1"));

    expect(result.redirect).toEqual({
      permanent: false,
      destination: "/login?next=%2Frun%2Fp1%2Fr1",
    });
  });

  it("returns notFound to a logged-in user for an unknown run", async () => {
    loggedIn();
    mockClient(null);

    const result: any = await getServerSideProps(buildCtx("p1", "r1"));

    expect(result.notFound).toBe(true);
  });
});
