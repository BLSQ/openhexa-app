import { useState, useEffect } from "react";
import { useTranslation } from "next-i18next";
import Dialog from "core/components/Dialog";
import Field from "core/components/forms/Field";
import Input from "core/components/forms/Input";
import Textarea from "core/components/forms/Textarea";
import Button from "core/components/Button";
import { ErrorAlert } from "core/components/Alert";

interface AddConfigurationDialogProps {
  open: boolean;
  onClose: () => void;
  onSave: (name: string, value: any) => void;
  editingConfig?: { name: string; value: any } | null;
}

const AddConfigurationDialog = ({
  open,
  onClose,
  onSave,
  editingConfig,
}: AddConfigurationDialogProps) => {
  const { t } = useTranslation();

  const getInitialValue = (val: any): string => {
    if (typeof val === "string") {
      return val;
    }
    return JSON.stringify(val, null, 2);
  };

  const [name, setName] = useState("");
  const [value, setValue] = useState("");
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (open) {
      if (editingConfig) {
        setName(editingConfig.name);
        setValue(getInitialValue(editingConfig.value));
      } else {
        setName("");
        setValue("");
      }
      setError(null);
    }
  }, [open, editingConfig]);

  const parseValue = (inputValue: string): any => {
    const trimmedValue = inputValue.trim();

    if (!trimmedValue) {
      return "";
    }

    try {
      return JSON.parse(trimmedValue);
    } catch (e) {
      return trimmedValue;
    }
  };

  const handleSave = () => {
    if (!name.trim()) {
      setError(t("Name is required"));
      return;
    }

    const finalValue = parseValue(value);
    onSave(name.trim(), finalValue);
    handleClose();
  };

  const handleClose = () => {
    setName("");
    setValue("");
    setError(null);
    onClose();
  };

  return (
    <Dialog open={open} onClose={handleClose}>
      <Dialog.Title>
        {editingConfig ? t("Edit Configuration") : t("Add Configuration")}
      </Dialog.Title>
      <Dialog.Content className="space-y-4">
        {error && (
          <ErrorAlert onClose={() => setError(null)}>{error}</ErrorAlert>
        )}

        <Field name="name" label={t("Name")} required>
          <Input
            id="name"
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder={t("Configuration name")}
            required
          />
        </Field>

        <Field
          name="value"
          label={t("Value")}
          help={t(
            'Enter a value as plain text or JSON. Examples: "hello", 123, true, {"key": "value"}, [1, 2, 3]',
          )}
        >
          <Textarea
            id="value"
            value={value}
            onChange={(e) => setValue(e.target.value)}
            placeholder={t("Enter value as text or JSON...")}
            rows={4}
            className="font-mono text-sm"
          />
        </Field>
      </Dialog.Content>
      <Dialog.Actions>
        <Button variant="secondary" onClick={handleClose}>
          {t("Cancel")}
        </Button>
        <Button onClick={handleSave}>
          {editingConfig ? t("Update") : t("Add")}
        </Button>
      </Dialog.Actions>
    </Dialog>
  );
};

export default AddConfigurationDialog;
