import { useTranslation } from "next-i18next";
import { DateTime } from "luxon";
import { Organization_OrganizationFragment } from "organizations/graphql/queries.generated";
import ProgressBar from "core/components/ProgressBar";
import Link from "core/components/Link";
import { ArrowTopRightOnSquareIcon } from "@heroicons/react/24/outline";
import { usePublicEnv } from "core/helpers/runtimeConfig";

type OrganizationUsageLimitsProps = {
  organization: Organization_OrganizationFragment;
};

const OrganizationUsageLimits = ({
  organization,
}: OrganizationUsageLimitsProps) => {
  const { t } = useTranslation();
  const { CONSOLE_URL } = usePublicEnv();

  const { usage, subscription } = organization;
  const limits = subscription?.limits;

  const usageItems = [
    {
      label: t("Users"),
      current: usage.users,
      limit: limits?.users,
    },
    {
      label: t("Workspaces"),
      current: usage.workspaces,
      limit: limits?.workspaces,
    },
    {
      label: t("Pipeline Runs (this month)"),
      current: usage.pipelineRuns,
      limit: limits?.pipelineRuns,
    },
  ];

  const formatTokens = (tokens: number) => {
    if (tokens >= 1_000_000) {
      return `${(tokens / 1_000_000).toFixed(2)}M`;
    }
    if (tokens >= 1_000) {
      return `${(tokens / 1_000).toFixed(1)}K`;
    }
    return tokens.toString();
  };

  const formatCost = (cost: number) => {
    return new Intl.NumberFormat("en-US", {
      style: "currency",
      currency: "USD",
      minimumFractionDigits: 2,
      maximumFractionDigits: 4,
    }).format(cost);
  };

  return (
    <div className="mt-6 rounded-lg bg-white shadow">
      <div className="flex items-center justify-between border-b border-gray-200 px-6 py-4">
        <div>
          <h2 className="text-lg font-semibold text-gray-900">
            {t("Usage & Limits")}
          </h2>
          <p className="mt-1 text-sm text-gray-500">
            {t("Current resource usage for your organization")}
          </p>
        </div>
        {CONSOLE_URL && (
          <Link
            href={CONSOLE_URL}
            target="_blank"
            noStyle
            className="flex items-center gap-2 text-sm text-blue-600 hover:text-blue-800"
          >
            {t("Manage subscription")}
            <ArrowTopRightOnSquareIcon className="h-4 w-4" />
          </Link>
        )}
      </div>

      <div className="space-y-6 px-6 py-6">
        {usageItems.map((item) => (
          <div key={item.label}>
            <div className="mb-2 text-sm font-medium text-gray-700">
              {item.label}
            </div>
            {item.limit !== undefined ? (
              <ProgressBar value={item.current} max={item.limit} />
            ) : (
              <p className="text-lg font-semibold text-gray-900">
                {item.current}
              </p>
            )}
          </div>
        ))}

        {organization.assistantEnabled && (
          <div className="border-t border-gray-200 pt-4">
            <div className="mb-2 text-sm font-medium text-gray-700">
              {t("AI Assistant (this month)")}
            </div>
            <dl className="grid grid-cols-3 gap-4 text-sm">
              <div>
                <dt className="text-gray-500">{t("Input tokens")}</dt>
                <dd className="font-medium text-gray-900">
                  {formatTokens(usage.assistantUsage.inputTokens)}
                </dd>
              </div>
              <div>
                <dt className="text-gray-500">{t("Output tokens")}</dt>
                <dd className="font-medium text-gray-900">
                  {formatTokens(usage.assistantUsage.outputTokens)}
                </dd>
              </div>
              <div>
                <dt className="text-gray-500">{t("Estimated cost")}</dt>
                <dd className="font-medium text-gray-900">
                  {formatCost(usage.assistantUsage.cost)}
                </dd>
              </div>
            </dl>
          </div>
        )}

        {subscription && (
          <div className="border-t border-gray-200 pt-4">
            <dl className="grid grid-cols-2 gap-4 text-sm">
              <div>
                <dt className="text-gray-500">{t("Plan")}</dt>
                <dd className="font-medium capitalize text-gray-900">
                  {subscription.planCode.replace(/_/g, " ")}
                </dd>
              </div>
              <div>
                <dt className="text-gray-500">{t("Valid until")}</dt>
                <dd className="font-medium text-gray-900">
                  {DateTime.fromISO(subscription.endDate).toLocaleString(
                    DateTime.DATE_MED,
                  )}
                </dd>
              </div>
            </dl>
          </div>
        )}
      </div>
    </div>
  );
};

export default OrganizationUsageLimits;
