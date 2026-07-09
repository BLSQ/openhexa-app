(function () {
  "use strict";

  var OPENHEXA_BASE = "{{ base_url|escapejs }}";
  var GRAPHQL_PATH = "/graphql/";
  var MESSAGE_TYPE = "openhexa-dev-auth";

  // Run once, and only during local development. When the webapp is served by
  // OpenHEXA itself, window.OPENHEXA is injected and /graphql/ already works
  // same-origin — so the shim stays out of the way, which makes it safe to
  // leave this tag in the deployed index.html.
  if (window.__OPENHEXA_DEV_ACTIVE__) {
    return;
  }
  window.__OPENHEXA_DEV_ACTIVE__ = true;

  var isFilePage = window.location.protocol === "file:";
  var LOCAL_HOSTS = ["localhost", "127.0.0.1", "::1", "[::1]"];
  if (!isFilePage && LOCAL_HOSTS.indexOf(window.location.hostname) === -1) {
    return;
  }

  // --- Which web app to connect to -------------------------------------------
  // Read from data-workspace-slug / data-webapp-slug, ?workspaceSlug=&webappSlug=
  // on the script src, or window.OPENHEXA_DEV = { workspaceSlug, webappSlug }.
  // When both aren't given, dev-auth shows a picker.
  var config = window.OPENHEXA_DEV || {};
  var scriptEl = document.currentScript;

  function option(dataAttr, key) {
    if (config[key]) {
      return config[key];
    }
    if (!scriptEl) {
      return null;
    }
    var attr = scriptEl.getAttribute("data-" + dataAttr);
    if (attr) {
      return attr;
    }
    try {
      return new URL(scriptEl.src, window.location.href).searchParams.get(key);
    } catch (e) {
      return null;
    }
  }

  var workspaceSlug = option("workspace-slug", "workspaceSlug");
  var webappSlug = option("webapp-slug", "webappSlug");
  var pinned = !!(workspaceSlug && webappSlug);

  var baseOrigin = new URL(OPENHEXA_BASE).origin;
  // file:// pages report location.origin inconsistently ("null" vs "file://");
  // normalise to "null" so the backend treats it as an opaque origin.
  var pageOrigin = isFilePage ? "null" : window.location.origin;

  var authUrl =
    OPENHEXA_BASE + "/webapps/dev-auth/?origin=" + encodeURIComponent(pageOrigin);
  if (pinned) {
    authUrl +=
      "&workspaceSlug=" +
      encodeURIComponent(workspaceSlug) +
      "&webappSlug=" +
      encodeURIComponent(webappSlug);
  }

  // --- Per-tab credential cache ----------------------------------------------
  // A refresh reuses the cached credential instead of re-running the handshake.
  var CACHE_KEY =
    "openhexa_dev:" + (pinned ? workspaceSlug + "/" + webappSlug : "picker");

  function readCache() {
    try {
      return JSON.parse(sessionStorage.getItem(CACHE_KEY) || "null");
    } catch (e) {
      return null;
    }
  }
  function writeCache(value) {
    try {
      sessionStorage.setItem(CACHE_KEY, JSON.stringify(value));
    } catch (e) {
      /* storage unavailable — fall back to re-handshaking each load */
    }
  }
  function clearCache() {
    try {
      sessionStorage.removeItem(CACHE_KEY);
    } catch (e) {
      /* ignore */
    }
  }

  // --- Connection state ------------------------------------------------------
  // `preview` resolves to the preview URL once connected. /graphql/ calls await
  // it, so a request made before connecting simply pends (never forces a popup).
  var preview, resolvePreview;
  function resetPreview() {
    preview = new Promise(function (resolve) {
      resolvePreview = resolve;
    });
  }
  resetPreview();

  var connectedKey = null; // "<workspace>/<webapp>" currently connected to
  var reconnecting = false;

  function setContext(data) {
    window.OPENHEXA = Object.freeze({
      workspaceSlug: data.workspaceSlug,
      webappSlug: data.webappSlug,
      isPublic: false,
    });
  }

  // dev-auth posts the credential back here. The credential IS the preview host,
  // so only trust messages that genuinely came from OpenHEXA.
  window.addEventListener("message", function (event) {
    if (event.origin !== baseOrigin) {
      return;
    }
    var data = event.data || {};
    if (data.type !== MESSAGE_TYPE) {
      return;
    }

    writeCache(data);
    setContext(data);

    var key = data.workspaceSlug + "/" + data.webappSlug;
    if (reconnecting && connectedKey && key !== connectedKey) {
      // Switched web app → reload so the page re-runs against the new one.
      window.location.reload();
      return;
    }
    reconnecting = false;
    connectedKey = key;
    showPill(data.workspaceSlug, data.webappSlug);
    console.info("[openhexa] Local dev connected:", key);
    resolvePreview(data.previewUrl);
  });

  // Opens the authenticated handshake popup. Must run from a click, or the
  // browser blocks it — then we fall back to the Connect button.
  function connect() {
    if (!window.open(authUrl, "openhexa-dev-auth", "width=480,height=680")) {
      showConnectButton();
    }
  }

  // Clear the credential and connect again (the picker reappears when the web
  // app isn't pinned). Bound to the pill, so it runs from a user gesture.
  function reconnect() {
    reconnecting = true;
    clearCache();
    resetPreview();
    connect();
  }

  // --- Corner overlay: Connect button / connected pill -----------------------
  var PILL_STYLE =
    "position:fixed;bottom:16px;right:16px;z-index:2147483647;padding:8px 14px;" +
    "border-radius:6px;font:500 13px system-ui,sans-serif;box-shadow:0 1px 4px rgba(0,0,0,.2);";
  var overlay = null;

  function setOverlay(node) {
    if (overlay) {
      overlay.remove();
    }
    overlay = node;
    if (node) {
      (document.body || document.documentElement).appendChild(node);
    }
  }

  function span(text, style) {
    var el = document.createElement("span");
    el.textContent = text;
    el.setAttribute("style", style);
    return el;
  }

  function showConnectButton() {
    var button = document.createElement("button");
    button.textContent = "Connect to OpenHEXA";
    button.setAttribute(
      "style",
      PILL_STYLE + "border:none;background:#2563eb;color:#fff;cursor:pointer;",
    );
    button.addEventListener("click", connect);
    setOverlay(button);
  }

  function showPill(workspaceSlug, webappSlug) {
    var pill = document.createElement("div");
    pill.setAttribute(
      "style",
      PILL_STYLE +
        "border:none;background:#111827;color:#fff;display:flex;align-items:center;gap:10px;",
    );

    var path = document.createElement("span");
    path.setAttribute(
      "style",
      "font-family:'SF Mono',SFMono-Regular,ui-monospace,Menlo,monospace;",
    );
    path.appendChild(span(workspaceSlug, "opacity:.7;"));
    path.appendChild(span("/", "opacity:.5;margin:0 1px;"));
    path.appendChild(span(webappSlug, "color:#93c5fd;font-weight:600;"));

    var action = document.createElement("button");
    // Pinned web app → only reconnect; picker → switch to a different one.
    action.textContent = pinned ? "Reconnect" : "Switch";
    action.title = pinned ? "Get a fresh credential" : "Choose a different web app";
    action.setAttribute(
      "style",
      "background:transparent;border:none;color:#93c5fd;font:inherit;cursor:pointer;" +
        "padding:0;text-decoration:underline;",
    );
    action.addEventListener("click", reconnect);

    pill.appendChild(span("OpenHEXA", "opacity:.6;"));
    pill.appendChild(path);
    pill.appendChild(action);
    setOverlay(pill);
  }

  // --- Bootstrap -------------------------------------------------------------
  // Reuse a cached credential silently; otherwise show the Connect button and
  // wait for a click — never auto-open the popup.
  function start() {
    var cached = readCache();
    if (cached && cached.previewUrl) {
      setContext(cached);
      connectedKey = cached.workspaceSlug + "/" + cached.webappSlug;
      showPill(cached.workspaceSlug, cached.webappSlug);
      resolvePreview(cached.previewUrl);
    } else {
      showConnectButton();
    }
  }
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", start);
  } else {
    start();
  }

  // --- Route /graphql/ through the preview host ------------------------------
  var nativeFetch = window.fetch.bind(window);

  function isGraphqlRequest(url) {
    try {
      var parsed = new URL(url, window.location.href);
      return (
        parsed.pathname === GRAPHQL_PATH &&
        parsed.origin === window.location.origin
      );
    } catch (e) {
      return false;
    }
  }

  function proxyGraphql(input, init, retried) {
    return preview.then(function (previewUrl) {
      var target = previewUrl.replace(/\/$/, "") + GRAPHQL_PATH;
      var opts = Object.assign({}, init, { credentials: "omit" });
      var request =
        typeof input === "string"
          ? nativeFetch(target, opts)
          : nativeFetch(new Request(target, input), opts);
      return request.then(function (res) {
        // An expired/rotated credential no longer maps to a session, so its host
        // 404s (or 401s): drop it and prompt to reconnect (no auto-popup). The
        // retry waits until the user clicks Connect.
        if (!retried && (res.status === 404 || res.status === 401)) {
          reconnecting = false;
          clearCache();
          resetPreview();
          showConnectButton();
          return proxyGraphql(input, init, true);
        }
        return res;
      });
    });
  }

  window.fetch = function (input, init) {
    var url = typeof input === "string" ? input : input && input.url;
    if (!url || !isGraphqlRequest(url)) {
      return nativeFetch(input, init);
    }
    return proxyGraphql(input, init, false);
  };
})();
