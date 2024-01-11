import { render, screen } from "@testing-library/react";
import { TestApp } from "core/helpers/testutils";
import mockRouter from "next-router-mock";
import DefaultLayout from "../DefaultLayout";

describe("DefaultLayout", () => {
  beforeEach(() => {
    mockRouter.setCurrentUrl("/");
  });

  it("renders the layout for an unauthenticated user", async () => {
    const { container, debug } = render(
      <TestApp me={{ user: null, features: [] }}>
        <DefaultLayout pageProps={{}}>
          <span data-testid="page" />
        </DefaultLayout>
      </TestApp>,
    );

    expect(screen.getByTestId("page")).toBeInTheDocument();
    expect(screen.queryByText("Dashboard")).toBeNull();

    expect(container).toMatchSnapshot();
  });

  it("renders the layout for a authenticated user", async () => {
    const { container, debug } = render(
      <TestApp>
        <DefaultLayout pageProps={{}}>
          <span data-testid="page" />
        </DefaultLayout>
      </TestApp>,
    );
    expect(screen.getByText("Catalog")).toBeInTheDocument();
    expect(container).toMatchSnapshot();
  });
});
