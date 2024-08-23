import { NextRequest } from "next/server";

interface TrackEventProperties {
  [key: string]: any;
}

export async function trackEvent(
  event: string,
  properties: TrackEventProperties,
): Promise<void> {
  if (typeof window === "undefined") {
    // We do not support tracking events on the server
    return;
  }
  try {
    const res = await fetch("/analytics/track/", {
      method: "POST",
      priority: "low",
      headers: {
        "Content-Type": "application/json",
      },
      credentials: "include",
      body: JSON.stringify({ event, properties }),
    });

    if (!res.ok) {
      throw new Error(`Failed to track event: ${res.statusText}`);
    }
  } catch (error) {
    console.error("Error tracking event:", error);
  }
}

export async function pageView(request: NextRequest) {
  // This is to be called on the server side only.
  if (typeof window !== "undefined") {
    return;
  }
  try {
    const headers = request.headers;
    headers.set("content-type", "application/json");
    const res = await fetch(
      `${process.env.OPENHEXA_BACKEND_URL ?? ""}/analytics/track/`,
      {
        method: "POST",
        headers,
        body: JSON.stringify({
          event: "pageview",
          properties: {
            pathname: request.nextUrl.pathname,
            searchParams: request.nextUrl.searchParams.toString(),
          },
        }),
      },
    );

    if (!res.ok) {
      throw new Error(`Failed to track event: ${res.statusText}`);
    }
  } catch (error) {
    console.error("Error tracking event:", error);
  }
}
