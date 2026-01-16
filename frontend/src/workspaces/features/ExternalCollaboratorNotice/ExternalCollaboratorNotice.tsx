import { useTranslation } from "next-i18next";
import {
  ArrowTopRightOnSquareIcon,
  SparklesIcon,
} from "@heroicons/react/24/outline";
import Link from "core/components/Link";
import { useOrganizationsQuery } from "organizations/graphql/queries.generated";

type ExternalCollaboratorNoticeProps = {
  compact?: boolean;
};

const ExternalCollaboratorNotice = ({
  compact = false,
}: ExternalCollaboratorNoticeProps) => {
  const { t } = useTranslation();
  const consoleUrl = process.env.NEXT_PUBLIC_CONSOLE_URL;

  const { data, loading } = useOrganizationsQuery();

  if (
    loading ||
    !data ||
    data.organizations.length > 0 ||
    !consoleUrl ||
    compact
  ) {
    return null;
  }

  return (
    <div className="mx-2 my-4 rounded-lg bg-linear-to-r from-indigo-500 to-purple-500 p-4 text-white">
      <div className="flex items-start gap-3">
        <SparklesIcon className="mt-0.5 h-5 w-5 shrink-0" />
        <div className="space-y-2">
          <p className="text-sm font-medium">
            {t("Create your own organization")}
          </p>
          <p className="text-xs text-indigo-100">
            {t(
              "Get full control over workspaces, pipelines, and team management.",
            )}
          </p>
          <Link
            href={consoleUrl}
            target="_blank"
            noStyle
            className="inline-flex items-center gap-1.5 text-xs font-medium text-white underline hover:text-indigo-100"
          >
            {t("Get started")}
            <ArrowTopRightOnSquareIcon className="h-3 w-3" />
          </Link>
        </div>
      </div>
    </div>
  );
};

export default ExternalCollaboratorNotice;
