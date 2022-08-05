import { NextRequest } from "next/server";

export const config = {
  runtime: "experimental-edge",
};

/**
 * Proxy to the old frontend. See middleware.ts for more info.
 *
 * @param req
 */
export default async function proxy(req: NextRequest) {
  const url = new URL(req.url);
  const fallbackURL = `${process.env.FALLBACK_URL}${url.pathname}${url.search}`;

  const cookie = ["sessionid", "csrftoken"]
    .map((key) => {
      const value = req.cookies.get(key);
      if (value) {
        return `${key}=${value}`;
      }
      return null;
    })
    .filter((c) => c !== null)
    .join(";");

  const response = await fetch(fallbackURL, {
    headers: { cookie },
    credentials: "include",
  });

  return new Response(await response.text(), {
    status: response.status,
    headers: {
      "Content-Type": response.headers.get("Content-Type") || "text/html",
    },
  });
}
