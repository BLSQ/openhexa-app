import Clipboard from "core/components/Clipboard";
import { useTranslation } from "next-i18next";
import { SavedQueryParameter } from "./savedQueryParameters";

type Props = {
  workspaceSlug: string;
  slug: string;
  parameters: SavedQueryParameter[];
};

const sampleValue = (parameter: SavedQueryParameter): string => {
  switch (parameter.type) {
    case "integer":
      return String(parameter.min ?? 10);
    case "number":
      return String(parameter.min ?? 1.5);
    case "boolean":
      return "true";
    case "date":
      return '"2024-01-01"';
    default:
      return parameter.choices?.length
        ? JSON.stringify(parameter.choices[0])
        : '"example"';
  }
};

// Read-only panel shown for public queries: the stable slug plus a ready-to-copy
// example of the anonymous GraphQL call a web app would make.
const SavedQueryPublicShare = ({ workspaceSlug, slug, parameters }: Props) => {
  const { t } = useTranslation();

  const parameterLines = parameters
    .map((parameter) => `      ${parameter.name}: ${sampleValue(parameter)}`)
    .join("\n");

  const example = [
    "mutation {",
    "  executePublicSavedQuery(input: {",
    `    workspaceSlug: ${JSON.stringify(workspaceSlug)}`,
    `    slug: ${JSON.stringify(slug)}`,
    ...(parameters.length
      ? ["    parameters: {", parameterLines, "    }"]
      : []),
    "  }) {",
    "    success",
    "    columns",
    "    rows",
    "    errors",
    "  }",
    "}",
  ].join("\n");

  return (
    <div className="space-y-2 rounded-md border border-green-200 bg-green-50 p-3">
      <div className="flex items-center justify-between gap-2">
        <span className="text-sm font-medium text-green-900">
          {t("This query is public")}
        </span>
        <code className="rounded-sm bg-white px-2 py-0.5 font-mono text-xs text-gray-700">
          {slug}
        </code>
      </div>
      <p className="text-xs text-green-800">
        {t(
          "Anyone can run it anonymously by POSTing this GraphQL mutation to /graphql/:",
        )}
      </p>
      <div className="flex items-start justify-between gap-2 rounded-md bg-white p-2">
        <pre className="overflow-x-auto text-xs text-gray-700">{example}</pre>
        <Clipboard value={example} />
      </div>
    </div>
  );
};

export default SavedQueryPublicShare;
