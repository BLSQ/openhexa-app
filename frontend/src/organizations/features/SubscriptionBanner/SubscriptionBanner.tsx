import { gql } from "@apollo/client";
import {
  ArrowTopRightOnSquareIcon,
  EnvelopeIcon,
  ExclamationTriangleIcon,
  LockClosedIcon,
  XMarkIcon,
} from "@heroicons/react/24/outline";
import clsx from "clsx";
import { DateTime } from "luxon";
import { useTranslation } from "next-i18next";
import { CSSProperties } from "react";
import Link from "core/components/Link";
import { Classes as ButtonClasses } from "core/components/Button/Button";
import { usePublicEnv } from "core/helpers/runtimeConfig";
import useCookieState from "core/hooks/useCookieState";
import { SubscriptionBanner_OrganizationFragment } from "./SubscriptionBanner.generated";

type BannerState = "expiringSoon" | "gracePeriod" | "frozen";

type SubscriptionBannerOrganization =
  SubscriptionBanner_OrganizationFragment | null | undefined;

const BANNER_HEIGHT = "2.5rem";
const DISMISSED_COOKIE = "subscription-banner-dismissed";

/**
 * Only organization admins and owners see the banner: they are the ones who can renew the plan.
 */
export const getSubscriptionBannerState = (
  organization: SubscriptionBannerOrganization,
): BannerState | null => {
  const subscription = organization?.subscription;
  if (!subscription || !organization.permissions.manageMembers) return null;
  if (subscription.isExpired) {
    return subscription.isInGracePeriod ? "gracePeriod" : "frozen";
  }
  return subscription.isExpiringSoon ? "expiringSoon" : null;
};

/**
 * Banner state after the user's dismissal is applied. Only the "expiring soon" reminder can
 * be dismissed; expired states always show. The dismissal is stored per organization against
 * the subscription end date, so it no longer applies once the subscription changes.
 * It lives in a cookie so the server renders the layout without the banner gap.
 */
export const useSubscriptionBanner = (
  organization: SubscriptionBannerOrganization,
) => {
  const [dismissed, setDismissed] = useCookieState<Record<string, string>>({
    name: DISMISSED_COOKIE,
    defaultValue: {},
  });
  const state = getSubscriptionBannerState(organization);
  const endDate = organization?.subscription?.endDate;
  const isDismissed =
    state === "expiringSoon" &&
    !!organization &&
    dismissed[organization.id] === endDate;

  const dismiss = () => {
    if (!organization || !endDate) return;
    setDismissed({ ...dismissed, [organization.id]: endDate });
  };

  return { state: isDismissed ? null : state, dismiss };
};

/**
 * Sets the CSS variable that layouts use to push their fixed sidebar, header and
 * content below the banner.
 */
export const useSubscriptionBannerOffsetStyle = (
  organization: SubscriptionBannerOrganization,
) => {
  const { state } = useSubscriptionBanner(organization);
  return {
    "--subscription-banner-height": state ? BANNER_HEIGHT : "0px",
  } as CSSProperties;
};

type SubscriptionBannerProps = {
  organization: SubscriptionBannerOrganization;
};

const SubscriptionBanner = ({ organization }: SubscriptionBannerProps) => {
  const { t } = useTranslation();
  const { CONSOLE_URL, CONTACT_EMAIL } = usePublicEnv();

  const { state, dismiss } = useSubscriptionBanner(organization);
  if (!state || !organization?.subscription) return null;

  const endDate = DateTime.fromISO(
    organization.subscription.endDate,
  ).toLocaleString(DateTime.DATE_MED);

  const message = {
    expiringSoon: t(
      "Your subscription for {{organization}} expires on {{date}}. Renew or upgrade your plan to avoid any interruption.",
      { organization: organization.name, date: endDate },
    ),
    gracePeriod: t(
      "Your subscription for {{organization}} expired on {{date}}. Renew soon to avoid service interruption.",
      { organization: organization.name, date: endDate },
    ),
    frozen: t(
      "Your subscription for {{organization}} has expired. Limits are frozen until you renew.",
      { organization: organization.name },
    ),
  }[state];

  const Icon = state === "frozen" ? LockClosedIcon : ExclamationTriangleIcon;
  const buttonClassName = clsx(
    ButtonClasses.base,
    ButtonClasses.white,
    ButtonClasses.sm,
    "shrink-0 gap-1 rounded-sm",
  );

  return (
    <div
      role="alert"
      className={clsx(
        "fixed inset-x-0 top-0 z-20 flex h-(--subscription-banner-height) items-center justify-center gap-4 px-12 text-sm",
        state === "frozen"
          ? "border-b border-red-200 bg-red-50 text-red-800"
          : "border-b border-amber-200 bg-amber-50 text-amber-800",
      )}
    >
      <Icon className="h-5 w-5 shrink-0" />
      <span className="truncate font-medium">{message}</span>
      {CONSOLE_URL && (
        <Link
          href={CONSOLE_URL}
          target="_blank"
          noStyle
          className={buttonClassName}
        >
          {t("Upgrade plan")}
          <ArrowTopRightOnSquareIcon className="h-3.5 w-3.5" />
        </Link>
      )}
      {CONTACT_EMAIL && (
        <a href={`mailto:${CONTACT_EMAIL}`} className={buttonClassName}>
          <EnvelopeIcon className="h-3.5 w-3.5" />
          {t("Contact us")}
        </a>
      )}
      {state === "expiringSoon" && (
        <button
          type="button"
          onClick={dismiss}
          aria-label={t("Dismiss")}
          className="absolute right-3 rounded-sm p-1 hover:bg-amber-100"
        >
          <XMarkIcon className="h-4 w-4" />
        </button>
      )}
    </div>
  );
};

SubscriptionBanner.fragments = {
  organization: gql`
    fragment SubscriptionBanner_organization on Organization {
      id
      name
      permissions {
        manageMembers
      }
      subscription {
        endDate
        isExpired
        isInGracePeriod
        isExpiringSoon
      }
    }
  `,
};

export default SubscriptionBanner;
