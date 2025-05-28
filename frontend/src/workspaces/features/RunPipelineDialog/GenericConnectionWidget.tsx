import { Description, Field } from "@headlessui/react";
import { useTranslation } from "next-i18next";
import { DHIS2Widget, dhis2WidgetToQuery } from "./DHIS2Widget";
import { IASOWidget, iasoWidgetToQuery } from "./IASOWidget";
import {gql} from "@apollo/client";

type GenericConnectionWidgetProps = {
  parameter: any;
  widget: string;
  form: any;
  workspaceSlug: string;
  name: string;
};

const GenericConnectionWidget = ({
  parameter,
  widget,
  form,
  workspaceSlug,
  ...delegated
}: GenericConnectionWidgetProps) => {
  const { t } = useTranslation();
  if (parameter.widget in iasoWidgetToQuery) {
    return (
      <IASOWidget
        parameter={parameter}
        widget={widget}
        form={form}
        workspaceSlug={workspaceSlug}
        {...delegated}
      />
    );
  }
  else if (parameter.widget in dhis2WidgetToQuery) {
    return (
      <DHIS2Widget
        parameter={parameter}
        widget={widget}
        form={form}
        workspaceSlug={workspaceSlug}
        {...delegated}
      />
    );
  }
  return (
    <div className="w-full max-w-md px-4">
      <Field>
        <Description className="text-sm/6  text-red-400">
          {t("Widget {{widget}} was not found", { widget: widget })}
        </Description>
      </Field>
    </div>
  );
};

export default GenericConnectionWidget;
