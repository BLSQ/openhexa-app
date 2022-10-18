import { render, screen } from "@testing-library/react";
import { TestApp } from "core/helpers/testutils";
import mockRouter from "next-router-mock";
import Layout from "../Layout";

describe("Layout", () => {
  beforeEach(() => {
    mockRouter.setCurrentUrl("/");
  });

  it("renders the layout for an unauthenticated user", async () => {
    const { container, debug } = render(
      <TestApp me={{ user: null }}>
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
