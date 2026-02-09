import { useTranslation } from "next-i18next";
import { DateTime } from "luxon";
import { Organization_OrganizationFragment } from "organizations/graphql/queries.generated";
import ProgressBar from "core/components/ProgressBar";
import Link from "core/components/Link";
import {
  ArrowTopRightOnSquareIcon,
  ExclamationTriangleIcon,
  LockClosedIcon,
} from "@heroicons/react/24/outline";
import { usePublicEnv } from "core/helpers/runtimeConfig";
import clsx from "clsx";

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

  const isExpiredPastGracePeriod =
    subscription?.isExpired && !subscription?.isInGracePeriod;

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
        {subscription?.isInGracePeriod && (
          <div className="flex items-center gap-2 rounded-md bg-amber-50 px-3 py-2 text-sm text-amber-800">
            <ExclamationTriangleIcon className="h-5 w-5 flex-shrink-0" />
            <span>
              {t(
                "Your subscription has expired. Please renew soon to avoid service interruption.",
              )}
            </span>
          </div>
        )}
        {isExpiredPastGracePeriod && (
          <div className="flex items-center gap-2 rounded-md bg-red-50 px-3 py-2 text-sm text-red-800">
            <LockClosedIcon className="h-5 w-5 flex-shrink-0" />
            <span>
              {t(
                "Your subscription has expired. Limits are frozen until you renew.",
              )}
            </span>
          </div>
        )}

        {usageItems.map((item) => (
          <div key={item.label}>
            <div className="mb-2 flex items-center gap-2 text-sm font-medium text-gray-700">
              {item.label}
              {isExpiredPastGracePeriod && item.limit !== undefined && (
                <LockClosedIcon className="h-4 w-4 text-gray-400" />
              )}
            </div>
            {item.limit !== undefined ? (
              <ProgressBar
                value={item.current}
                max={item.limit}
                disabled={isExpiredPastGracePeriod}
              />
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
                <dt className="text-gray-500">
                  {subscription.isExpired ? t("Expired on") : t("Valid until")}
                </dt>
                <dd
                  className={clsx(
                    "font-medium",
                    isExpiredPastGracePeriod
                      ? "text-red-800"
                      : subscription.isInGracePeriod
                        ? "text-amber-800"
                        : "text-gray-900",
                  )}
                >
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
