import {
  Disclosure,
  DisclosureButton,
  DisclosurePanel,
} from "@headlessui/react";
import {
  ChevronDownIcon,
  ExclamationCircleIcon,
} from "@heroicons/react/24/outline";
import clsx from "clsx";
import Checkbox from "core/components/forms/Checkbox";
import Field from "core/components/forms/Field";
import { useTranslation } from "next-i18next";
import PipelineVersionPicker from "../PipelineVersionPicker";
import ParameterField from "./ParameterField";
import { RunPipelineDialog_PipelineFragment } from "./RunPipelineDialog.generated";
import { RunPipelineFormState } from "./useRunPipelineForm";

type RunPipelineFormFieldsProps = {
  pipeline: RunPipelineDialog_PipelineFragment;
  state: RunPipelineFormState;
  // Narrow containers (e.g. a side panel) cannot fit two parameter columns.
  singleColumn?: boolean;
};

const RunPipelineFormFields = ({
  pipeline,
  state,
  singleColumn = false,
}: RunPipelineFormFieldsProps) => {
  const { t } = useTranslation();
  const {
    form,
    activeVersion,
    setActiveVersion,
    parameterDisablers,
    parameterNameByCode,
  } = state;

  if (!activeVersion) {
    return null;
  }

  return (
    <>
      <div
        className={clsx(
          "grid gap-x-3 gap-y-4",
          !singleColumn &&
            activeVersion.parameters.length > 4 &&
            "grid-cols-2 gap-x-5",
        )}
      >
        {activeVersion.parameters.map((param, i) => {
          const disablingCodes = parameterDisablers.get(param.code);
          const isDisabled = !!disablingCodes;
          return (
            <Field
              required={
                (param.required || param.type === "bool") && !isDisabled
              }
              key={i}
              name={param.code}
              label={param.name}
              help={param.help}
              note={
                disablingCodes
                  ? t("Disabled by {{names}}", {
                      names: disablingCodes
                        .map((code) => parameterNameByCode[code] ?? code)
                        .join(", "),
                    })
                  : undefined
              }
              error={form.touched[param.code] && form.errors[param.code]}
            >
              <fieldset
                disabled={isDisabled}
                className={clsx(isDisabled && "opacity-50")}
              >
                <ParameterField
                  parameter={param}
                  value={
                    form.formData[param.code] ?? (param.multiple ? [] : "")
                  }
                  onChange={(value: any) => {
                    form.setFieldValue(param.code, value);
                  }}
                  form={form}
                  workspaceSlug={pipeline.workspace?.slug}
                  pipelineVersionId={activeVersion.id}
                />
              </fieldset>
            </Field>
          );
        })}
      </div>
      {form.submitError && (
        <div className="mt-4 flex items-center gap-2 rounded-md bg-red-50 px-3 py-2 text-sm text-red-700">
          <ExclamationCircleIcon className="h-4 w-4 shrink-0 text-red-500" />
          {form.submitError}
        </div>
      )}
      <Disclosure as="div" className={"mt-5"}>
        {({ open }) => (
          <>
            <DisclosureButton className="group flex w-full justify-between text-left">
              <div className="flex flex-col">
                <span
                  className={"font-bold text-sm group-data-hover:text-black/80"}
                >
                  {t("Advanced settings")}
                </span>
                {!open && (
                  <span className="text-gray-500 text-sm mt-1">
                    {t("Pipeline version, notifications and logs")}
                  </span>
                )}
              </div>
              <ChevronDownIcon
                className={`size-5 mt-1 ml-5 group-data-hover:text-black/80 ${
                  open ? "rotate-180" : ""
                }`}
              />
            </DisclosureButton>
            <DisclosurePanel>
              <Field
                name="version"
                label={t("Version")}
                required
                className="mb-3"
              >
                <PipelineVersionPicker
                  required
                  pipeline={pipeline}
                  value={activeVersion}
                  onChange={(value) => setActiveVersion(value)}
                />
              </Field>
              <Field
                name="notification"
                label={t("Notifications")}
                required
                className="mb-4"
              >
                <Checkbox
                  checked={form.formData.sendMailNotifications}
                  name="sendMailNotifications"
                  onChange={(event) =>
                    form.setFieldValue(
                      "sendMailNotifications",
                      event.target.checked,
                    )
                  }
                  label={t("Send notifications")}
                  help={t("Notifications will be sent for this run.")}
                />
              </Field>
              <Field name="logs" label={t("Logs")} required>
                <Checkbox
                  checked={form.formData.enableDebugLogs}
                  name="enableDebugLogs"
                  onChange={(event) =>
                    form.setFieldValue("enableDebugLogs", event.target.checked)
                  }
                  label={t("Show debug messages")}
                  help={t("Debug messages will be shown for this run.")}
                />
              </Field>
            </DisclosurePanel>
          </>
        )}
      </Disclosure>
    </>
  );
};

export default RunPipelineFormFields;
