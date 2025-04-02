import { gql } from "@apollo/client";
import { PlusIcon, TrashIcon } from "@heroicons/react/24/outline";
import Badge from "core/components/Badge";
import Button from "core/components/Button";
import Drawer from "core/components/Drawer/Drawer";
import Field from "core/components/forms/Field";
import Input from "core/components/forms/Input";
import Textarea from "core/components/forms/Textarea";
import { Table, TableBody } from "core/components/Table";
import Title from "core/components/Title";
import { TabularColumn } from "datasets/hooks/useTabularFileMetadata";
import { useTranslation } from "next-i18next";
import { useEffect, useMemo } from "react";
import RenderColumnAttribute from "../RenderColumnAttribute";
import { ColumnMetadataDrawer_FileFragment } from "./ColumnMetadataDrawer.generated";
import useForm from "core/hooks/useForm";
import {
  deleteColumnMetadataAttribute,
  setColumnMetadataAttribute,
} from "datasets/helpers/dataset";
import { toast } from "react-toastify";
import { DateTime } from "luxon";

type ColumnMetadataDrawerProps = {
  onClose: () => void;
  column: TabularColumn | null;
  file: ColumnMetadataDrawer_FileFragment;
};

const CELL_CLASSNAME = " h-12 py-3 px-2 first:px-4";

const AttributeRow = ({
  attribute,
  onDelete,
  onChange,
}: {
  attribute: any;
  isEdited: boolean;
  onDelete: () => void;
  onChange: ({ label, value }: { label: string; value: string }) => void;
}) => {
  const { t } = useTranslation();
  return (
    <tr>
      <td className={CELL_CLASSNAME}>
        <Input
          placeholder={t("Label")}
          name={"label"}
          fullWidth
          maxLength={255}
          value={attribute.label}
          onChange={(e) =>
            onChange({ label: e.target.value, value: attribute.value })
          }
        />
      </td>
      <td className={CELL_CLASSNAME}>
        <Input
          placeholder={t("Value")}
          name={"value"}
          fullWidth
          maxLength={255}
          value={attribute.value}
          onChange={(e) =>
            onChange({ label: attribute.label, value: e.target.value })
          }
        />
      </td>
      <td className={CELL_CLASSNAME}>
        <div className="flex items-center gap-2 justify-end">
          <Button type="button" variant="outlined" size="sm" onClick={onDelete}>
            <TrashIcon className="w-4 h-4" />
          </Button>
        </div>
      </td>
    </tr>
  );
};

type Form = {
  description: string | undefined;
  attributes: { key?: string; label: string; value: string }[];
  deletedKeys: string[];
};

export default function ColumnMetadataDrawer({
  onClose,
  column,
  file,
}: ColumnMetadataDrawerProps) {
  const form = useForm<Form>({
    getInitialState() {
      const descriptionAttribute = column?.attributes.find(
        (attr) => attr.key === `${column.key}.description`,
      );
      return {
        description: descriptionAttribute?.value ?? "",
        attributes: column
          ? column.attributes
              .filter(
                (attr) =>
                  !attr.system && attr.key !== `${column.key}.description`,
              )
              .map((attr) => ({
                key: attr.key,
                label: attr.label ?? "",
                value: attr.value ?? "",
              }))
          : [],
        deletedKeys: [],
      };
    },
    validate(values) {
      const errors = {} as any;

      for (const attr of values.attributes!) {
        if (attr.label.trim() === "" || attr.value.trim() === "") {
          errors.attributes = t("Label and value are required");
        }
      }
      return errors;
    },
    async onSubmit(values) {
      try {
        // Handle the description
        await setColumnMetadataAttribute(
          file.targetId,
          column!.key,
          `${column!.key}.description`,
          null,
          values.description ?? "",
        );

        for (const attr of values.attributes!) {
          await setColumnMetadataAttribute(
            file.targetId,
            column!.key,
            attr.key ?? null,
            attr.label,
            attr.value,
          );
        }

        for (const key of values.deletedKeys!) {
          await deleteColumnMetadataAttribute(file.targetId, key);
        }
        onClose();
        toast.info(t("Metadata updated."));
      } catch (err: any) {
        toast.error(err.message);
      }
    },
  });

  useEffect(() => {
    if (column) {
      form.resetForm();
    }
  }, [column]);

  const lastUpdated = useMemo(() => {
    if (!column || !column.attributes.length) return null;

    const sortedAttributes = column.attributes
      .filter((x) => !x.system)
      .sort((a, b) => (b.updatedAt > a.updatedAt ? 1 : -1));
    return sortedAttributes[0];
  }, [column]);

  const onDelete = (index: number) => {
    const key = form.formData.attributes![index].key;
    if (key) {
      form.setFieldValue("deletedKeys", [...form.formData.deletedKeys!, key]);
    }
    form.setFieldValue(
      "attributes",
      form.formData.attributes!.filter((_, i) => i !== index),
    );
  };

  const onChange = (
    index: number,
    { label, value }: { label: string; value: string },
  ) => {
    const newAttributes = [...form.formData.attributes!];
    newAttributes[index] = { ...newAttributes[index], label, value };
    form.setFieldValue("attributes", newAttributes);
  };

  const { t } = useTranslation();
  return (
    <Drawer open={!!column} setOpen={onClose} width="max-w-2xl">
      {column && (
        <>
          <form
            className="flex-1 h-full flex flex-col"
            onSubmit={form.handleSubmit}
          >
            <Drawer.Title className="flex items-center justify-between gap-2">
              <span>{column.name}</span>
              <RenderColumnAttribute
                column={column}
                attributeKeys={["data_type"]}
              >
                {(data_type) => (
                  <Badge
                    className="font-mono bg-amber-50 ring-amber-500/20"
                    size="sm"
                  >
                    {data_type?.value}
                  </Badge>
                )}
              </RenderColumnAttribute>
            </Drawer.Title>

            <Drawer.Content className="flex-1">
              <Field label={t("Description")} name="description">
                <Textarea
                  name="description"
                  rows={10}
                  onChange={(e) =>
                    form.setFieldValue("description", e.target.value)
                  }
                  value={form.formData.description}
                  placeholder={t("Enter a description for this column")}
                />
              </Field>
              <Title
                level={5}
                className="mt-4 flex items-center gap-2 justify-between"
              >
                <span>{t("Attributes")}</span>
                <Button
                  type="button"
                  size="sm"
                  variant="secondary"
                  leadingIcon={<PlusIcon className="w-4 h-4" />}
                  onClick={() => {
                    form.setFieldValue("attributes", [
                      ...form.formData.attributes!,
                      { label: "", value: "" },
                    ]);
                  }}
                >
                  {t("Attribute")}
                </Button>
              </Title>
              {form.formData.attributes!.length > 0 ? (
                <div className="rounded-sm overflow-hidden">
                  <Table>
                    <thead>
                      <tr className="bg-gray-50 text-left text-xs font-medium text-gray-500 uppercase tracking-wider ">
                        <th className={CELL_CLASSNAME}>{t("Label")}</th>
                        <th className={CELL_CLASSNAME}>{t("Value")}</th>
                        <th className={CELL_CLASSNAME}></th>
                      </tr>
                    </thead>
                    <TableBody>
                      {form.formData.attributes!.map(
                        (attr: any, index: number) => (
                          <AttributeRow
                            key={index}
                            attribute={attr}
                            isEdited={false}
                            onDelete={() => onDelete(index)}
                            onChange={(attr) => onChange(index, attr)}
                          />
                        ),
                      )}
                    </TableBody>
                  </Table>
                  {form.errors.attributes && (
                    <div className="text-red-500 py-2">
                      {form.errors.attributes}
                    </div>
                  )}
                </div>
              ) : (
                <span>{t("No attributes found")}</span>
              )}
              {form.submitError && (
                <div className="text-red-500">{form.submitError}</div>
              )}
            </Drawer.Content>
            <Drawer.Footer className="border-t border-gray-200 flex items-center">
              {lastUpdated && (
                <div className="text-xs text-gray-500 flex-1">
                  {t("Last updated on {{datetime}} by {{user}}", {
                    datetime: DateTime.fromISO(
                      lastUpdated.updatedAt,
                    ).toLocaleString(DateTime.DATETIME_SHORT),
                    user:
                      lastUpdated.updatedBy?.displayName ??
                      t("an unknown user"),
                  })}
                </div>
              )}
              <Button type="button" variant="outlined" onClick={onClose}>
                {t("Close")}
              </Button>
              <Button
                type="submit"
                variant="primary"
                disabled={!form.isDirty || form.isSubmitting}
              >
                {t("Save")}
              </Button>
            </Drawer.Footer>
          </form>
        </>
      )}
    </Drawer>
  );
}

ColumnMetadataDrawer.fragments = {
  file: gql`
    fragment ColumnMetadataDrawer_file on DatasetVersionFile {
      id
      targetId
      attributes {
        id
        key
        value
        label
        system
        __typename
      }
      properties
    }
  `,
};
