import { useState } from "react";
import { useTranslation } from "next-i18next";
import { PencilIcon, PlusIcon, TrashIcon } from "@heroicons/react/24/outline";
import Button from "core/components/Button";
import AddConfigurationDialog from "../AddConfigurationDialog";

interface ConfigurationListProps {
  configuration: Record<string, any>;
  onChange: (newConfiguration: Record<string, any>) => void;
  disabled?: boolean;
}

const ConfigurationList = ({
  configuration = {},
  onChange,
  disabled = false,
}: ConfigurationListProps) => {
  const { t } = useTranslation();
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [editingConfig, setEditingConfig] = useState<{
    name: string;
    value: any;
  } | null>(null);

  const configEntries = Object.entries(configuration);

  const handleAdd = (name: string, value: any) => {
    const newConfig = { ...configuration, [name]: value };
    onChange(newConfig);
  };

  const handleEdit = (oldName: string, newName: string, value: any) => {
    const newConfig = { ...configuration };
    if (oldName !== newName) {
      delete newConfig[oldName];
    }
    newConfig[newName] = value;
    onChange(newConfig);
  };

  const handleDelete = (name: string) => {
    const newConfig = { ...configuration };
    delete newConfig[name];
    onChange(newConfig);
  };

  const openEditDialog = (name: string, value: any) => {
    setEditingConfig({ name, value });
    setIsDialogOpen(true);
  };

  const openAddDialog = () => {
    setEditingConfig(null);
    setIsDialogOpen(true);
  };

  const closeDialog = () => {
    setIsDialogOpen(false);
    setEditingConfig(null);
  };

  const handleSave = (name: string, value: any) => {
    if (editingConfig) {
      handleEdit(editingConfig.name, name, value);
    } else {
      handleAdd(name, value);
    }
  };

  const formatValue = (value: any): string => {
    if (typeof value === "string") {
      return value;
    }
    return JSON.stringify(value);
  };

  const getValueType = (value: any): string => {
    if (typeof value === "string") return "text";
    if (Array.isArray(value)) return "array";
    if (value === null) return "null";
    if (typeof value === "object") return "JSON";
    return typeof value;
  };

  const getValueTypeColor = (value: any): string => {
    const type = getValueType(value);
    switch (type) {
      case "text": return "bg-green-100 text-green-800";
      case "number": return "bg-blue-100 text-blue-800";
      case "boolean": return "bg-purple-100 text-purple-800";
      case "array": return "bg-orange-100 text-orange-800";
      case "JSON": return "bg-gray-100 text-gray-800";
      case "null": return "bg-red-100 text-red-800";
      default: return "bg-blue-100 text-blue-800";
    }
  };

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        {!disabled && (
          <Button
            size="sm"
            variant="secondary"
            onClick={openAddDialog}
            leadingIcon={<PlusIcon className="h-4 w-4" />}
          >
            {t("Add Configuration")}
          </Button>
        )}
      </div>

      {configEntries.length === 0 && !disabled ? (
        <div className="space-y-2">
          <textarea
            className="w-full p-3 border border-gray-300 rounded-lg font-mono text-sm resize-none bg-gray-50"
            rows={1}
            placeholder={t("Click 'Add Configuration' to create your first property")}
            value=""
            disabled
          />
        </div>
      ) : configEntries.length === 0 ? (
        <div className="prose text-sm text-gray-500 italic">
          Not set
        </div>
      ) : (
        <div className="space-y-2">
          {configEntries.map(([name, value]) => (
            <div
              key={name}
              className="flex items-center justify-between p-3 bg-gray-50 rounded-lg border"
            >
              <div className="flex-1 min-w-0">
                <div className="flex items-center space-x-3">
                  <span className="font-medium text-gray-900 text-sm">
                    {name}
                  </span>
                  <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getValueTypeColor(value)}`}>
                    {getValueType(value)}
                  </span>
                </div>
                <div className="mt-1 text-sm text-gray-600 font-mono break-all">
                  {formatValue(value)}
                </div>
              </div>
              {!disabled && (
                <div className="flex items-center space-x-1 ml-4">
                  <Button
                    size="sm"
                    variant="secondary"
                    onClick={() => openEditDialog(name, value)}
                    leadingIcon={<PencilIcon className="h-3 w-3" />}
                  >
                    {t("Edit")}
                  </Button>
                  <Button
                    size="sm"
                    variant="secondary"
                    onClick={() => handleDelete(name)}
                    leadingIcon={<TrashIcon className="h-3 w-3" />}
                    className="text-red-600 hover:text-red-700"
                  >
                    {t("Delete")}
                  </Button>
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      <AddConfigurationDialog
        open={isDialogOpen}
        onClose={closeDialog}
        onSave={handleSave}
        editingConfig={editingConfig}
      />
    </div>
  );
};

export default ConfigurationList;