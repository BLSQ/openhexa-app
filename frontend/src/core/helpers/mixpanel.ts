import mixpanel from "mixpanel-browser";
import { DEFAULT_MIXPANEL_API_HOST, getPublicEnv } from "./runtimeConfig";

const NEW_USER_WINDOW_DAYS = 7;
// Replays target the onboarding experience: only a user's first few sessions
// are worth recording, even within the new-user window.
const ONBOARDING_MAX_SESSIONS = 3;
const SESSION_COUNT_KEY_PREFIX = "hexa_replay_session_count";
const SESSION_MARKER_KEY_PREFIX = "hexa_replay_session_counted";

// Routes where we never want to capture a session replay. The pipeline code
// editor and notebooks can render user-supplied credentials or PHI; auth flows
// contain passwords and MFA codes; account settings handle 2FA secrets.
const SENSITIVE_ROUTE_PATTERNS: RegExp[] = [
  /^\/login/,
  /^\/register/,
  /^\/signup/,
  // Covers /auth/password_reset and /auth/reset/<uid>/<token>.
  /^\/auth\//,
  /^\/user\/account/,
  /^\/workspaces\/[^/]+\/pipelines\/[^/]+\/code/,
  /^\/workspaces\/[^/]+\/notebooks/,
  // Connection forms hold credentials and secrets. Every text node is already
  // masked; excluding the route entirely is a second, coarser layer on top.
  /^\/workspaces\/[^/]+\/connections/,
];

let initialized = false;

export interface MixpanelUser {
  id: string;
  email: string;
  displayName: string;
  dateJoined: string;
  analyticsEnabled: boolean;
}

export function initMixpanel(): void {
  if (initialized) return;
  if (typeof window === "undefined") return;

  const { MIXPANEL_TOKEN, MIXPANEL_API_HOST, DISABLE_ANALYTICS } =
    getPublicEnv();
  if (DISABLE_ANALYTICS === "true") return;
  if (!MIXPANEL_TOKEN) return;

  // The Python SDK accepts a bare hostname for api_host while mixpanel-browser
  // requires a full URL with scheme — without it the SDK treats the value as a
  // relative path and posts to the current origin. Normalize so the same env
  // var works for both.
  const host = MIXPANEL_API_HOST || DEFAULT_MIXPANEL_API_HOST;
  const apiHost = /^https?:\/\//.test(host) ? host : `https://${host}`;

  mixpanel.init(MIXPANEL_TOKEN, {
    api_host: apiHost,
    // Pageviews only: no clicks, inputs, scrolls or submits. "url-with-path"
    // re-fires on SPA route changes but ignores query-string and hash noise.
    autocapture: {
      pageview: "url-with-path",
      click: false,
      input: false,
      scroll: false,
      submit: false,
      capture_text_content: false,
    },
    // Session replay disabled by default; opt-in per session via applyReplayGate.
    record_sessions_percent: 0,
    record_idle_timeout_ms: 600_000,
    record_min_ms: 2_000,
    // Mask all text and inputs by default; defense in depth on top of the
    // sensitive-route exclusions below.
    record_mask_text_selector: "*",
    // Setting this key replaces the SDK default rather than extending it, so
    // "img, video, audio" is repeated here.
    // data-mp-no-record is an opt-out hook that nothing carries today. It is
    // meant for sensitive elements on routes we still record, such as the
    // revealed password in SecretField on /databases, which currently only
    // record_mask_text_selector hides.
    record_block_selector: "img, video, audio, [data-mp-no-record]",
    persistence: "localStorage",
    ignore_dnt: false,
  });
  initialized = true;
}

export function identifyUser(user: MixpanelUser): void {
  if (!initialized) return;

  if (!user.analyticsEnabled) {
    mixpanel.opt_out_tracking();
    return;
  }
  // opt_in_tracking fires a $opt_in event each call; only call it when the
  // state actually changes to avoid one noise event per page load.
  if (!mixpanel.has_opted_in_tracking()) {
    mixpanel.opt_in_tracking();
  }
  mixpanel.identify(user.id);
  mixpanel.people.set({
    $email: user.email,
    $name: user.displayName,
    $created: user.dateJoined,
  });
}

export function isNewUser(dateJoined: string): boolean {
  const joined = new Date(dateJoined).getTime();
  if (Number.isNaN(joined)) return false;
  const ageMs = Date.now() - joined;
  return ageMs < NEW_USER_WINDOW_DAYS * 24 * 60 * 60 * 1000;
}

export function isSensitiveRoute(pathname: string): boolean {
  return SENSITIVE_ROUTE_PATTERNS.some((rx) => rx.test(pathname));
}

export function isWithinOnboardingSessions(userId: string): boolean {
  // localStorage persists the per-user session count across visits while the
  // sessionStorage marker ensures each browser session is counted only once,
  // even though the gate re-runs on every route change.
  try {
    const countKey = `${SESSION_COUNT_KEY_PREFIX}:${userId}`;
    const markerKey = `${SESSION_MARKER_KEY_PREFIX}:${userId}`;
    let count = Number(window.localStorage.getItem(countKey) ?? "0");
    if (!Number.isFinite(count) || count < 0) count = 0;
    if (!window.sessionStorage.getItem(markerKey)) {
      count += 1;
      window.localStorage.setItem(countKey, String(count));
      window.sessionStorage.setItem(markerKey, "1");
    }
    return count <= ONBOARDING_MAX_SESSIONS;
  } catch {
    // Storage can be unavailable (private browsing, blocked cookies); fail
    // closed so a broken counter never records more than intended.
    return false;
  }
}

export function applyReplayGate(
  user: MixpanelUser | null,
  pathname: string,
): void {
  if (!initialized) return;
  if (!user || !user.analyticsEnabled) {
    mixpanel.stop_session_recording();
    return;
  }
  if (!isNewUser(user.dateJoined)) {
    mixpanel.stop_session_recording();
    return;
  }
  if (!isWithinOnboardingSessions(user.id)) {
    mixpanel.stop_session_recording();
    return;
  }
  if (isSensitiveRoute(pathname)) {
    mixpanel.stop_session_recording();
    return;
  }
  mixpanel.start_session_recording();
}

// Exported so tests can reset between cases.
export function __resetForTests(): void {
  initialized = false;
}
