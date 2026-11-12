import { render, renderHook, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { ReactNode } from "react";
import { Cookies, CookiesProvider } from "react-cookie";
import { getPublicEnv } from "core/helpers/runtimeConfig";
import SubscriptionBanner, {
  getSubscriptionBannerState,
  useSubscriptionBannerOffsetStyle,
} from "./SubscriptionBanner";

jest.mock("core/helpers/runtimeConfig", () => ({
  ...jest.requireActual("core/helpers/runtimeConfig"),
  usePublicEnv: jest.fn(),
  getPublicEnv: jest.fn(),
}));

const mockedEnv = getPublicEnv as jest.Mock;

const buildOrganization = (
  subscription: Partial<{
    isExpired: boolean;
    isInGracePeriod: boolean;
    isExpiringSoon: boolean;
  }> | null,
  manageMembers = true,
) => ({
  id: "org-1",
  name: "Acme",
  permissions: { manageMembers },
  subscription: subscription && {
    endDate: "2026-11-20",
    isExpired: false,
    isInGracePeriod: false,
    isExpiringSoon: false,
    ...subscription,
  },
});

let cookies: Cookies;
const wrapper = ({ children }: { children: ReactNode }) => (
  <CookiesProvider cookies={cookies}>{children}</CookiesProvider>
);
const renderBanner = (organization: ReturnType<typeof buildOrganization>) =>
  render(<SubscriptionBanner organization={organization} />, { wrapper });

describe("SubscriptionBanner", () => {
  beforeEach(() => {
    cookies = new Cookies();
    cookies.remove("subscription-banner-dismissed", { path: "/" });
    const env = {
      CONSOLE_URL: "https://console.example.com",
      CONTACT_EMAIL: "sales@example.com",
    };
    mockedEnv.mockReturnValue(env);
    jest
      .requireMock("core/helpers/runtimeConfig")
      .usePublicEnv.mockReturnValue(env);
  });

  it.each([
    ["no subscription (self-hosted)", buildOrganization(null), null],
    ["an active subscription", buildOrganization({}), null],
    [
      "a subscription expiring soon",
      buildOrganization({ isExpiringSoon: true }),
      "expiringSoon",
    ],
    [
      "a subscription in grace period",
      buildOrganization({ isExpired: true, isInGracePeriod: true }),
      "gracePeriod",
    ],
    ["a frozen subscription", buildOrganization({ isExpired: true }), "frozen"],
    ["a non-admin member", buildOrganization({ isExpired: true }, false), null],
  ])("computes the state for %s", (_, organization, expected) => {
    expect(getSubscriptionBannerState(organization)).toBe(expected);
  });

  it("only offsets the layout when the banner is shown", () => {
    const offsetFor = (organization: ReturnType<typeof buildOrganization>) =>
      renderHook(() => useSubscriptionBannerOffsetStyle(organization), {
        wrapper,
      }).result.current;
    expect(offsetFor(buildOrganization({}))).toEqual({
      "--subscription-banner-height": "0px",
    });
    expect(offsetFor(buildOrganization({ isExpiringSoon: true }))).toEqual({
      "--subscription-banner-height": "2.5rem",
    });
  });

  it("hides the expiring soon banner and its layout offset once dismissed", async () => {
    const organization = buildOrganization({ isExpiringSoon: true });
    const user = userEvent.setup();
    renderBanner(organization);
    await user.click(screen.getByRole("button", { name: "Dismiss" }));
    expect(screen.queryByRole("alert")).not.toBeInTheDocument();
    const { result } = renderHook(
      () => useSubscriptionBannerOffsetStyle(organization),
      { wrapper },
    );
    expect(result.current).toEqual({ "--subscription-banner-height": "0px" });
  });

  it("shows the banner again when the subscription end date changes", () => {
    cookies.set(
      "subscription-banner-dismissed",
      { "org-1": "2026-01-01" },
      { path: "/" },
    );
    renderBanner(buildOrganization({ isExpiringSoon: true }));
    expect(screen.getByRole("alert")).toBeInTheDocument();
  });

  it("cannot dismiss an expired subscription banner", () => {
    cookies.set(
      "subscription-banner-dismissed",
      { "org-1": "2026-11-20" },
      { path: "/" },
    );
    renderBanner(buildOrganization({ isExpired: true, isInGracePeriod: true }));
    expect(screen.getByRole("alert")).toBeInTheDocument();
    expect(
      screen.queryByRole("button", { name: "Dismiss" }),
    ).not.toBeInTheDocument();
  });

  it("renders nothing when there is nothing to warn about", () => {
    const { container } = renderBanner(buildOrganization({}));
    expect(container).toBeEmptyDOMElement();
  });

  it("renders the expiring soon banner with both CTAs", () => {
    renderBanner(buildOrganization({ isExpiringSoon: true }));
    expect(screen.getByRole("alert")).toHaveTextContent(/expires on/);
    expect(screen.getByRole("link", { name: /Upgrade plan/ })).toHaveAttribute(
      "href",
      "https://console.example.com",
    );
    expect(screen.getByRole("link", { name: /Contact us/ })).toHaveAttribute(
      "href",
      "mailto:sales@example.com",
    );
  });

  it("renders the frozen banner", () => {
    renderBanner(buildOrganization({ isExpired: true }));
    expect(screen.getByRole("alert")).toHaveTextContent(
      "Limits are frozen until you renew",
    );
  });

  it("hides the CTAs that are not configured", () => {
    jest
      .requireMock("core/helpers/runtimeConfig")
      .usePublicEnv.mockReturnValue({ CONSOLE_URL: "", CONTACT_EMAIL: "" });
    renderBanner(
      buildOrganization({
        isExpired: true,
        isInGracePeriod: true,
      }),
    );
    expect(screen.getByRole("alert")).toBeInTheDocument();
    expect(screen.queryByRole("link")).not.toBeInTheDocument();
  });
});
