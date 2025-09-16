import { useState } from "react";
import { XMarkIcon, PlusIcon } from "@heroicons/react/24/outline";
import Tag from "core/features/Tag";
import { Tag_TagFragment } from "core/features/Tag.generated";
import { useDataCardProperty } from "./context";
import DataCard from "../DataCard";
import { PropertyDefinition } from "./types";
import Button from "../Button";
import Field from "../forms/Field";

type EditableTagPropertyProps = PropertyDefinition;

const EditableTagProperty = (props: EditableTagPropertyProps) => {
  const { defaultValue } = props;
  const { property, section } = useDataCardProperty<Tag_TagFragment[]>(props);
  const [newTagName, setNewTagName] = useState("");

  const addTag = () => {
    if (!newTagName.trim()) return;

    const existingTag = property.formValue?.find(tag =>
      tag.name.toLowerCase() === newTagName.trim().toLowerCase()
    );

    if (existingTag) return;

    const newTag: Tag_TagFragment = {
      id: newTagName.trim(),
      name: newTagName.trim(),
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
              size="sm"
              onClick={addTag}
              disabled={!newTagName.trim()}
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