import React, { useState } from "react";
import { useTranslation } from "next-i18next";

import { FolderPlusIcon } from "@heroicons/react/24/outline";

import Button from "core/components/Button";
import Input from "core/components/forms/Input";
import Spinner from "core/components/Spinner";

interface CreateFolderButtonProps {
  disabled?: boolean;
  onCreateFolder: (folderName: string) => Promise<void>;
}

const CreateFolderButton: React.FC<CreateFolderButtonProps> = ({
  disabled = false,
  onCreateFolder,
}) => {
  const { t } = useTranslation();

  const [isCreating, setIsCreating] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [folderName, setFolderName] = useState("");

  const handleButtonClick = () => {
    setIsCreating(true);
    setFolderName("");
  };

  const handleConfirm = async () => {
    if (!folderName.trim()) return;

    setIsLoading(true);
    try {
      await onCreateFolder(folderName.trim());
      // Reset state after successful creation
      setIsCreating(false);
      setFolderName("");
    } catch (error) {
      // Keep input visible on error so user can retry
      console.error("Failed to create folder:", error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleCancel = () => {
    setIsCreating(false);
    setIsLoading(false);
    setFolderName("");
  };

  if (isCreating) {
    return (
      <div className="flex items-center gap-2">
        {isLoading ? (
          <div className="flex items-center gap-2 px-3 py-2">
            <Spinner size="sm" />
            <span className="text-gray-500">{t("Creating folder...")}</span>
          </div>
        ) : (
          <Input
            autoFocus
            value={folderName}
            onChange={(e) => setFolderName(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter") {
                e.preventDefault();
                handleConfirm();
              } else if (e.key === "Escape") {
                e.preventDefault();
                handleCancel();
              }
            }}
            onBlur={handleCancel}
            className="w-48"
            placeholder={t("New folder")}
          />
        )}
      </div>
    );
  } else {
    return (
      <Button
        variant="secondary"
        leadingIcon={<FolderPlusIcon className="h-4 w-4" />}
        onClick={handleButtonClick}
        disabled={disabled}
      >
        {t("Create a folder")}
      </Button>
    );
  }
};

export default CreateFolderButton;
