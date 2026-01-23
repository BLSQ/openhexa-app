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
