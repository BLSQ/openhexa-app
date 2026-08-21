import { TagIcon, XMarkIcon } from "@heroicons/react/24/outline";
import clsx from "clsx";
import Badge from "core/components/Badge";
import Popover from "core/components/Popover";
import Checkbox from "core/components/forms/Checkbox";
import { useTranslation } from "next-i18next";

type TagFilterProps = {
  tags?: string[] | null;
  value: string[];
  onChange: (tags: string[]) => void;
};

const TagFilter = ({ tags, value, onChange }: TagFilterProps) => {
  const { t } = useTranslation();

  if (!tags?.length) {
    return null;
  }

  const toggle = (tag: string) =>
    onChange(
      value.includes(tag) ? value.filter((t) => t !== tag) : [...value, tag],
    );

  return (
    <Popover
      placement="bottom-start"
      trigger={
        <div className="flex items-center gap-2 px-3 py-2 border border-gray-300 rounded-md hover:bg-gray-50 cursor-pointer">
          <TagIcon className="w-4 h-4 text-gray-600 shrink-0" />
          <span className="text-sm text-gray-700">{t("Tags")}</span>
          <Badge
            className={clsx(
              "bg-purple-100 text-purple-700 ring-purple-400/20 w-7 justify-center",
              value.length === 0 && "invisible",
            )}
          >
            {value.length}
          </Badge>
        </div>
      }
    >
      <div className="w-64 max-h-80 overflow-y-auto">
        <div className="flex items-center justify-between mb-3">
          <h3 className="text-sm font-semibold text-gray-900">
            {t("Filter by tags")}
          </h3>
          {value.length > 0 && (
            <button
              onClick={() => onChange([])}
              className="text-xs text-gray-500 hover:text-gray-700 flex items-center gap-1"
            >
              <XMarkIcon className="w-3 h-3" />
              {t("Clear")}
            </button>
          )}
        </div>
        <div className="space-y-2">
          {tags.map((tag) => (
            <div
              key={tag}
              className="flex items-center gap-2 cursor-pointer hover:bg-gray-50 p-1 rounded"
              onClick={() => toggle(tag)}
            >
              <Checkbox
                checked={value.includes(tag)}
                onChange={() => toggle(tag)}
              />
              <span className="text-sm text-gray-700">{tag}</span>
            </div>
          ))}
        </div>
      </div>
    </Popover>
  );
};

export default TagFilter;
