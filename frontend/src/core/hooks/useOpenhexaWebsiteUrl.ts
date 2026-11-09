import { useEffect, useState } from "react";

export const OPENHEXA_WEBSITE_URL = "https://www.openhexa.com/";

export type UtmTags = {
  source: string;
  campaign: string;
  content: string;
};

// Mirrors the backend hexa.webapps.utils.powered_by_url, so Google Analytics on
// openhexa.com reads the same UTM parameters wherever OpenHEXA links to it.
// Built on the client because it needs the current host. Without tags, the
// plain website URL.
const useOpenhexaWebsiteUrl = (tags?: UtmTags) => {
  const [url, setUrl] = useState(OPENHEXA_WEBSITE_URL);
  const { source, campaign, content } = tags ?? {};

  useEffect(() => {
    if (!source || !campaign || !content) {
      setUrl(OPENHEXA_WEBSITE_URL);
      return;
    }
    const params = new URLSearchParams({
      utm_source: source,
      utm_medium: "referral",
      utm_campaign: campaign,
      utm_content: content,
      utm_term: window.location.host,
    });
    setUrl(`${OPENHEXA_WEBSITE_URL}?${params.toString()}`);
  }, [source, campaign, content]);

  return url;
};

export default useOpenhexaWebsiteUrl;
