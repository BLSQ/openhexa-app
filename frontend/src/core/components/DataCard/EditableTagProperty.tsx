import { useState } from "react";
import { XMarkIcon, PlusIcon } from "@heroicons/react/24/outline";
import Tag from "core/features/Tag";
import { Tag_TagFragment } from "core/features/Tag.generated";
import { useDataCardProperty } from "./context";
import DataCard from "../DataCard";
import { PropertyDefinition } from "./types";
import Button from "../Button";
import Field from "../forms/Field";

/**
 * Normalize tag name according to backend Tag model requirements.
 * Converts input to lowercase, replaces spaces/underscores with hyphens,
 * removes invalid characters, and cleans up multiple hyphens.
 */
const normalizeTagName = (input: string): string => {
  if (!input || typeof input !== "string") {
    return "";
  }

  let normalized = input.toLowerCase().trim();

  // Replace spaces and underscores with hyphens
  normalized = normalized.replace(/[\s_]+/g, '-');
  // Remove any characters that aren't alphanumeric or hyphens
  normalized = normalized.replace(/[^a-z0-9-]/g, '');
  // Remove multiple consecutive hyphens
  normalized = normalized.replace(/-+/g, '-');
  // Remove leading/trailing hyphens
  normalized = normalized.replace(/^-|-$/g, '');

  return normalized;
};

const isValidTagName = (name: string): boolean => {
  return name.length >= 2 && /^[a-z0-9-]+$/.test(name);
};

type EditableTagPropertyProps = PropertyDefinition;

const EditableTagProperty = (props: EditableTagPropertyProps) => {
  const { defaultValue } = props;
  const { property, section } = useDataCardProperty<Tag_TagFragment[]>(props);
  const [newTagName, setNewTagName] = useState("");

  const addTag = () => {
    if (!newTagName.trim()) return;

    const normalizedTagName = normalizeTagName(newTagName);

    if (!isValidTagName(normalizedTagName)) return;

    const existingTag = property.formValue?.find(tag =>
      tag.name.toLowerCase() === normalizedTagName
    );

    if (existingTag) return;

    const newTag: Tag_TagFragment = {
      id: normalizedTagName,
      name: normalizedTagName,
    };

    const currentTags = property.formValue || [];
    property.setValue([...currentTags, newTag]);
    setNewTagName("");
  };

  const removeTag = (tagToRemove: Tag_TagFragment) => {
    const currentTags = property.formValue || [];
    property.setValue(currentTags.filter(tag => tag.id !== tagToRemove.id));
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      addTag();
    }
  };

  const isAddButtonDisabled = () => {
    if (!newTagName.trim()) return true;
    const normalizedTagName = normalizeTagName(newTagName);
    return !isValidTagName(normalizedTagName);
  };

  const displayTags = section.isEdited ? property.formValue : property.displayValue;

  return (
    <DataCard.Property property={property}>
      <div className="space-y-3">
        {displayTags && displayTags.length > 0 && (
          <div className="flex flex-wrap items-center gap-1.5">
            {displayTags.map((tag) => (
              <div key={tag.id} className="flex items-center gap-1">
                <Tag tag={tag} />
                {section.isEdited && (
                  <button
                    type="button"
                    onClick={() => removeTag(tag)}
                    className="text-gray-400 hover:text-red-500 transition-colors"
                    title="Remove tag"
                  >
                    <XMarkIcon className="h-3 w-3" />
                  </button>
                )}
              </div>
            ))}
          </div>
        )}

        {section.isEdited && (
          <div className="flex items-center gap-3 flex-wrap">
            <Field
              name="new-tag"
              placeholder="Add a tag..."
              value={newTagName}
              onChange={(e) => setNewTagName(e.target.value)}
              onKeyDown={handleKeyDown}
              className="w-48 min-w-0"
            />
            <Button
              type="button"
              variant="outlined"
              onClick={addTag}
              disabled={isAddButtonDisabled()}
              leadingIcon={<PlusIcon className="h-4 w-4" />}
              className="border border-gray-300 hover:border-gray-400 shrink-0"
            >
              Add Tag
            </Button>
          </div>
        )}
      </div>
    </DataCard.Property>
  );
};

export default EditableTagProperty;