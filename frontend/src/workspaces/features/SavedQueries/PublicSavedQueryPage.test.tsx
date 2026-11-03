import { render, screen } from "@testing-library/react";
import PublicSavedQueryPage from "pages/queries/[querySlug]";

const mockMe = jest.fn();
const mockPageQuery = jest.fn();

jest.mock("identity/hooks/useMe", () => () => mockMe());

jest.mock("next/router", () => ({
  useRouter: () => ({ asPath: "/queries/my-query" }),
}));

jest.mock("workspaces/graphql/queries.generated", () => ({
  ...jest.requireActual("workspaces/graphql/queries.generated"),
  usePublicSavedQueryPageQuery: () => mockPageQuery(),
  useExecuteSavedQueryLazyQuery: () => [
    jest.fn(),
    { data: undefined, loading: false, error: undefined },
  ],
}));

jest.mock("workspaces/features/DataStudioEditor/DataStudioResults", () => ({
  __esModule: true,
  default: () => null,
}));

const publicSavedQuery = {
  slug: "my-query",
  name: "My query",
  description: "a query",
};

const renderPage = ({
  user = null,
  savedQueryBySlug = null,
}: {
  user?: any;
  savedQueryBySlug?: any;
}) => {
  mockMe.mockReturnValue({ user, features: [] });
  mockPageQuery.mockReturnValue({
    data: { publicSavedQuery, savedQueryBySlug },
  });
  return render(<PublicSavedQueryPage querySlug="my-query" />);
};

describe("PublicSavedQueryPage", () => {
  it("invites visitors to try OpenHEXA", () => {
    renderPage({});

    expect(screen.getByText("Start a free trial").closest("a")).toHaveAttribute(
      "href",
      "https://www.openhexa.com/",
    );
    expect(screen.queryByText("Open in Data Studio")).not.toBeInTheDocument();
  });

  // The app's home is a login page for them: the website tells them more.
  it("links the logo to the website for visitors", () => {
    renderPage({});
    expect(
      screen.getAllByRole("img", { name: "OpenHEXA" })[0].closest("a"),
    ).toHaveAttribute("href", "https://www.openhexa.com/");
  });

  it("links the logo to the app's home for logged-in users", () => {
    renderPage({ user: { id: "u1" } });
    expect(
      screen.getAllByRole("img", { name: "OpenHEXA" })[0].closest("a"),
    ).toHaveAttribute("href", "/");
  });

  // Members already use OpenHEXA: they get a way back to the query instead.
  it("sends members to the query in the Data Studio", () => {
    renderPage({
      user: { id: "u1" },
      savedQueryBySlug: {
        id: "q1",
        slug: "my-query",
        workspace: { slug: "ws-1" },
      },
    });

    expect(
      screen.getByText("Open in Data Studio").closest("a"),
    ).toHaveAttribute("href", "/workspaces/ws-1/data-studio/queries/my-query");
    expect(screen.queryByText("Start a free trial")).not.toBeInTheDocument();
  });

  it("does not invite a logged-in user who is not a member", () => {
    renderPage({ user: { id: "u2" } });

    expect(screen.queryByText("Start a free trial")).not.toBeInTheDocument();
    expect(screen.queryByText("Open in Data Studio")).not.toBeInTheDocument();
  });

  it("is powered by OpenHEXA, for everyone", () => {
    renderPage({ user: { id: "u1" } });

    // The header logo is a link named OpenHEXA too, but to the app's home.
    const poweredBy = screen
      .getAllByRole("link", { name: /OpenHEXA/ })
      .filter(
        (link) => link.getAttribute("href") === "https://www.openhexa.com/",
      );
    expect(poweredBy).toHaveLength(1);
  });
});
