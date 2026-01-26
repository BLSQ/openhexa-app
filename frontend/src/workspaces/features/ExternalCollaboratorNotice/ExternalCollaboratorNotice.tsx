import { useTranslation } from "next-i18next";
import {
  ArrowTopRightOnSquareIcon,
  SparklesIcon,
} from "@heroicons/react/24/outline";
import Link from "core/components/Link";
import { usePublicEnv } from "core/helpers/runtimeConfig";
import { useOrganizationsQuery } from "organizations/graphql/queries.generated";

type ExternalCollaboratorNoticeProps = {
  compact?: boolean;
};

const ExternalCollaboratorNotice = ({
  compact = false,
}: ExternalCollaboratorNoticeProps) => {
  const { t } = useTranslation();
  const { CONSOLE_URL } = usePublicEnv();

  const { data, loading } = useOrganizationsQuery({
    variables: { directMembershipOnly: true },
  });

  if (loading || !data || data.organizations.length > 0 || !CONSOLE_URL) {
    return null;
  }

  if (compact) {
    return (
      <Link
        href={CONSOLE_URL}
        target="_blank"
        noStyle
        className="group relative mx-auto mb-4 flex h-10 w-10 items-center justify-center overflow-hidden rounded-lg bg-linear-to-r from-indigo-500 to-purple-500"
        title={t("Create your own organization")}
      >
        <SparklesIcon className="h-5 w-5 text-white" />
        <div className="absolute inset-0 -translate-x-full animate-[shimmer_2s_infinite] bg-linear-to-r from-transparent via-white/20 to-transparent" />
      </Link>
    );
  }

  return (
    <Link
      href={CONSOLE_URL}
      target="_blank"
      noStyle
      className="group relative mx-2 my-4 block overflow-hidden rounded-lg bg-linear-to-r from-indigo-500 to-purple-500 p-4 text-white transition-shadow hover:shadow-lg"
    >
      <div className="absolute inset-0 -translate-x-full animate-[shimmer_2s_infinite] bg-linear-to-r from-transparent via-white/20 to-transparent" />
      <div className="relative flex items-start gap-3">
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
          <span className="inline-flex items-center gap-1.5 text-xs font-medium text-white underline group-hover:text-indigo-100">
            {t("Get started")}
            <ArrowTopRightOnSquareIcon className="h-3 w-3" />
          </span>
        </div>
      </div>
    </Link>
  );
};

export default ExternalCollaboratorNotice;
