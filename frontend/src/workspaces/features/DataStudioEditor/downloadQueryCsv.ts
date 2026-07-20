import { getCookie } from "cookies-next";

// A single reusable hidden iframe receives the POST response. A successful
// attachment is handed to the browser's download manager and leaves both the
// iframe and the page untouched; a failed response lands in the iframe instead
// of navigating the whole app away.
const DOWNLOAD_FRAME_NAME = "data-studio-csv-download-frame";

const ensureDownloadFrame = () => {
  const existing = document.querySelector(
    `iframe[name="${DOWNLOAD_FRAME_NAME}"]`,
  );
  if (existing) {
    return;
  }
  const iframe = document.createElement("iframe");
  iframe.name = DOWNLOAD_FRAME_NAME;
  iframe.setAttribute("aria-hidden", "true");
  iframe.style.display = "none";
  document.body.appendChild(iframe);
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

// Downloads the full result of a SQL query by POSTing it to the backend, which
// streams a CSV attachment back. A form POST (rather than fetch) lets the
// browser stream the response straight to disk, so even very large exports never
// have to be held in browser memory. maxRows is intentionally not sent: the
// download is always the entire result set.
export const downloadQueryCsv = (workspaceSlug: string, query: string) => {
  const apiBasePath = process.env.NEXT_PUBLIC_API_BASE_PATH ?? "";
  const csrfToken = getCookie("csrftoken");

  ensureDownloadFrame();

  const form = document.createElement("form");
  form.method = "POST";
  form.action = `${apiBasePath}/databases/${encodeURIComponent(
    workspaceSlug,
  )}/query/download/`;
  form.target = DOWNLOAD_FRAME_NAME;
  form.style.display = "none";

  appendHiddenField(form, "query", query);
  if (typeof csrfToken === "string") {
    appendHiddenField(form, "csrfmiddlewaretoken", csrfToken);
  }

  document.body.appendChild(form);
  form.submit();
  form.remove();
};
