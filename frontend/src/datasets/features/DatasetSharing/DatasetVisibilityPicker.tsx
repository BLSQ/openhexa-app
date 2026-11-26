import {
  Listbox,
  ListboxButton,
  ListboxOption,
  ListboxOptions,
} from "@headlessui/react";
import { CheckIcon, ChevronDownIcon } from "@heroicons/react/24/outline";
import clsx from "clsx";
import Callout from "core/components/Callout";
import Clipboard from "core/components/Clipboard";
import ConfirmSharingDialog from "core/features/Sharing/ConfirmSharingDialog";
import useDatasetShareDialog from "datasets/features/DatasetSharing/useDatasetShareDialog";
import { DatasetVisibility } from "graphql/types";
import { useTranslation } from "next-i18next";
import { useState } from "react";
import { DatasetShareButton_DatasetFragment } from "./DatasetShareButton.generated";

type DatasetVisibilityPickerProps = {
  dataset: DatasetShareButton_DatasetFragment;
  disabled?: boolean;
};

// Visibility summary of the Access management tab, whose title doubles as the
// control. Switching between private and organization applies straight away,
// as it is easily undone; going public or leaving public asks for
// confirmation, with its warning and public slug.
const DatasetVisibilityPicker = ({
  dataset,
  disabled = false,
}: DatasetVisibilityPickerProps) => {
  const { t } = useTranslation();
  const { onSave, warning, children, isSaveDisabled, ...picker } =
    useDatasetShareDialog(dataset);
  const { visibility } = dataset;
  const [pending, setPending] = useState<DatasetVisibility | null>(null);
  const [saving, setSaving] = useState(false);

  const save = async (next: DatasetVisibility) => {
    setSaving(true);
    try {
      await onSave(next);
      setPending(null);
    } catch {
      // Reported by onSave.
    } finally {
      setSaving(false);
    }
  };

  const select = (next: DatasetVisibility) => {
    if (next === visibility) {
      return;
    }
    if ([next, visibility].includes(DatasetVisibility.Public)) {
      setPending(next);
    } else {
      save(next);
    }
  };

  const current = picker.options.find((option) => option.value === visibility)!;
  const makingPublic = pending === DatasetVisibility.Public;
  const warningContent = pending && warning?.(pending, visibility);

  return (
    <div className="rounded-lg border border-gray-200 p-5">
      <div className="flex items-start gap-4">
        <span
          className={clsx(
            "flex h-10 w-10 shrink-0 items-center justify-center rounded-full",
            current.badgeClassName,
          )}
        >
          <current.Icon className={clsx("h-5 w-5", current.iconClassName)} />
        </span>
        <div className="min-w-0 flex-1">
          <Listbox
            value={visibility}
            onChange={select}
            disabled={disabled || saving}
          >
            <ListboxButton
              aria-label={t("Visibility")}
              className="-ml-2 inline-flex items-center gap-1.5 rounded-md px-2 py-0.5 font-semibold text-gray-900 hover:bg-gray-100 focus:outline-hidden focus:ring-2 focus:ring-blue-500 data-disabled:cursor-default data-disabled:hover:bg-transparent data-open:bg-gray-100"
            >
              {current.label}
              {!disabled && (
                <ChevronDownIcon className="h-4 w-4" aria-hidden="true" />
              )}
            </ListboxButton>
            <ListboxOptions
              anchor="bottom start"
              className="z-20 w-96 rounded-lg bg-white p-1.5 shadow-lg ring-1 ring-black/5 [--anchor-gap:4px] focus:outline-hidden"
            >
              {picker.options.map((option) => (
                <ListboxOption
                  key={option.value}
                  value={option.value}
                  disabled={picker.isOptionDisabled?.(option.value)}
                  className="group flex cursor-pointer gap-2.5 rounded-md p-2.5 data-disabled:cursor-not-allowed data-disabled:opacity-50 data-focus:bg-gray-50 data-selected:bg-blue-50"
                >
                  <option.Icon
                    className={clsx(
                      "mt-0.5 h-4 w-4 shrink-0",
                      option.iconClassName,
                    )}
                  />
                  <span className="flex-1">
                    <span className="block text-sm font-medium text-gray-900">
                      {option.label}
                    </span>
                    <span className="block text-xs text-gray-500">
                      {option.description}
                    </span>
                  </span>
                  <CheckIcon
                    className="invisible h-4 w-4 shrink-0 text-blue-600 group-data-selected:visible"
                    aria-hidden="true"
                  />
                </ListboxOption>
              ))}
            </ListboxOptions>
          </Listbox>
          <p className="mt-0.5 text-sm text-gray-600">{current.description}</p>
          {!disabled && picker.hint && (
            <p className="mt-2 text-xs text-gray-500">{picker.hint}</p>
          )}
          {visibility === DatasetVisibility.Public && dataset.publicSlug && (
            <div className="mt-3 flex items-center gap-2 text-sm text-gray-600">
              {t("Public link identifier")}
              <Clipboard value={dataset.publicSlug}>
                <code className="rounded-sm bg-gray-100 px-1.5 py-0.5 text-gray-800">
                  {dataset.publicSlug}
                </code>
              </Clipboard>
            </div>
          )}
        </div>
      </div>
      <ConfirmSharingDialog
        open={pending !== null}
        title={
          makingPublic
            ? t("Make this dataset public?")
            : t("Stop sharing this dataset publicly?")
        }
        confirmLabel={
          makingPublic ? t("Make dataset public") : t("Stop sharing publicly")
        }
        saving={saving}
        confirmDisabled={Boolean(pending && isSaveDisabled?.(pending))}
        onClose={() => setPending(null)}
        onConfirm={() => pending && save(pending)}
      >
        {warningContent && (
          <Callout variant="warning">{warningContent}</Callout>
        )}
        {pending && children?.(pending, visibility)}
      </ConfirmSharingDialog>
    </div>
  );
};

export default DatasetVisibilityPicker;
