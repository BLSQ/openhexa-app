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

  const response = await fetch(fallbackURL, {
    credentials: "include",
    headers: req.headers,
  });

  return new Response(response.body, {
    status: response.status,
    headers: response.headers,
  });
}
