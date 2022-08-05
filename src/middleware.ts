import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

/**
 * This middleware forwards all routes to a proxy API route, unless they have
 * been explicitly handled in this middleware.
 *
 * This is useful for now as most of the OpenHexa UX has not been implemented
 * yet in this NextJS app. This allows us to start moving / creating parts
 * of the OpenHexa UX in here, with a fallback mechanism to the previous
 * frontend.
 *
 * @param request
 */
export async function middleware(request: NextRequest) {
  if (
    request.nextUrl.pathname.startsWith("/collections") ||
    request.nextUrl.pathname.startsWith("/images") ||
    request.nextUrl.pathname.startsWith("/_next")
  ) {
    return NextResponse.next();
  }

  return NextResponse.rewrite(new URL("/api/proxy", request.url));
}

// See "Matching Paths" below to learn more
export const config = {
  matcher: "/:path*",
};
