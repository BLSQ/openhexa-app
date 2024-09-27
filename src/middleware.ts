import { pageView } from "core/helpers/analytics";
import { NextResponse } from "next/server";
import type { NextFetchEvent, NextRequest } from "next/server";

// This middleware will rewrite the request to the fallback server
export function middleware(request: NextRequest, event: NextFetchEvent) {
  if (
    [
      "/auth/logout",
      "/static/",
      "/admin/",
      "/analytics/track/",
      "/files/up",
      "/files/dl",
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
  /*
   * Match all request paths except for the ones starting with:
   * - api (API routes)
   * - _next/static (static files)
   * - _next/image (image optimization files)
   * - favicon.ico (favicon file)
   * - images (image files)
   */
  matcher: "/((?!api|_next/static|_next/image|images|favicon.ico).*)",
};
