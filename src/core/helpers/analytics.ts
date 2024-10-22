import { NextRequest } from "next/server";
import getConfig from "next/config";

const { publicRuntimeConfig } = getConfig();

interface TrackEventProperties {
  [key: string]: any;
}

async function sendEvent(
  event: string,
  properties: TrackEventProperties,
  headers?: Headers,
): Promise<void> {
  if (publicRuntimeConfig.DISABLE_ANALYTICS) {
    return;
  }
  const res = await fetch(
    `${publicRuntimeConfig.OPENHEXA_BACKEND_URL ?? ""}/analytics/track/`,
    {
      method: "POST",
      priority: "low",
      headers: headers,
      credentials: "include",
      body: JSON.stringify({ event, properties }),
    },
  );

  if (!res.ok) {
    throw new Error(`Failed to send event: ${res.statusText}`);
  }
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
    await sendEvent(event, properties);
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

    await sendEvent(
      "pageview",
      {
        pathname: request.nextUrl.pathname,
        searchParams: request.nextUrl.searchParams.toString(),
      },
      headers,
    );
  } catch (error) {
    console.error("Error tracking event:", error);
  }
}
