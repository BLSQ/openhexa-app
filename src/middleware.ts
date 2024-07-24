import { pageView } from "core/helpers/analytics";
import { NextResponse } from "next/server";
import type { NextFetchEvent, NextRequest } from "next/server";

// This middleware will rewrite the request to the fallback server
export function middleware(request: NextRequest, event: NextFetchEvent) {
  if (
    [
      "/graphql",
      "/auth/logout",
      "/static/",
      "/admin/",
      "/analytics/track",
    ].some((path) => request.nextUrl.pathname.startsWith(path))
  ) {
    return NextResponse.rewrite(
      new URL(
        request.nextUrl.pathname + request.nextUrl.search,
        process.env.OPENHEXA_BACKEND_URL,
      ),
    );
  }

  event.waitUntil(pageView(request));
  return NextResponse.next();
}

export const config = {
  matcher: [
    /*
     * Match all request paths except for the ones starting with:
     * - api (API routes)
     * - _next/static (static files)
     * - _next/image (image optimization files)
     * - favicon.ico (favicon file)
     * - images (image files)
     */
    {
      source: "/((?!api|_next/static|_next/image|images|favicon.ico).*)",
      missing: [
        { type: "header", key: "next-router-prefetch" },
        { type: "header", key: "purpose", value: "prefetch" },
      ],
    },

    {
      source: "/((?!api|_next/static|_next/image|images|favicon.ico).*)",
      has: [
        { type: "header", key: "next-router-prefetch" },
        { type: "header", key: "purpose", value: "prefetch" },
      ],
    },

    {
      source: "/((?!api|_next/static|_next/image|images|favicon.ico).*)",
      has: [{ type: "header", key: "x-present" }],
      missing: [{ type: "header", key: "x-missing", value: "prefetch" }],
    },
  ],
};
