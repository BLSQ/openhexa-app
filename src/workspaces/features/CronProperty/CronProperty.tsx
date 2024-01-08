import DataCard from "core/components/DataCard";
import { useDataCardProperty } from "core/components/DataCard/context";
import { PropertyDefinition } from "core/components/DataCard/types";
import Input from "core/components/forms/Input";
import { useTranslation } from "next-i18next";
import {
  getCronExpressionDescription,
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
    return (
      <DataCard.Property property={property}>
        <Input
          value={property.formValue ?? ""}
          onChange={(e) => property.setValue(e.target.value)}
          required={property.required}
          readOnly={property.readonly}
          placeholder={placeholder}
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
