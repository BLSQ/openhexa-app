import { PlusCircleIcon } from "@heroicons/react/24/outline";
import Button from "core/components/Button";
import Dialog from "core/components/Dialog";
import Checkbox from "core/components/forms/Checkbox";
import Field from "core/components/forms/Field";
import SimpleSelect from "core/components/forms/SimpleSelect";
import Title from "core/components/Title";
import { useTranslation } from "next-i18next";
import { useState } from "react";

export enum ConnectionType {
  DHSI2 = "DHSI2",
  POSTGRESQL = "POSTGRESQL",
}

interface CreateConnectionDialogProps {
  open: boolean;
  onClose: () => void;
}

const DHSI2Form = () => {
  const { t } = useTranslation();
  return (
    <div className="space-y-5">
      <Field
        onChange={() => {}}
        type="text"
        name="server_url"
        label={t("Server Url")}
        required
      />
      <Field
        onChange={() => {}}
        type="text"
        name="username"
        label={t("Username")}
        required
      />
      <Field
        onChange={() => {}}
        type="password"
        name="password"
        label={t("Password")}
        required
      />
    </div>
  );
};

const PostgresForm = () => {
  const { t } = useTranslation();
  return (
    <div className="space-y-5">
      <Field
        onChange={() => {}}
        type="text"
        name="hostname"
        label={t("Hostname")}
        required
      />
      <Field
        onChange={() => {}}
        type="text"
        name="username"
        label={t("Username")}
        required
      />
      <Field
        onChange={() => {}}
        type="password"
        name="password"
        label={t("Password")}
        required
      />
      <Field
        onChange={() => {}}
        type="text"
        name="port"
        label={t("Port")}
        required
      />
      <Field
        onChange={() => {}}
        type="text"
        name="database"
        label={t("Database")}
        required
      />
    </div>
  );
};

export default function CreateCollectionDialog({
  open,
  onClose,
}: CreateConnectionDialogProps) {
  const { t } = useTranslation();
  const [selectedType, setSelectedType] = useState<ConnectionType>();

  const handleClose = () => {
    setSelectedType(undefined);
    onClose();
  };

  return (
    <Dialog
      open={open}
      onClose={handleClose}
      maxWidth="max-w-2xl"
      centered={false}
      padding="py-2 px-2"
      className="h-2/3"
    >
      <Dialog.Description className="p-4">
        {t("Create a connection")}
      </Dialog.Description>
      <Dialog.Content className="h-[80%] overflow-y-auto px-2">
        <form className="space-y-2 ">
          <Field
            onChange={() => {}}
            type="text"
            name="name"
            label={t("Name")}
            required
          />
          <Field onChange={() => {}} name="slug" label={t("Slug")} required />
          <div>
            <label className="text-sm font-medium text-gray-600" htmlFor="type">
              {t("Connection Type")}
            </label>
            <SimpleSelect
              id="type"
              className="form-select w-full rounded-md border border-gray-300 focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
              onChange={(event) =>
                setSelectedType(
                  ConnectionType[
                    event.currentTarget.value as keyof typeof ConnectionType
                  ]
                )
              }
              required
              value={selectedType}
            >
              {Object.values(ConnectionType).map((type, index) => (
                <option key={index} value={type}>
                  {type}
                </option>
              ))}
            </SimpleSelect>
          </div>
          <Field
            onChange={() => {}}
            name="excerpt"
            label={t("Excerpt")}
            required
          />
          <Field
            onChange={() => {}}
            name="description"
            label={t("Description")}
            required
          />
          <div className="space-y-3">
            <Title level={5}>{t("Fields")}</Title>
            <div className="flex flex-row items-center space-x-5">
              <Field
                className="w-1/2"
                onChange={() => {}}
                name="key"
                label={t("Key")}
                required
              />
              <Field
                onChange={() => {}}
                name="value"
                label={t("Value")}
                required
                className="w-1/2"
              />
              <Checkbox name="secret" label={t("Secret")} />
            </div>
            <Button
              variant="white"
              leadingIcon={<PlusCircleIcon className="w-6" />}
            >
              {t("Add")}
            </Button>
          </div>
          {selectedType && selectedType === ConnectionType.POSTGRESQL && (
            <PostgresForm />
          )}
          {selectedType && selectedType === ConnectionType.DHSI2 && (
            <DHSI2Form />
          )}
        </form>
      </Dialog.Content>
      <Dialog.Actions>
        <Button variant="white" onClick={handleClose}>
          {t("Cancel")}
        </Button>
        <Button>{t("Save")}</Button>
      </Dialog.Actions>
    </Dialog>
  );
}
