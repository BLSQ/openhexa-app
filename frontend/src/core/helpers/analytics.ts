import { getPublicEnv } from "./runtimeConfig";

interface TrackEventProperties {
  [key: string]: any;
}

async function sendEvent(
  event: string,
  properties: TrackEventProperties,
): Promise<void> {
  const { DISABLE_ANALYTICS, OPENHEXA_BACKEND_URL } = getPublicEnv();
  if (DISABLE_ANALYTICS === "true") {
    return;
  }
  const res = await fetch(`${OPENHEXA_BACKEND_URL}/analytics/track/`, {
    method: "POST",
    priority: "low",
    credentials: "include",
    body: JSON.stringify({ event, properties }),
  });

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
