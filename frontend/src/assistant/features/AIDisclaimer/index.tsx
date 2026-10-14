import Link from "core/components/Link";
import { Trans } from "next-i18next";

export const AI_DOCS_URL = "https://docs.openhexa.com/ai/";

const AIDisclaimer = () => (
  <p className="mt-2 text-center text-xs text-gray-400">
    <Trans>
      AI can make mistakes. Always verify important information.{" "}
      <Link
        href={AI_DOCS_URL}
        target="_blank"
        customStyle="underline underline-offset-2 hover:text-gray-600"
      >
        Learn how AI is used in OpenHEXA
      </Link>
    </Trans>
  </p>
);

export default AIDisclaimer;
