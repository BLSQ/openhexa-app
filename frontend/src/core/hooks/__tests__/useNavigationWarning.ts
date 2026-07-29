import { act, renderHook } from "@testing-library/react";
import mockRouter from "next-router-mock";
import useNavigationWarning, {
  NavigationWarningProps,
} from "../useNavigationWarning";

const confirm = window.confirm as jest.Mock;

const DEFAULT_MESSAGE = "You have unsaved changes. Leave anyway?";

const renderWarning = (props: NavigationWarningProps) =>
  renderHook((p: NavigationWarningProps) => useNavigationWarning(p), {
    initialProps: props,
  });

// `beforePopState` takes a single callback, which is the only way to reach the
// back/forward path: next-router-mock stubs the method out, so the test drives
// the registered callback itself.
type PopStateCallback = (state: { as: string }) => boolean;
const spyOnPopState = () => {
  const spy = jest.spyOn(mockRouter, "beforePopState");
  return () => (spy.mock.calls[0] as unknown as [PopStateCallback])[0];
};

beforeEach(() => {
  mockRouter.setCurrentUrl("/current");
});

describe("useNavigationWarning", () => {
  it("lets navigation through when disabled", async () => {
    renderWarning({ enabled: false });

    await act(() => mockRouter.push("/other"));

    expect(mockRouter.asPath).toBe("/other");
    expect(confirm).not.toHaveBeenCalled();
  });

  it("keeps the user on the page when they cancel", async () => {
    confirm.mockReturnValue(false);
    renderWarning({ enabled: true });

    await expect(mockRouter.push("/other")).rejects.toBe(
      "Route change aborted",
    );

    expect(confirm).toHaveBeenCalledWith(DEFAULT_MESSAGE);
    expect(mockRouter.asPath).toBe("/current");
  });

  it("navigates when the user confirms", async () => {
    confirm.mockReturnValue(true);
    renderWarning({ enabled: true, message: "Discard the query?" });

    await act(() => mockRouter.push("/other"));

    expect(confirm).toHaveBeenCalledWith("Discard the query?");
    expect(mockRouter.asPath).toBe("/other");
  });

  it("ignores a navigation to the page it is already on", async () => {
    confirm.mockReturnValue(false);
    renderWarning({ enabled: true });

    await act(() => mockRouter.push("/current"));

    expect(confirm).not.toHaveBeenCalled();
  });

  it("does not warn about navigations the caller performs itself", async () => {
    confirm.mockReturnValue(false);
    const { result } = renderWarning({ enabled: true });

    await act(() => result.current.navigateWithoutWarning("/other"));

    expect(confirm).not.toHaveBeenCalled();
    expect(mockRouter.asPath).toBe("/other");
  });

  it("subscribes once and still sees the latest state", async () => {
    const on = jest.spyOn(mockRouter.events, "on");
    confirm.mockReturnValue(false);
    const { rerender } = renderWarning({ enabled: false });

    rerender({ enabled: false });
    rerender({ enabled: true });

    expect(
      on.mock.calls.filter(([event]) => event === "routeChangeStart"),
    ).toHaveLength(1);
    await expect(mockRouter.push("/other")).rejects.toBe(
      "Route change aborted",
    );
  });

  it("warns before the page is unloaded", () => {
    const { rerender } = renderWarning({ enabled: false });

    const unload = () => {
      const event = new Event("beforeunload", { cancelable: true });
      window.dispatchEvent(event);
      return event.defaultPrevented;
    };

    expect(unload()).toBe(false);
    rerender({ enabled: true });
    expect(unload()).toBe(true);
  });

  it("restores the address bar when a back/forward is cancelled", () => {
    const historyState = { __N: true, as: "/current" };
    window.history.pushState(historyState, "", "/current");
    confirm.mockReturnValue(false);
    const popStateCallback = spyOnPopState();
    renderWarning({ enabled: true });

    expect(popStateCallback()({ as: "/other" })).toBe(false);

    expect(window.location.pathname).toBe("/current");
    expect(window.history.state).toEqual(historyState);
  });

  it("allows a back/forward the user confirms", () => {
    confirm.mockReturnValue(true);
    const popStateCallback = spyOnPopState();
    renderWarning({ enabled: true });

    expect(popStateCallback()({ as: "/other" })).toBe(true);
  });

  it("allows a back/forward while disabled", () => {
    const popStateCallback = spyOnPopState();
    renderWarning({ enabled: false });

    expect(popStateCallback()({ as: "/other" })).toBe(true);
    expect(confirm).not.toHaveBeenCalled();
  });
});
