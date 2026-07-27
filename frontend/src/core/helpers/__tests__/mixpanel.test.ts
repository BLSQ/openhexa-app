import mixpanel from "mixpanel-browser";
import {
  __resetForTests,
  applyReplayGate,
  identifyUser,
  initMixpanel,
  isNewUser,
  isSensitiveRoute,
  isWithinOnboardingSessions,
  MixpanelUser,
} from "../mixpanel";

jest.mock("mixpanel-browser", () => ({
  __esModule: true,
  default: {
    init: jest.fn(),
    identify: jest.fn(),
    opt_in_tracking: jest.fn(),
    opt_out_tracking: jest.fn(),
    has_opted_in_tracking: jest.fn().mockReturnValue(false),
    start_session_recording: jest.fn(),
    stop_session_recording: jest.fn(),
    people: {
      set: jest.fn(),
    },
  },
}));

jest.mock("../runtimeConfig", () => ({
  ...jest.requireActual("../runtimeConfig"),
  getPublicEnv: jest.fn(),
}));

import { getPublicEnv } from "../runtimeConfig";
const getPublicEnvMock = getPublicEnv as jest.Mock;

const baseEnv = {
  OPENHEXA_BACKEND_URL: "",
  SENTRY_DSN: "",
  SENTRY_ENVIRONMENT: "",
  SENTRY_TRACES_SAMPLE_RATE: "1",
  DISABLE_ANALYTICS: "",
  CONSOLE_URL: "",
  MIXPANEL_TOKEN: "test-token",
  MIXPANEL_API_HOST: "api-eu.mixpanel.com",
};

function newUser(overrides: Partial<MixpanelUser> = {}): MixpanelUser {
  return {
    id: "user-1",
    email: "u@example.org",
    displayName: "U Example",
    dateJoined: new Date().toISOString(),
    analyticsEnabled: true,
    ...overrides,
  };
}

function daysAgo(days: number): string {
  return new Date(Date.now() - days * 24 * 60 * 60 * 1000).toISOString();
}

beforeEach(() => {
  jest.clearAllMocks();
  __resetForTests();
  window.localStorage.clear();
  window.sessionStorage.clear();
  getPublicEnvMock.mockReturnValue(baseEnv);
});

describe("initMixpanel", () => {
  it("initializes the SDK with the configured host and pageview-only autocapture", () => {
    initMixpanel();
    expect(mixpanel.init).toHaveBeenCalledTimes(1);
    const [token, options] = (mixpanel.init as jest.Mock).mock.calls[0];
    expect(token).toBe("test-token");
    expect(options.api_host).toBe("https://api-eu.mixpanel.com");
    expect(options.autocapture).toEqual({
      pageview: "url-with-path",
      click: false,
      input: false,
      scroll: false,
      submit: false,
      capture_text_content: false,
    });
    expect(options.record_sessions_percent).toBe(0);
    expect(options.record_mask_text_selector).toBe("*");
  });

  it("passes through an api_host that already includes a scheme", () => {
    getPublicEnvMock.mockReturnValue({
      ...baseEnv,
      MIXPANEL_API_HOST: "https://api-eu.mixpanel.com",
    });
    initMixpanel();
    const [, options] = (mixpanel.init as jest.Mock).mock.calls[0];
    expect(options.api_host).toBe("https://api-eu.mixpanel.com");
  });

  it("falls back to the EU host when MIXPANEL_API_HOST is empty", () => {
    getPublicEnvMock.mockReturnValue({ ...baseEnv, MIXPANEL_API_HOST: "" });
    initMixpanel();
    const [, options] = (mixpanel.init as jest.Mock).mock.calls[0];
    expect(options.api_host).toBe("https://api-eu.mixpanel.com");
  });

  it("skips init when MIXPANEL_TOKEN is empty", () => {
    getPublicEnvMock.mockReturnValue({ ...baseEnv, MIXPANEL_TOKEN: "" });
    initMixpanel();
    expect(mixpanel.init).not.toHaveBeenCalled();
  });

  it("skips init when DISABLE_ANALYTICS is true", () => {
    getPublicEnvMock.mockReturnValue({
      ...baseEnv,
      DISABLE_ANALYTICS: "true",
    });
    initMixpanel();
    expect(mixpanel.init).not.toHaveBeenCalled();
  });

  it("is idempotent (second call is a no-op)", () => {
    initMixpanel();
    initMixpanel();
    expect(mixpanel.init).toHaveBeenCalledTimes(1);
  });
});

describe("identifyUser", () => {
  it("opts out and skips identify when analyticsEnabled is false", () => {
    initMixpanel();
    identifyUser(newUser({ analyticsEnabled: false }));
    expect(mixpanel.opt_out_tracking).toHaveBeenCalledTimes(1);
    expect(mixpanel.identify).not.toHaveBeenCalled();
  });

  it("skips opt_in_tracking when already opted in", () => {
    (mixpanel.has_opted_in_tracking as jest.Mock).mockReturnValue(true);
    initMixpanel();
    identifyUser(newUser());
    expect(mixpanel.opt_in_tracking).not.toHaveBeenCalled();
    expect(mixpanel.identify).toHaveBeenCalled();
    (mixpanel.has_opted_in_tracking as jest.Mock).mockReturnValue(false);
  });

  it("opts in, identifies, and sets profile when analyticsEnabled is true", () => {
    initMixpanel();
    const u = newUser();
    identifyUser(u);
    expect(mixpanel.opt_in_tracking).toHaveBeenCalledTimes(1);
    expect(mixpanel.identify).toHaveBeenCalledWith(u.id);
    expect(mixpanel.people.set).toHaveBeenCalledWith({
      $email: u.email,
      $name: u.displayName,
      $created: u.dateJoined,
    });
  });

  it("is a no-op when not initialized", () => {
    identifyUser(newUser());
    expect(mixpanel.identify).not.toHaveBeenCalled();
  });
});

describe("isNewUser", () => {
  it("returns true within the 7 day window", () => {
    expect(isNewUser(daysAgo(0))).toBe(true);
    expect(isNewUser(daysAgo(6))).toBe(true);
  });

  it("returns false outside the 7 day window", () => {
    expect(isNewUser(daysAgo(8))).toBe(false);
    expect(isNewUser(daysAgo(365))).toBe(false);
  });

  it("returns false for unparseable dates", () => {
    expect(isNewUser("not-a-date")).toBe(false);
  });
});

describe("isSensitiveRoute", () => {
  it.each([
    "/login",
    "/register",
    "/forgot-password",
    "/account",
    "/account/security",
    "/workspaces/abc/pipelines/xyz/code",
    "/workspaces/abc/notebooks",
    "/workspaces/abc/notebooks/foo",
    "/workspaces/abc/connections",
    "/workspaces/abc/connections/conn-1",
  ])("marks %s as sensitive", (path) => {
    expect(isSensitiveRoute(path)).toBe(true);
  });

  it.each([
    "/",
    "/workspaces/abc",
    "/workspaces/abc/datasets/ds1",
    "/workspaces/abc/pipelines/xyz",
    "/workspaces/abc/pipelines/xyz/runs",
  ])("marks %s as non-sensitive", (path) => {
    expect(isSensitiveRoute(path)).toBe(false);
  });
});

describe("isWithinOnboardingSessions", () => {
  it("allows the first three sessions", () => {
    for (let session = 1; session <= 3; session++) {
      window.sessionStorage.clear();
      expect(isWithinOnboardingSessions("user-1")).toBe(true);
    }
  });

  it("counts a session only once despite repeated calls", () => {
    isWithinOnboardingSessions("user-1");
    isWithinOnboardingSessions("user-1");
    isWithinOnboardingSessions("user-1");
    expect(
      window.localStorage.getItem("hexa_replay_session_count:user-1"),
    ).toBe("1");
  });

  it("blocks from the fourth session on", () => {
    for (let session = 1; session <= 3; session++) {
      window.sessionStorage.clear();
      isWithinOnboardingSessions("user-1");
    }
    window.sessionStorage.clear();
    expect(isWithinOnboardingSessions("user-1")).toBe(false);
  });

  it("tracks sessions per user", () => {
    for (let session = 1; session <= 4; session++) {
      window.sessionStorage.clear();
      isWithinOnboardingSessions("user-1");
    }
    expect(isWithinOnboardingSessions("user-2")).toBe(true);
  });

  it("fails closed when storage throws", () => {
    const spy = jest
      .spyOn(Storage.prototype, "getItem")
      .mockImplementation(() => {
        throw new Error("storage disabled");
      });
    expect(isWithinOnboardingSessions("user-1")).toBe(false);
    spy.mockRestore();
  });
});

describe("applyReplayGate", () => {
  beforeEach(() => initMixpanel());

  it("stops recording when user is null", () => {
    applyReplayGate(null, "/workspaces/abc");
    expect(mixpanel.stop_session_recording).toHaveBeenCalledTimes(1);
    expect(mixpanel.start_session_recording).not.toHaveBeenCalled();
  });

  it("stops recording when analyticsEnabled is false", () => {
    applyReplayGate(newUser({ analyticsEnabled: false }), "/workspaces/abc");
    expect(mixpanel.stop_session_recording).toHaveBeenCalledTimes(1);
    expect(mixpanel.start_session_recording).not.toHaveBeenCalled();
  });

  it("stops recording when user is not new", () => {
    applyReplayGate(newUser({ dateJoined: daysAgo(60) }), "/workspaces/abc");
    expect(mixpanel.stop_session_recording).toHaveBeenCalledTimes(1);
    expect(mixpanel.start_session_recording).not.toHaveBeenCalled();
  });

  it("stops recording on sensitive route even for a new user", () => {
    applyReplayGate(newUser(), "/account");
    expect(mixpanel.stop_session_recording).toHaveBeenCalledTimes(1);
    expect(mixpanel.start_session_recording).not.toHaveBeenCalled();
  });

  it("starts recording for a new opted-in user on a non-sensitive route", () => {
    applyReplayGate(newUser(), "/workspaces/abc/datasets/ds1");
    expect(mixpanel.start_session_recording).toHaveBeenCalledTimes(1);
  });

  it("stops recording once the onboarding session budget is spent", () => {
    for (let session = 1; session <= 3; session++) {
      window.sessionStorage.clear();
      isWithinOnboardingSessions("user-1");
    }
    window.sessionStorage.clear();
    applyReplayGate(newUser(), "/workspaces/abc/datasets/ds1");
    expect(mixpanel.stop_session_recording).toHaveBeenCalledTimes(1);
    expect(mixpanel.start_session_recording).not.toHaveBeenCalled();
  });

  it("is a no-op when not initialized", () => {
    __resetForTests();
    applyReplayGate(newUser(), "/workspaces/abc");
    expect(mixpanel.start_session_recording).not.toHaveBeenCalled();
    expect(mixpanel.stop_session_recording).not.toHaveBeenCalled();
  });
});
