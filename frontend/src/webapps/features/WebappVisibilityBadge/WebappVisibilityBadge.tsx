import { BadgeProps } from "core/components/Badge";
import SharingBadge from "core/features/Sharing/SharingBadge";
import { SHARING_STYLES } from "core/features/Sharing/sharingStyles";
import { useTranslation } from "next-i18next";

type WebappVisibilityBadgeProps = {
  isPublic: boolean;
  size?: BadgeProps["size"];
  className?: string;
};

const WebappVisibilityBadge = ({
  isPublic,
  ...props
}: WebappVisibilityBadgeProps) => {
  const { t } = useTranslation();
  const option = isPublic
    ? { ...SHARING_STYLES.public, label: t("Public") }
    : { ...SHARING_STYLES.private, label: t("Private") };
  return <SharingBadge option={option} {...props} />;
};

export default WebappVisibilityBadge;
