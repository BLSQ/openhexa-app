import {
  Cog6ToothIcon,
  PlusCircleIcon,
  XMarkIcon,
} from "@heroicons/react/24/outline";
import Button from "core/components/Button";
import Dialog from "core/components/Dialog";
import Checkbox from "core/components/forms/Checkbox";
import Field from "core/components/forms/Field";
import Link from "core/components/Link";
import Title from "core/components/Title";
import { useTranslation } from "next-i18next";
import { useState } from "react";

export const TYPES = [
  {
    value: "postgresql",
    label: "PostgreSQL",
    iconSrc: "/static/connector_postgresql/img/symbol.svg",
  },
  {
    value: "aws_s3_bucket",
    label: "Amazon S3 Bucket",
    iconSrc: "/static/connector_s3/img/symbol.svg",
  },
  {
    value: "gcs_bucket",
    label: "Google Cloud Bucket",
    iconSrc: "/static/connector_gcs/img/symbol.svg",
  },
  {
    value: "dhis2",
    label: "DHIS2 Instance",
    iconSrc: "/static/connector_dhis2/img/symbol.svg",
  },
];
interface CreateConnectionDialogProps {
  open: boolean;
  onClose: () => void;
}

const ConnectionTypePanel = ({
  onSelect,
}: {
  onSelect(type: string): void;
}) => {
  const { t } = useTranslation();
  return (
    <div className="space-y-4">
      <p>
        {t("You can create a connection based on our supported integrations")}
      </p>
      <div className="flex flex-wrap gap-6">
        {TYPES.map((connectionType, index) => (
          <button
            key={index}
            onClick={() => onSelect(connectionType.value)}
            className="border-1 flex h-24 w-32 flex-col items-center justify-center gap-1.5 overflow-hidden rounded-md border border-gray-100 p-2 text-center shadow-md hover:border-gray-200 hover:bg-gray-100"
          >
            {connectionType.iconSrc && (
              <img src={connectionType.iconSrc} className="h-8 w-8" alt="" />
            )}
            <div className="text-sm">{connectionType.label}</div>
          </button>
        ))}
      </div>
      <p className="pt-4">{t("Or you can create a custom connection")}</p>
      <button
        onClick={() => onSelect("CUSTOM")}
        className="border-1 flex h-24 w-32 flex-col items-center justify-center gap-1.5 overflow-hidden rounded-md border border-gray-100 p-2 text-center shadow-md hover:border-gray-200 hover:bg-gray-100"
      >
        <Cog6ToothIcon className="h-16 w-16 text-gray-500" />
        <div className="text-sm">{t("Custom connection")}</div>
      </button>
    </div>
  );
};

export default function CreateCollectionDialog({
  open,
  onClose,
}: CreateConnectionDialogProps) {
  const { t } = useTranslation();
  const [selectedType, setSelectedType] = useState<string | null>(null);
  const [fields, setFields] = useState<
    { key?: string; value?: string; secret?: boolean }[]
  >([{ key: "", value: "" }]);

  const updateField = (index: number, values: any) => {
    const newFields = [...fields];
    newFields.splice(index, 1, values);
    setFields(newFields);
  };

  const handleClose = () => {
    setSelectedType(null);
    onClose();
  };

  return (
    <Dialog
      open={open}
      onClose={handleClose}
      centered={false}
      maxWidth={selectedType ? "max-w-7xl" : "max-w-3xl"}
    >
      <Dialog.Title>{t("Create a connection")}</Dialog.Title>
      {selectedType ? (
        <Dialog.Content className="flex">
          <form className="grid flex-1 grid-cols-2 gap-x-2 gap-y-4">
            <Field
              onChange={() => {}}
              type="text"
              name="name"
              label={t("Connection name")}
              placeholder={t("My connection")}
              required
            />
            <Field
              onChange={() => {}}
              name="slug"
              label={t("Slug")}
              required
              placeholder={t("MY_CONNECTION")}
            />
            <Field
              onChange={() => {}}
              name="description"
              className="col-span-2"
              label={t("Description")}
              help={t("Short description of the connection")}
              required
            />
            <div className="col-span-2 space-y-3">
              <Title level={5}>{t("Fields")}</Title>
              <div className="max-h-80 overflow-y-auto">
                {fields.map((field, index) => (
                  <div
                    key={index}
                    className="flex w-full items-center justify-end gap-2"
                  >
                    <Field
                      className="flex-1"
                      onChange={(event) =>
                        updateField(index, {
                          key: event.target.value,
                          value: field.value,
                        })
                      }
                      value={field.key}
                      name="key"
                      label={t("Key")}
                      placeholder={t("KEY_XXX")}
                      required
                    />
                    <Field
                      name="value"
                      label={t("Value")}
                      onChange={(event) =>
                        updateField(index, {
                          value: event.target.value,
                          key: field.key,
                        })
                      }
                      value={field.value}
                      placeholder={t("Text value")}
                      required
                      className="flex-1"
                    />
                    <div className="mt-3 flex gap-2">
                      <Checkbox
                        id={`secret_${index}`}
                        className="mt-1"
                        name={`secret_${index}`}
                        onChange={(event) =>
                          updateField(index, {
                            ...field,
                            secret: event.target.checked,
                          })
                        }
                        checked={field.secret ?? false}
                        label={t("Secret")}
                      />
                      <button
                        type="button"
                        onClick={() =>
                          setFields(fields.filter((_, i) => i !== index))
                        }
                      >
                        <XMarkIcon className="h-4 w-4" />
                      </button>
                    </div>
                  </div>
                ))}
              </div>

              <Button
                variant="white"
                size="sm"
                type="button"
                onClick={() => setFields([...fields, {}])}
                leadingIcon={<PlusCircleIcon className="h-4 w-4" />}
              >
                {t("Add a field")}
              </Button>
            </div>
          </form>
          <div className="ml-4 w-1/3 border-l-2 border-gray-100 pl-4">
            <Title level={4} className="">
              {t("Resources")}
            </Title>
            <p>Explanation of the parameters</p>
            <Link href="https://docs.openhexa.org">
              Link to the documentation
            </Link>
          </div>
        </Dialog.Content>
      ) : (
        <ConnectionTypePanel onSelect={setSelectedType} />
      )}
      <Dialog.Actions>
        <Button type="button" variant="white" onClick={handleClose}>
          {t("Cancel")}
        </Button>
        {selectedType && <Button disabled>{t("Create connection")}</Button>}
      </Dialog.Actions>
    </Dialog>
  );
}
