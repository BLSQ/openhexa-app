import DataCard from "core/components/DataCard";
import { useDataCardProperty } from "core/components/DataCard/context";
import { PropertyDefinition } from "core/components/DataCard/types";
import Input from "core/components/forms/Input";
import { useTranslation } from "react-i18next";
import {
  getCronExpressionDescription,
  validateCronExpression,
} from "workspaces/helpers/pipelines";

type CronPropertyProps = PropertyDefinition & { className?: string };

const CronProperty = (props: CronPropertyProps) => {
  const { className, ...delegated } = props;
  const { t } = useTranslation();
  const validateCron = (value: string) => {
    if (!validateCronExpression(value)) {
      return t("Invalid cron expression");
    }
    return null;
  };

  const { property, section } = useDataCardProperty({
    ...delegated,
    validate: validateCron,
  });
  if (section.isEdited && !property.readonly) {
    return (
      <DataCard.Property property={property}>
        <Input
          value={property.formValue ?? ""}
          onChange={(e) => property.setValue(e.target.value)}
          required={property.required}
          readOnly={property.readonly}
        />
      </DataCard.Property>
    );
  } else {
    return (
      <DataCard.Property property={property}>
        <div className={className}>
          {property.displayValue
            ? getCronExpressionDescription(property.displayValue)
            : property.defaultValue}
        </div>
      </DataCard.Property>
    );
  }
};

export default CronProperty;
