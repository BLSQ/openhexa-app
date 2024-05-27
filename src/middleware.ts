import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

// This middleware will rewrite the request to the fallback server
export function middleware(request: NextRequest) {
  const srcUrl = new URL(request.url);
  return NextResponse.rewrite(
    new URL(srcUrl.pathname + srcUrl.search, process.env.OPENHEXA_BACKEND_URL),
  );
}

export const config = {
  matcher: [
    "/graphql/:path*" /* GraphQL */,
    "/admin/:path*" /* Django Admin */,
    "/static/:path*" /* Static files of Django */,
    "/auth/logout",
  ],
};
