import { getCookie } from "cookies-next";

// A single reusable hidden iframe receives the POST response. A successful
// attachment is handed to the browser's download manager and leaves both the
// iframe and the page untouched; a failed response lands in the iframe instead
// of navigating the whole app away.
const DOWNLOAD_FRAME_NAME = "data-studio-csv-download-frame";

// The backend signals "download began" the instant it starts streaming the
// attachment by setting a short-lived cookie whose NAME carries this prefix plus
// our per-download token — our only positive signal, since a successful download
// never fires the iframe's load event. A per-token name (rather than one shared
// cookie holding the token as its value) lets concurrent downloads each wait on
// their own signal without clobbering one another. Must match the backend's
// f"csvDownloadToken-{token}" in databases/views.py.
const SUCCESS_COOKIE_PREFIX = "csvDownloadToken-";
const POLL_INTERVAL_MS = 250;
// Generous ceiling — longer than the backend download statement timeout — so a
// legitimately slow export is not reported as failed while it is still running.
const DOWNLOAD_TIMEOUT_MS = 6 * 60 * 1000;

const ensureDownloadFrame = (): HTMLIFrameElement => {
  const existing = document.querySelector<HTMLIFrameElement>(
    `iframe[name="${DOWNLOAD_FRAME_NAME}"]`,
  );
  if (existing) {
    return existing;
  }
  const iframe = document.createElement("iframe");
  iframe.name = DOWNLOAD_FRAME_NAME;
  iframe.setAttribute("aria-hidden", "true");
  iframe.style.display = "none";
  document.body.appendChild(iframe);
  return iframe;
};

const appendHiddenField = (
  form: HTMLFormElement,
  name: string,
  value: string,
) => {
  const input = document.createElement("input");
  input.type = "hidden";
  input.name = name;
  input.value = value;
  form.appendChild(input);
};

const clearCookie = (name: string) => {
  document.cookie = `${name}=; Max-Age=0; path=/`;
};

// Downloads the full result of a SQL query by POSTing it to the backend, which
// streams a CSV attachment back. A form POST (rather than fetch) lets the
// browser stream the response straight to disk, so even very large exports never
// have to be held in browser memory. maxRows is intentionally not sent: the
// download is always the entire result set.
//
// The returned promise resolves once the download has demonstrably started and
// rejects (with the server's message when readable) if the backend returns an
// error instead — see SUCCESS_COOKIE_PREFIX and the iframe load handler below.
export const downloadQueryCsv = (
  workspaceSlug: string,
  query: string,
): Promise<void> => {
  const apiBasePath = process.env.NEXT_PUBLIC_API_BASE_PATH ?? "";
  const csrfToken = getCookie("csrftoken");
  const iframe = ensureDownloadFrame();

  const token = `${Date.now()}-${Math.random().toString(36).slice(2)}`;
  const successCookie = `${SUCCESS_COOKIE_PREFIX}${token}`;

  const form = document.createElement("form");
  form.method = "POST";
  form.action = `${apiBasePath}/databases/${encodeURIComponent(
    workspaceSlug,
  )}/query/download/`;
  form.target = DOWNLOAD_FRAME_NAME;
  form.style.display = "none";

  appendHiddenField(form, "query", query);
  appendHiddenField(form, "download_token", token);
  if (typeof csrfToken === "string") {
    appendHiddenField(form, "csrfmiddlewaretoken", csrfToken);
  }

  return new Promise<void>((resolve, reject) => {
    let settled = false;
    const settle = (action: () => void) => {
      if (settled) {
        return;
      }
      settled = true;
      clearInterval(poll);
      clearTimeout(timeout);
      iframe.removeEventListener("load", onLoad);
      action();
    };

    // An error response navigates the iframe (load fires); a successful download
    // does not. The iframe's initial empty about:blank document is ignored.
    const onLoad = () => {
      let message: string | null;
      try {
        message = iframe.contentDocument?.body?.textContent?.trim() || null;
      } catch {
        // Cross-origin error page: a definite failure whose body we cannot read.
        message = "";
      }
      if (message === null) {
        return;
      }
      settle(() => reject(new Error(message || "Export failed")));
    };
    iframe.addEventListener("load", onLoad);

    const poll = setInterval(() => {
      if (getCookie(successCookie)) {
        clearCookie(successCookie);
        settle(resolve);
      }
    }, POLL_INTERVAL_MS);

    const timeout = setTimeout(() => {
      settle(() => reject(new Error("Export timed out")));
    }, DOWNLOAD_TIMEOUT_MS);

    document.body.appendChild(form);
    form.submit();
    form.remove();
  });
};
