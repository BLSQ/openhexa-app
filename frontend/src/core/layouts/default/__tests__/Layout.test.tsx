import { render, screen } from "@testing-library/react";
import { TestApp } from "core/helpers/testutils";
import mockRouter from "next-router-mock";
import DefaultLayout from "../DefaultLayout";

jest.mock("next-i18next", () => ({
  useTranslation: () => ({
    t: (key: string) => key,
  }),
  i18n: {
    t: (key: string) => key,
  },
}));

describe("DefaultLayout", () => {
  beforeEach(() => {
    mockRouter.setCurrentUrl("/");
  });

  it("renders the layout for an unauthenticated user", async () => {
    const { container } = render(
      <TestApp me={{ user: null, features: [] }}>
        <DefaultLayout pageProps={{}}>
          <span data-testid="page" />
        </DefaultLayout>
      </TestApp>,
    );

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
    expect(container).toMatchSnapshot();
  });
});
