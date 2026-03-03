import express from "express";
import next from "next";
import proxy from "express-http-proxy";
const port = process.env.PORT ?? 3000;
const dev = process.env.NODE_ENV !== "production";
const api_url = process.env.OPENHEXA_BACKEND_URL ?? "localhost:8000";
const api_base_path = process.env.NEXT_PUBLIC_API_BASE_PATH ?? "";
const max_request_body_size = process.env.MAX_REQUEST_BODY_SIZE;

const app = next({ dev });
const handle = app.getRequestHandler();

const API_PATHS = [
  "/graphql/",
  "/auth/logout",
  "/static/",
  "/admin/",
  "/analytics/track/",
  "/files/up",
  "/files/dl",
  "/superset",
];

app.prepare().then(async () => {
  const server = express();

  // Redirect /dashboards/[externalId] to /superset/dashboards/external/[externalId]
  // This is a temporary redirect until we have completely migrated from the older dashboard embedding solution
  server.get("/dashboards/:externalId", (req, res) => {
    res.redirect(301, `/superset/dashboard/external/${req.params.externalId}`);
  });

  server.use(
    "/",
    proxy(api_url, {
      // Decides whether to proxy a request to the backend.
      // When an API base path prefix is configured (e.g. /api),
      // we strip it before sending it.
      filter: function (req) {
        const hasPrefix =
          api_base_path && req.path.startsWith(api_base_path + "/");
        const realPath = hasPrefix
          ? req.path.replace(api_base_path, "") || "/"
          : req.path;

        return API_PATHS.some((path) => realPath.startsWith(path));
      },
      // Decides what path to send to the backend.
      // when a prefix is configured, we again strip it before sending it.
      proxyReqPathResolver: function (req) {
        // Use req.originalUrl (not req.path) to preserve query strings.
        if (api_base_path && req.path.startsWith(api_base_path + "/")) {
          return req.originalUrl.replace(api_base_path, "") || "/";
        }

        return req.originalUrl;
      },
      limit: max_request_body_size,
    }),
  );

  server.all(/(.*)/, (req, res) => handle(req, res));

  server.listen(port, () => {
    console.log(`> Ready on http://localhost:${port}`);
  });
});
