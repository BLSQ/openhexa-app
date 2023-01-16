import express from "express";
import next from "next";
import proxy from "express-http-proxy";
const port = process.env.PORT ?? 3000;
const dev = process.env.NODE_ENV !== "production";
const fallback_url = process.env.FALLBACK_URL ?? "localhost:8000";

const app = next({ dev });
const handle = app.getRequestHandler();

app.prepare().then(async () => {
  const server = express();

  server.use(
    "/",
    proxy(fallback_url, {
      filter: function (req) {
        const isNext =
          req.path.startsWith("/login") ||
          req.path.startsWith("/user/account") ||
          req.path.startsWith("/two_factor") ||
          req.path.startsWith("/collections") ||
          req.path.startsWith("/visualizations") ||
          req.path.startsWith("/") ||
          req.path.startsWith("/notebooks") ||
          req.path.startsWith("/pipelines") ||
          req.path.startsWith("/workspaces") ||
          req.path.startsWith("/user/account") ||
          req.path.startsWith("/catalog/search") ||
          req.path.startsWith("/airflow") ||
          req.path.startsWith("/images") ||
          req.path.startsWith("/_next") ||
          req.path === "/" ||
          req.path.startsWith("/ready");

        const isLegacy = req.path.search(
          /^\/visualizations\/[0-9a-fA-F]{8}\b-[0-9a-fA-F]{4}\b-[0-9a-fA-F]{4}\b-[0-9a-fA-F]{4}\b-[0-9a-fA-F]{12}\b\/image/
        );
        return !isNext || !isLegacy;
      },
    })
  );

  server.all("*", (req, res) => handle(req, res));

  server.listen(port, () => {
    console.log(`> Ready on http://localhost:${port}`);
  });
});
