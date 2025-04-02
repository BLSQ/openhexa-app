import Select from "core/components/forms/Select";
import { PipelineNotificationLevel } from "graphql/types";
import { i18n } from "next-i18next";

export const formatNotificationLevel = (level: PipelineNotificationLevel) => {
  switch (level) {
    case PipelineNotificationLevel.All:
      return i18n!.t("All");
    case PipelineNotificationLevel.Error:
      return i18n!.t("Error");
  }
};

export const NotificationLevelSelect = ({
  value,
  onChange,
}: {
  value?: PipelineNotificationLevel | null | undefined;
  onChange: (notificationLevel: PipelineNotificationLevel) => void;
}) => {
  return (
    <Select
      value={value || null}
      displayValue={(value) => formatNotificationLevel(value)}
      placeholder={i18n!.t("Select notification level")}
      onChange={onChange}
      required
      getOptionLabel={(option) => formatNotificationLevel(option)}
      options={[PipelineNotificationLevel.All, PipelineNotificationLevel.Error]}
    />
  );
};
