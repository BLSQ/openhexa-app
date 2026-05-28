import DataCard from "core/components/DataCard";
import { useDataCardProperty } from "core/components/DataCard/context";
import { PropertyDefinition } from "core/components/DataCard/types";
import Input from "core/components/forms/Input";
import { Trans, useTranslation } from "next-i18next";
import Link from "core/components/Link";
import { ExclamationCircleIcon } from "@heroicons/react/24/outline";
import {
  getCronExpressionDescription,
  getCronExpressionNextRun,
  validateCronExpression,
} from "workspaces/helpers/pipelines";

type CronPropertyProps = PropertyDefinition & {
  className?: string;
  placeholder?: string;
};

const CronProperty = (props: CronPropertyProps) => {
  const { className, placeholder, ...delegated } = props;
  const { t } = useTranslation();
  const validateCron = (value: string) => {
    if (value && !validateCronExpression(value)) {
      return t("Invalid cron expression");
    }
    return null;
  };

  const { property, section } = useDataCardProperty({
    ...delegated,
    validate: validateCron,
  });

  if (section.isEdited && !property.readonly) {
    const description = getCronExpressionDescription(property.formValue);
    const nextRun = getCronExpressionNextRun(property.formValue);
    return (
      <DataCard.Property property={property}>
        <div className="flex items-center gap-2">
          <Input
            value={property.formValue ?? ""}
            onChange={(e) => property.setValue(e.target.value)}
            required={property.required}
            readOnly={property.readonly}
            placeholder={placeholder}
            className="shrink-0 w-72"
            fullWidth={false}
          />
          <span className="grow-0 text-gray-500 italic">
            {description ? `${description} (UTC)` : t("Invalid")}
          </span>
        </div>
        {nextRun && (
          <div
            className="text-xs text-gray-500 mt-1"
            suppressHydrationWarning={true}
          >
            {t("Next run: {{date}} ({{timeZone}})", {
              date: nextRun.formatted,
              timeZone: nextRun.timeZone,
            })}
          </div>
        )}
        <Trans>
          <div className="text-xs text-gray-500 mt-1">
            Use{" "}
            <Link
              href={
                "https://crontab.guru/#" +
                (property.formValue?.replaceAll(" ", "_") ?? "")
              }
              target="_blank"
            >
              crontab.guru
            </Link>{" "}
            to help you create a cron expression.
          </div>
        </Trans>
        <div className="flex items-start gap-1 text-xs text-gray-600 mt-1">
          <ExclamationCircleIcon className="w-4 h-4 flex-shrink-0 mt-0.5" />
          <span>
            {t(
              "If there is already a running or scheduled pipeline run, the execution will be skipped.",
            )}
          </span>
        </div>
      </DataCard.Property>
    );
  } else {
    const description = property.displayValue
      ? getCronExpressionDescription(property.displayValue)
      : null;
    const nextRun = property.displayValue
      ? getCronExpressionNextRun(property.displayValue)
      : null;
    return (
      <DataCard.Property property={property}>
        <div className={className}>
          {property.displayValue
            ? description && `${description} (UTC)`
            : property.defaultValue}
        </div>
        {nextRun && (
          <div
            className="text-xs text-gray-500 mt-1"
            suppressHydrationWarning={true}
          >
            {t("Next run: {{date}} ({{timeZone}})", {
              date: nextRun.formatted,
              timeZone: nextRun.timeZone,
            })}
          </div>
        )}
      </DataCard.Property>
    );
  }
};

export default CronProperty;
