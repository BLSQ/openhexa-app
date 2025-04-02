import express from "express";
import next from "next";
import proxy from "express-http-proxy";
const port = process.env.PORT ?? 3000;
const dev = process.env.NODE_ENV !== "production";
const api_url = process.env.OPENHEXA_BACKEND_URL ?? "localhost:8000";
const max_request_body_size = process.env.MAX_REQUEST_BODY_SIZE;

const app = next({ dev });
const handle = app.getRequestHandler();

app.prepare().then(async () => {
  const server = express();

  server.use(
    "/",
    proxy(api_url, {
      filter: function (req) {
        const needsProxy = [
          "/graphql/",
          "/auth/logout",
          "/static/",
          "/admin/",
          "/analytics/track/",
          "/files/up",
          "/files/dl",
          "/superset",
        ].some((path) => req.path.startsWith(path));
        return needsProxy;
      },
      limit: max_request_body_size,
    }),
  );

  server.all("*", (req, res) => handle(req, res));

  server.listen(port, () => {
    console.log(`> Ready on http://localhost:${port}`);
  });
});
