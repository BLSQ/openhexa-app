import React, { ChangeEvent } from "react";
import DataCard from "./DataCard";
import { useDataCardProperty } from "./context";
import { PropertyDefinition } from "./types";
import { useTranslation } from "next-i18next";

type ImagePropertyProps = PropertyDefinition & {
  className?: string;
  editButtonLabel?: string;
  placeholder?: string;
  accept?: string[];
};

const ImageProperty = (props: ImagePropertyProps) => {
  const {
    className,
    placeholder = "/images/placeholder.svg",
    editButtonLabel,
    accept = ["image/png", "image/jpeg", "image/jpg"],
    ...delegated
  } = props;
  const { property, section } = useDataCardProperty(delegated);
  const { t } = useTranslation();

  if (!property.visible) {
    return null;
  }

  const handleImageChange = (event: ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onloadend = () => {
        // Create an image element to check dimensions
        const img = new Image();
        img.onload = () => {
          const maxWidth = 64;
          const maxHeight = 64;

          let width = img.width;
          let height = img.height;
          const canvas = document.createElement("canvas");

          // Calculate new dimensions if image is too large
          if (width > maxWidth || height > maxHeight) {
            const ratio = Math.min(maxWidth / width, maxHeight / height);
            width = width * ratio;
            height = height * ratio;

            canvas.width = width;
            canvas.height = height;
          } else {
            canvas.width = img.width;
            canvas.height = img.height;
          }

          // Draw and resize image on canvas
          const ctx = canvas.getContext("2d");
          ctx?.drawImage(img, 0, 0, canvas.width, canvas.height);

          // Get resized image as a png encoded in base64
          const resizedImage = canvas.toDataURL("image/png", 0.7);
          property.setValue(resizedImage);
        };
        img.src = reader.result as string;
      };
      reader.readAsDataURL(file);
    }
  };

  const imageSrc = property.formValue || property.displayValue || placeholder;

  if (section.isEdited && !property.readonly) {
    return (
      <DataCard.Property property={property}>
        <div className="flex items-center">
          {imageSrc && (
            <label htmlFor="file-upload" className="cursor-pointer">
              <img
                src={imageSrc}
                alt="Image Preview"
                className="h-12 w-12 rounded"
              />
            </label>
          )}
          <label
            htmlFor="file-upload"
            className="cursor-pointer bg-white rounded-md font-medium text-indigo-600 hover:text-indigo-500 underline ml-3"
          >
            <input
              id="file-upload"
              name="file-upload"
              type="file"
              accept={accept.join(",")}
              onChange={handleImageChange}
              className="sr-only"
            />
            <span>{editButtonLabel ?? t("Edit")}</span>
          </label>
        </div>
      </DataCard.Property>
    );
  } else {
    return (
      <DataCard.Property property={property}>
        {imageSrc && (
          <img
            src={imageSrc}
            alt="Image Preview"
            className="h-12 w-12 rounded"
          />
        )}
      </DataCard.Property>
    );
  }
};

export default ImageProperty;
