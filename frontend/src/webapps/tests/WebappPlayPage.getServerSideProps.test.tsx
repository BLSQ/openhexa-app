import { getServerSideProps } from "pages/workspaces/[workspaceSlug]/webapps/[webappSlug]/play";
import { getApolloClient } from "core/helpers/apollo";
import { getMe } from "identity/helpers/auth";
import { IncomingMessage, ServerResponse } from "http";
import { Socket } from "net";
import nextConfig from "../../../next.config";

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

// A response carrying the headers next.config.js applies to every page, as Next
// sets them before the page renders.
const buildCtx = async () => {
  const req = new IncomingMessage(new Socket());
  const res = new ServerResponse(req);
  const rules = await nextConfig.headers();
  for (const { key, value } of rules.flatMap((rule: any) => rule.headers)) {
    res.setHeader(key, value);
  }
  return {
    params: { workspaceSlug: "test-workspace", webappSlug: "app" },
    query: {},
    req: Object.assign(req, { headers: {} }),
    res,
    resolvedUrl: "/workspaces/test-workspace/webapps/app/play",
  } as any;
};

const mockWebapp = (webapp: any) => {
  (getApolloClient as jest.Mock).mockReturnValue({
    query: jest.fn().mockResolvedValue({ data: { webapp } }),
  });
};

const WEBAPP = {
  slug: "app",
  name: "App",
  url: "https://example.com",
  type: "IFRAME",
  pointsToOpenhexaWebapp: false,
  showPoweredBy: true,
  workspace: { slug: "test-workspace" },
};

describe("WebappPlayPage getServerSideProps", () => {
  beforeEach(() => {
    jest.clearAllMocks();
    (getMe as jest.Mock).mockResolvedValue(null);
  });

  it("lets any site frame a public web app", async () => {
    mockWebapp({ ...WEBAPP, isPublic: true });
    const ctx = await buildCtx();

    await getServerSideProps(ctx);

    expect(ctx.res.getHeader("Content-Security-Policy")).toBe(
      "frame-ancestors *",
    );
    expect(ctx.res.hasHeader("X-Frame-Options")).toBe(false);
  });

  it("keeps the default framing restrictions for a private web app", async () => {
    (getMe as jest.Mock).mockResolvedValue({
      user: { id: "user-1" },
      features: [],
    });
    mockWebapp({ ...WEBAPP, isPublic: false });
    const ctx = await buildCtx();

    await getServerSideProps(ctx);

    expect(ctx.res.getHeader("Content-Security-Policy")).toBe(
      "frame-ancestors 'self'",
    );
    expect(ctx.res.getHeader("X-Frame-Options")).toBe("SAMEORIGIN");
  });
});
