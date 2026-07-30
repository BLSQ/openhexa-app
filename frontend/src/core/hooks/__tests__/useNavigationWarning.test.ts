import { act, renderHook } from "@testing-library/react";
import mockRouter from "next-router-mock";
import useNavigationWarning, {
  NavigationAbortedError,
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
const spyOnPopState = () => jest.spyOn(mockRouter, "beforePopState");
const registeredPopState = (spy: ReturnType<typeof spyOnPopState>) => {
  // Latest rather than first: the hook re-registers whenever the guard is
  // rearmed, and hands back a pass-through on unmount.
  const lastCall = spy.mock.calls.at(-1) as unknown as [PopStateCallback];
  return lastCall[0];
};

const dispatchUnload = () => {
  const event = new Event("beforeunload", { cancelable: true });
  window.dispatchEvent(event);
  return event.defaultPrevented;
};

beforeEach(() => {
  mockRouter.setCurrentUrl("/current");
});

describe("useNavigationWarning", () => {
  // Aborting leaves an unhandled rejection that only Sentry sees, so nothing
  // else fails if this name drifts away from the `ignoreErrors` entry in
  // sentry.client.config.ts -- every declined prompt would just start being
  // reported as an error.
  it("names the abort error after the Sentry ignoreErrors entry", () => {
    expect(new NavigationAbortedError().name).toBe("NavigationAbortedError");
  });

  it("lets navigation through when disabled", async () => {
    renderWarning({ enabled: false });

    await act(() => mockRouter.push("/other"));

    expect(mockRouter.asPath).toBe("/other");
    expect(confirm).not.toHaveBeenCalled();
  });

  it("keeps the user on the page when they cancel", async () => {
    confirm.mockReturnValue(false);
    renderWarning({ enabled: true });

    await expect(mockRouter.push("/other")).rejects.toBeInstanceOf(
      NavigationAbortedError,
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

  it("ignores a shallow navigation, which keeps the page mounted", async () => {
    confirm.mockReturnValue(false);
    renderWarning({ enabled: true });

    await act(() =>
      mockRouter.push("/current?tab=results", undefined, { shallow: true }),
    );

    expect(confirm).not.toHaveBeenCalled();
    expect(mockRouter.asPath).toBe("/current?tab=results");
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

  it("does not resubscribe on renders that change nothing", async () => {
    const on = jest.spyOn(mockRouter.events, "on");
    confirm.mockReturnValue(false);
    const { rerender } = renderWarning({ enabled: true });

    // Stands in for the editor re-rendering on every keystroke of a dirty buffer:
    // `enabled` holds the same value, so the listeners have to stay put.
    rerender({ enabled: true });
    rerender({ enabled: true });

    expect(
      on.mock.calls.filter(([event]) => event === "routeChangeStart"),
    ).toHaveLength(1);
    await expect(mockRouter.push("/other")).rejects.toBeInstanceOf(
      NavigationAbortedError,
    );
  });

  it("registers nothing at all while disabled", () => {
    const popState = spyOnPopState();
    const addEventListener = jest.spyOn(window, "addEventListener");
    const { rerender } = renderWarning({ enabled: false });

    expect(popState).not.toHaveBeenCalled();
    expect(addEventListener).not.toHaveBeenCalledWith(
      "beforeunload",
      expect.any(Function),
    );

    rerender({ enabled: true });

    expect(popState).toHaveBeenCalled();
    expect(addEventListener).toHaveBeenCalledWith(
      "beforeunload",
      expect.any(Function),
    );
  });

  it("warns before the page is unloaded", () => {
    const { rerender } = renderWarning({ enabled: false });

    expect(dispatchUnload()).toBe(false);
    rerender({ enabled: true });
    expect(dispatchUnload()).toBe(true);
  });

  it("stops guarding every route once unmounted", async () => {
    confirm.mockReturnValue(false);
    const popState = spyOnPopState();
    const { unmount } = renderWarning({ enabled: true });

    unmount();

    await act(() => mockRouter.push("/other"));
    expect(confirm).not.toHaveBeenCalled();
    expect(mockRouter.asPath).toBe("/other");

    expect(dispatchUnload()).toBe(false);
    expect(registeredPopState(popState)({ as: "/elsewhere" })).toBe(true);
  });

  it("restores the address bar when a back/forward is cancelled", () => {
    const historyState = { __N: true, as: "/current" };
    window.history.pushState(historyState, "", "/current");
    confirm.mockReturnValue(false);
    const popState = spyOnPopState();
    renderWarning({ enabled: true });

    expect(registeredPopState(popState)({ as: "/other" })).toBe(false);

    expect(window.location.pathname).toBe("/current");
    expect(window.history.state).toEqual(historyState);
  });

  it("allows a back/forward the user confirms", () => {
    confirm.mockReturnValue(true);
    const popState = spyOnPopState();
    renderWarning({ enabled: true });

    expect(registeredPopState(popState)({ as: "/other" })).toBe(true);
  });
});
