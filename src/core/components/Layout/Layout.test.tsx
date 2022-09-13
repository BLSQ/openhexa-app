import { render, screen } from "@testing-library/react";
import { LOGGED_IN_USER, TestApp } from "core/helpers/testutils";
import { graphql } from "msw";
import { setupServer } from "msw/node";
import mockRouter from "next-router-mock";
import Layout from "./Layout";

const server = setupServer(
  graphql.query("SearchQuery", (req, res, ctx) => res(ctx.data({ search: {} })))
);

let mockMe = jest.fn();
jest.mock("identity/hooks/useMe", () => ({
  __esModule: true,
  default: () => mockMe(),
}));

describe("Layout", () => {
  beforeAll(() => server.listen());

  afterAll(() => {
    server.close();
  });

  beforeEach(() => {
    mockRouter.setCurrentUrl("/");
  });

  it("renders the layout for an unauthenticated user", async () => {
    mockMe.mockReturnValue({ user: null });
    const { container, debug } = render(
      <TestApp>
        <Layout pageProps={{}}>
          <span data-testid="page" />
        </Layout>
      </TestApp>
    );

    expect(screen.getByTestId("page")).toBeInTheDocument();
    expect(screen.queryByText("Dashboard")).toBeNull();

    expect(container).toMatchSnapshot();
  });

  it("renders the layout for a authenticated user", async () => {
    mockMe.mockReturnValue({
      user: LOGGED_IN_USER,
      features: [],
      authorizedActions: [],
    });
    const { container, debug } = render(
      <TestApp>
        <Layout pageProps={{}}>
          <span data-testid="page" />
        </Layout>
      </TestApp>
    );
    expect(screen.getByText("Dashboard")).toBeInTheDocument();
    expect(container).toMatchSnapshot();
  });
});
