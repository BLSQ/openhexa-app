<div class="hero-section">
  <h1><i class="fas fa-hexagon" style="margin-right: 0.5rem;"></i>Static Webapps</h1>
</div>
</div>

Static webapps let you host a small HTML / CSS / JavaScript bundle inside an OpenHEXA workspace and serve it on its own subdomain. They're useful for dashboards, custom data-entry forms, or any front-end that needs to live alongside your pipelines and datasets — without standing up a separate hosting environment.

OpenHEXA supports three webapp types:

- **Static** (this page): you provide the source files; OpenHEXA serves them and proxies API access for you.
- **Iframe**: OpenHEXA embeds an external URL.
- **Superset**: OpenHEXA embeds a Superset dashboard.

## Creating a static webapp

From the workspace UI: **Web Apps → Create → Static**, then either drop in your files or start from the default `index.html` template.

Programmatically: use the `create_static_webapp` MCP tool, or the GraphQL `createWebapp` mutation with a `static` source carrying a list of `{path, content}` files. An `index.html` at the root is required.

## Project structure

Files live at the paths you provide. `index.html` is the entry point; everything else (CSS, JS, images, JSON fixtures) is served as-is from the same origin.

```
index.html
app.js
style.css
assets/logo.svg
```

Reference assets with relative paths (`<script src="app.js">`, `<link href="style.css">`) so they work both in preview and once published.

## URL and subdomain

Each webapp gets a subdomain under the workspace's webapps domain — e.g. `my-webapp.webapps.example.com`. The subdomain defaults to the slug derived from the webapp name and can be edited in the webapp settings.

## Public vs private

- **Private** (default): viewers must be authenticated workspace members. The browser session cookie is what authorises requests, so private static webapps can also call OpenHEXA's GraphQL API directly (see below).
- **Public**: anyone with the URL can view the webapp. Public webapps **cannot** call the GraphQL proxy — if you need to expose workspace data publicly, generate a static export from a pipeline and serve it as a file inside the webapp.

## Calling the OpenHEXA GraphQL API

Private static webapps can call the platform's GraphQL API directly from their JavaScript code to read and write workspace data. The rest of this page covers that API in detail — public webapps and iframe webapps cannot use this endpoint.

### How it works

- **Endpoint**: `POST /graphql/` on the webapp's own URL (same-origin). For example, a webapp served at `https://my-webapp.webapps.example.com/` calls `https://my-webapp.webapps.example.com/graphql/`.
- **Authentication**: handled by the webapp session — the user's browser session cookie is attached automatically. Do not send `Authorization` headers; do not embed tokens in your code.
- **Origin check**: only requests whose `Origin` matches the webapp's own origin are allowed. Cross-site calls are rejected.
- **Scope-gated**: each webapp declares an `allowed_operations` list. Only GraphQL top-level fields covered by those scopes are allowed; everything else returns a `403`.
- **JSON body**: same as any GraphQL POST — `{"query": "...", "variables": {...}}`.

## Enabling the API on a webapp

By default a static webapp has an empty `allowed_operations` list, which means it cannot call the API. Enable scopes from the workspace UI ("Webapp settings → API access") or via the GraphQL `updateWebapp` mutation.

## Scope reference

| Scope | What it grants |
|---|---|
| `USER_READ` | `me`, `workspace` |
| `PIPELINES_READ` | `pipeline`, `pipelines`, `pipelineByCode`, `pipelineRun`, `pipelineVersion` |
| `PIPELINES_RUN` | `runPipeline`, `stopPipeline` |
| `FILES_READ` | `getFileByPath`, `readFileContent`, `prepareObjectDownload` |
| `FILES_WRITE` | `prepareObjectUpload`, `createBucketFolder`, `deleteBucketObject`, `writeFileContent` |
| `DATASETS_READ` | `dataset`, `datasets`, `datasetVersion`, `datasetLink` |
| `DATASETS_WRITE` | `createDataset`, `updateDataset`, `deleteDataset`, `createDatasetVersion`, `updateDatasetVersion`, `deleteDatasetVersion`, `createDatasetVersionFile`, `deleteDatasetLink` |

Introspection fields `__typename`, `__schema`, `__type` are always allowed.

## Exploring the schema

The fastest way to design queries for a webapp is the interactive GraphQL playground at <https://app.openhexa.org/graphql/> (or `/graphql/` on your own install).

Note that the playground shows the **full** schema, not just what the webapp proxy allows. A query that works there can still return `403` from a webapp at runtime if its top-level field isn't covered by the webapp's [scopes](#scope-reference) — cross-check before pasting into webapp code.

## The `window.OPENHEXA` global

When OpenHEXA serves your static webapp's HTML it injects a small script before `</head>` that exposes:

```js
window.OPENHEXA = Object.freeze({
  workspaceSlug: "my-workspace",   // slug of the workspace owning this webapp
  webappSlug: "my-webapp",         // this webapp's own slug
  isPublic: false,                 // true for public webapps
});
```

The examples below read `workspaceSlug` from this global, so they're copy-pasteable into any webapp without having to edit a constant. The injection only touches `text/html` responses; CSS, JS, and JSON files are untouched.

---

## Example webapps

Each example below is a complete `index.html` you can drop into a static webapp. Every example inlines the same tiny `gql()` helper so it's standalone, and reads its workspace slug from `window.OPENHEXA`.

### USER_READ — Who am I?

Displays the current user and workspace on load.

```html
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>Who am I?</title>
  <style>
    body { font-family: system-ui, sans-serif; max-width: 640px; margin: 2rem auto; padding: 0 1rem; }
    pre { background: #f5f5f5; padding: 1rem; border-radius: 4px; overflow-x: auto; }
  </style>
</head>
<body>
  <h1>Who am I?</h1>
  <pre id="out">Loading…</pre>

  <script>
    const { workspaceSlug } = window.OPENHEXA;

    async function gql(query, variables = {}) {
      const res = await fetch("/graphql/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query, variables }),
      });
      const json = await res.json();
      if (json.errors) throw new Error(json.errors.map(e => e.message).join("; "));
      return json.data;
    }

    (async () => {
      const data = await gql(`
        query($slug: String!) {
          me { user { id email displayName } }
          workspace(slug: $slug) { slug name description }
        }
      `, { slug: workspaceSlug });
      document.getElementById("out").textContent = JSON.stringify(data, null, 2);
    })();
  </script>
</body>
</html>
```

### PIPELINES_READ — List pipelines

Lists every pipeline in the workspace.

```html
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>Pipelines</title>
  <style>
    body { font-family: system-ui, sans-serif; max-width: 720px; margin: 2rem auto; padding: 0 1rem; }
    li { margin-bottom: 0.75rem; }
    code { background: #f5f5f5; padding: 0.1rem 0.3rem; border-radius: 3px; }
  </style>
</head>
<body>
  <h1>Pipelines</h1>
  <ul id="list"><li>Loading…</li></ul>

  <script>
    const { workspaceSlug } = window.OPENHEXA;

    async function gql(query, variables = {}) {
      const res = await fetch("/graphql/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query, variables }),
      });
      const json = await res.json();
      if (json.errors) throw new Error(json.errors.map(e => e.message).join("; "));
      return json.data;
    }

    (async () => {
      const { pipelines } = await gql(`
        query($slug: String!) {
          pipelines(workspaceSlug: $slug, page: 1, perPage: 50) {
            items { id code name description schedule }
          }
        }
      `, { slug: workspaceSlug });

      const list = document.getElementById("list");
      list.innerHTML = "";
      for (const p of pipelines.items) {
        const li = document.createElement("li");
        li.innerHTML = `<strong>${p.name}</strong> <code>${p.code}</code><br><small>${p.description ?? ""}</small>`;
        list.appendChild(li);
      }
    })();
  </script>
</body>
</html>
```

### PIPELINES_READ + PIPELINES_RUN — Pick a pipeline and run it

Loads the list of pipelines on page open, lets you pick one from a dropdown, and runs it with a JSON config. Polls the run status until it terminates. Requires both `PIPELINES_READ` (to list) and `PIPELINES_RUN` (to launch).

```html
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>Run a pipeline</title>
  <style>
    body { font-family: system-ui, sans-serif; max-width: 640px; margin: 2rem auto; padding: 0 1rem; }
    label { display: block; margin: 0.75rem 0 0.25rem; font-weight: 500; }
    select, textarea { width: 100%; padding: 0.4rem; box-sizing: border-box; font-family: inherit; }
    button { margin-top: 1rem; padding: 0.5rem 1rem; }
    button[disabled] { opacity: 0.5; cursor: not-allowed; }
    #status { margin-top: 1rem; font-weight: 600; }
  </style>
</head>
<body>
  <h1>Run a pipeline</h1>

  <label>Pipeline
    <select id="pipeline" disabled><option>Loading…</option></select>
  </label>
  <label>Config (JSON)
    <textarea id="cfg" rows="4">{}</textarea>
  </label>
  <button id="runBtn" disabled onclick="runIt()">Run</button>

  <p id="status"></p>

  <script>
    const { workspaceSlug } = window.OPENHEXA;

    async function gql(query, variables = {}) {
      const res = await fetch("/graphql/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query, variables }),
      });
      const json = await res.json();
      if (json.errors) throw new Error(json.errors.map(e => e.message).join("; "));
      return json.data;
    }

    // 1. Load the pipeline list and populate the dropdown.
    (async () => {
      const { pipelines } = await gql(`
        query($slug: String!) {
          pipelines(workspaceSlug: $slug, page: 1, perPage: 100) {
            items { id code name }
          }
        }
      `, { slug: workspaceSlug });

      const select = document.getElementById("pipeline");
      if (!pipelines.items.length) {
        select.innerHTML = '<option>(no pipelines in this workspace)</option>';
        return;
      }
      select.innerHTML = pipelines.items
        .map(p => `<option value="${p.id}">${p.name} (${p.code})</option>`)
        .join("");
      select.disabled = false;
      document.getElementById("runBtn").disabled = false;
    })();

    // 2. Run the selected pipeline and poll until it terminates.
    async function runIt() {
      const id = document.getElementById("pipeline").value;
      const config = JSON.parse(document.getElementById("cfg").value || "{}");
      const status = document.getElementById("status");

      const { runPipeline } = await gql(`
        mutation($input: RunPipelineInput!) {
          runPipeline(input: $input) {
            success errors run { id status }
          }
        }
      `, { input: { id, config } });

      if (!runPipeline.success) {
        status.textContent = "Error: " + runPipeline.errors.join(", ");
        return;
      }

      const runId = runPipeline.run.id;
      status.textContent = "Running…";

      while (true) {
        await new Promise(r => setTimeout(r, 2000));
        const { pipelineRun } = await gql(
          `query($id: UUID!) { pipelineRun(id: $id) { status } }`,
          { id: runId },
        );
        status.textContent = "Status: " + pipelineRun.status;
        if (["SUCCESS", "FAILED", "STOPPED"].includes(pipelineRun.status)) break;
      }
    }
  </script>
</body>
</html>
```

### USER_READ + FILES_READ — Pick a CSV from the workspace bucket and preview it

Lists CSV files in the workspace bucket on page load, lets you pick one from a dropdown, and renders the first 100 lines as a table. Requires both `USER_READ` (to list files via `workspace.bucket.objects`) and `FILES_READ` (to read content).

```html
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>Preview CSV</title>
  <style>
    body { font-family: system-ui, sans-serif; max-width: 800px; margin: 2rem auto; padding: 0 1rem; }
    label { display: block; margin: 0.75rem 0 0.25rem; font-weight: 500; }
    select { width: 100%; padding: 0.4rem; box-sizing: border-box; font-family: inherit; }
    button { margin-top: 0.75rem; padding: 0.5rem 1rem; }
    button[disabled] { opacity: 0.5; cursor: not-allowed; }
    table { border-collapse: collapse; margin-top: 1rem; width: 100%; }
    th, td { border: 1px solid #ddd; padding: 0.3rem 0.5rem; font-size: 0.9rem; }
    th { background: #f5f5f5; }
    #status { margin-top: 1rem; color: #b91c1c; }
  </style>
</head>
<body>
  <h1>Preview CSV</h1>

  <label>File
    <select id="file" disabled><option>Loading…</option></select>
  </label>
  <button id="loadBtn" disabled onclick="load()">Load</button>

  <p id="status"></p>
  <div id="table"></div>

  <script>
    const { workspaceSlug } = window.OPENHEXA;

    async function gql(query, variables = {}) {
      const res = await fetch("/graphql/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query, variables }),
      });
      const json = await res.json();
      if (json.errors) throw new Error(json.errors.map(e => e.message).join("; "));
      return json.data;
    }

    // 1. List CSV files in the bucket and populate the dropdown.
    (async () => {
      const { workspace } = await gql(`
        query($slug: String!) {
          workspace(slug: $slug) {
            bucket {
              objects(page: 1, perPage: 200, ignoreHiddenFiles: true) {
                items { key name path type }
              }
            }
          }
        }
      `, { slug: workspaceSlug });

      const csvFiles = workspace.bucket.objects.items
        .filter(o => o.type === "FILE" && o.name.toLowerCase().endsWith(".csv"));

      const select = document.getElementById("file");
      if (!csvFiles.length) {
        select.innerHTML = '<option>(no CSV files in this workspace)</option>';
        return;
      }
      select.innerHTML = csvFiles
        .map(f => `<option value="${f.key}">${f.key}</option>`)
        .join("");
      select.disabled = false;
      document.getElementById("loadBtn").disabled = false;
    })();

    // 2. Fetch and render the selected file as a table.
    async function load() {
      const path = document.getElementById("file").value;
      const status = document.getElementById("status");
      const out = document.getElementById("table");
      status.textContent = "";
      out.innerHTML = "";

      const { readFileContent } = await gql(`
        query($slug: String!, $path: String!) {
          readFileContent(workspaceSlug: $slug, filePath: $path, startLine: 1, endLine: 100) {
            success content
          }
        }
      `, { slug: workspaceSlug, path });

      if (!readFileContent.success || !readFileContent.content) {
        status.textContent = "Could not read this file (it may be empty or unreadable as text).";
        return;
      }

      const rows = readFileContent.content.trim().split("\n").map(l => l.split(","));
      const [header, ...body] = rows;
      out.innerHTML = [
        "<table><thead><tr>",
        header.map(h => `<th>${h}</th>`).join(""),
        "</tr></thead><tbody>",
        body.map(r => "<tr>" + r.map(c => `<td>${c}</td>`).join("") + "</tr>").join(""),
        "</tbody></table>",
      ].join("");
    }
  </script>
</body>
</html>
```

### FILES_WRITE — Upload a file to the workspace bucket

Pick a file, upload it via a presigned URL.

```html
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>Upload a file</title>
  <style>
    body { font-family: system-ui, sans-serif; max-width: 560px; margin: 2rem auto; padding: 0 1rem; }
    input { width: 100%; padding: 0.4rem; box-sizing: border-box; }
    button { margin-top: 0.5rem; padding: 0.5rem 1rem; }
    #status { margin-top: 1rem; font-weight: 600; }
  </style>
</head>
<body>
  <h1>Upload a file</h1>

  <label>Destination key (path in the bucket)
    <input id="key" value="uploads/example.bin">
  </label>
  <input type="file" id="file">
  <button onclick="upload()">Upload</button>

  <p id="status"></p>

  <script>
    const { workspaceSlug } = window.OPENHEXA;

    async function gql(query, variables = {}) {
      const res = await fetch("/graphql/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query, variables }),
      });
      const json = await res.json();
      if (json.errors) throw new Error(json.errors.map(e => e.message).join("; "));
      return json.data;
    }

    async function upload() {
      const status = document.getElementById("status");
      const blob = document.getElementById("file").files[0];
      const key = document.getElementById("key").value.trim();
      if (!blob) { status.textContent = "Pick a file first."; return; }

      const { prepareObjectUpload } = await gql(`
        mutation($input: PrepareObjectUploadInput!) {
          prepareObjectUpload(input: $input) { success uploadUrl headers }
        }
      `, { input: { workspaceSlug, objectKey: key, contentType: blob.type } });

      const res = await fetch(prepareObjectUpload.uploadUrl, {
        method: "PUT",
        headers: { ...prepareObjectUpload.headers, "Content-Type": blob.type },
        body: blob,
      });
      status.textContent = res.ok ? "Uploaded ✓" : `Failed: HTTP ${res.status}`;
    }
  </script>
</body>
</html>
```

### DATASETS_READ — List datasets

Lists datasets visible to the workspace and their latest version.

```html
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>Datasets</title>
  <style>
    body { font-family: system-ui, sans-serif; max-width: 720px; margin: 2rem auto; padding: 0 1rem; }
    li { margin-bottom: 0.75rem; }
    small { color: #666; }
  </style>
</head>
<body>
  <h1>Datasets</h1>
  <ul id="list"><li>Loading…</li></ul>

  <script>
    const { workspaceSlug } = window.OPENHEXA;

    async function gql(query, variables = {}) {
      const res = await fetch("/graphql/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query, variables }),
      });
      const json = await res.json();
      if (json.errors) throw new Error(json.errors.map(e => e.message).join("; "));
      return json.data;
    }

    (async () => {
      const { workspace } = await gql(`
        query($slug: String!) {
          workspace(slug: $slug) {
            datasets(page: 1, perPage: 50) {
              items {
                dataset {
                  id slug name description
                  latestVersion { name createdAt }
                }
              }
            }
          }
        }
      `, { slug: workspaceSlug });

      const list = document.getElementById("list");
      list.innerHTML = "";
      for (const item of workspace.datasets.items) {
        const d = item.dataset;
        const li = document.createElement("li");
        const v = d.latestVersion ? `${d.latestVersion.name} — ${new Date(d.latestVersion.createdAt).toLocaleDateString()}` : "no version yet";
        li.innerHTML = `<strong>${d.name}</strong><br><small>Latest: ${v}</small>`;
        list.appendChild(li);
      }
    })();
  </script>
</body>
</html>
```

### DATASETS_WRITE — Create a new dataset

Tiny form that creates a dataset and prints the new id/slug.

```html
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>Create a dataset</title>
  <style>
    body { font-family: system-ui, sans-serif; max-width: 560px; margin: 2rem auto; padding: 0 1rem; }
    label { display: block; margin: 0.5rem 0 0.25rem; }
    input, textarea { width: 100%; padding: 0.4rem; box-sizing: border-box; font-family: inherit; }
    button { margin-top: 1rem; padding: 0.5rem 1rem; }
    #out { margin-top: 1rem; }
  </style>
</head>
<body>
  <h1>Create a dataset</h1>

  <label>Name
    <input id="name" placeholder="Survey results">
  </label>
  <label>Description
    <textarea id="desc" rows="3"></textarea>
  </label>
  <button onclick="create()">Create</button>

  <p id="out"></p>

  <script>
    const { workspaceSlug } = window.OPENHEXA;

    async function gql(query, variables = {}) {
      const res = await fetch("/graphql/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query, variables }),
      });
      const json = await res.json();
      if (json.errors) throw new Error(json.errors.map(e => e.message).join("; "));
      return json.data;
    }

    async function create() {
      const out = document.getElementById("out");
      const name = document.getElementById("name").value.trim();
      const description = document.getElementById("desc").value.trim();
      if (!name) { out.textContent = "Name is required."; return; }

      const { createDataset } = await gql(`
        mutation($input: CreateDatasetInput!) {
          createDataset(input: $input) {
            success errors dataset { id slug name }
          }
        }
      `, { input: { workspaceSlug, name, description } });

      if (!createDataset.success) {
        out.textContent = "Error: " + (createDataset.errors || []).join(", ");
        return;
      }
      out.textContent = `Created: ${createDataset.dataset.name} (slug: ${createDataset.dataset.slug})`;
    }
  </script>
</body>
</html>
```