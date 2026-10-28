import { TrashIcon } from "@heroicons/react/24/outline";
import Button from "core/components/Button";
import { SettingsCard } from "core/components/DetailShell";
import Spinner from "core/components/Spinner";
import { SavedQueryVisibility } from "graphql/types";
import { useTranslation } from "next-i18next";
import { useEffect, useState } from "react";
import { toast } from "react-toastify";
import DeleteSavedQueryTrigger from "workspaces/features/SavedQueries/DeleteSavedQueryTrigger";
import { SavedQuery_SavedQueryFragment } from "workspaces/features/SavedQueries/SavedQueries.generated";
import SavedQueryVisibilityPicker from "workspaces/features/SavedQueries/SavedQueryVisibilityPicker";
import { useSavedQueryMutations } from "workspaces/features/SavedQueries/useSavedQueryMutations";

type SavedQuerySettingsProps = {
  savedQuery: SavedQuery_SavedQueryFragment;
  onSaved: (savedQuery: SavedQuery_SavedQueryFragment) => void;
  onDeleted: () => void;
};

const INPUT_CLASS =
  "w-full rounded-md border border-gray-300 px-2.5 py-2 text-[13px] text-gray-900 outline-hidden focus:border-blue-600 focus:ring-1 focus:ring-blue-600 disabled:bg-gray-50 disabled:text-gray-500";

// The details of a saved query (name, description, sharing) and its danger
// zone, laid out like the web app and pipeline settings tabs.
const SavedQuerySettings = ({
  savedQuery,
  onSaved,
  onDeleted,
}: SavedQuerySettingsProps) => {
  const { t } = useTranslation();
  const canEdit = savedQuery.permissions.update;
  const canEditVisibility = savedQuery.permissions.updateVisibility;
  const { update, updating } = useSavedQueryMutations();

  const [name, setName] = useState(savedQuery.name);
  const [description, setDescription] = useState(savedQuery.description ?? "");
  const [visibility, setVisibility] = useState<SavedQueryVisibility>(
    savedQuery.visibility,
  );

  useEffect(() => {
    setName(savedQuery.name);
    setDescription(savedQuery.description ?? "");
    setVisibility(savedQuery.visibility);
  }, [savedQuery]);

  const isDirty =
    name !== savedQuery.name ||
    description !== (savedQuery.description ?? "") ||
    visibility !== savedQuery.visibility;

  const handleCancel = () => {
    setName(savedQuery.name);
    setDescription(savedQuery.description ?? "");
    setVisibility(savedQuery.visibility);
  };

  const handleSave = async () => {
    if (!name.trim()) {
      toast.error(t("The query needs a name"));
      return;
    }
    const res = await update({
      id: savedQuery.id,
      name: name.trim(),
      description,
      // Only sent when it changed: echoing it back needs the stricter permission.
      ...(visibility !== savedQuery.visibility ? { visibility } : {}),
    });
    if (res.ok) {
      toast.success(t("Query updated"));
      onSaved(res.savedQuery);
    } else {
      toast.error(res.message);
    }
  };

  return (
    <div className="mx-auto max-w-4xl space-y-4">
      <SettingsCard
        title={t("Details")}
        footer={
          canEdit && (
            <>
              <button
                onClick={handleCancel}
                disabled={!isDirty || updating}
                className="rounded border border-gray-300 bg-white px-3.5 py-2 text-[13px] font-medium text-gray-800 hover:bg-gray-50 disabled:opacity-60"
              >
                {t("Cancel")}
              </button>
              <button
                onClick={handleSave}
                disabled={!isDirty || updating}
                className="inline-flex items-center gap-1.5 rounded border-none bg-blue-600 px-3.5 py-2 text-[13px] font-medium text-white hover:bg-blue-700 disabled:opacity-60"
              >
                {updating && <Spinner size="xs" />}
                {t("Save")}
              </button>
            </>
          )
        }
      >
        <div className="grid grid-cols-2 gap-x-5 gap-y-3.5">
          <div className="flex flex-col gap-1.5">
            <label className="text-xs font-medium text-gray-700">
              {t("Name")}
            </label>
            <input
              type="text"
              value={name}
              disabled={!canEdit}
              onChange={(e) => setName(e.target.value)}
              className={INPUT_CLASS}
            />
          </div>
          <div className="flex flex-col gap-1.5">
            <label className="text-xs font-medium text-gray-700">
              {t("Slug")}
            </label>
            <input
              type="text"
              value={savedQuery.slug}
              disabled
              className={`${INPUT_CLASS} font-mono`}
            />
            <span className="text-xs text-gray-500">
              {t("How web apps and the API refer to this query. It never changes.")}
            </span>
          </div>
          <div className="col-span-2 flex flex-col gap-1.5">
            <label className="text-xs font-medium text-gray-700">
              {t("Description")}
            </label>
            <textarea
              value={description}
              disabled={!canEdit}
              onChange={(e) => setDescription(e.target.value)}
              rows={3}
              className={INPUT_CLASS}
            />
          </div>
          <div className="col-span-2 flex flex-col gap-1.5">
            <label className="text-xs font-medium text-gray-700">
              {t("Sharing")}
            </label>
            <SavedQueryVisibilityPicker
              value={visibility}
              onChange={setVisibility}
              disabled={!canEdit || !canEditVisibility}
            />
          </div>
        </div>
      </SettingsCard>

      {savedQuery.permissions.delete && (
        <SettingsCard title={t("Danger zone")} className="border-red-200">
          <div className="flex items-center justify-between gap-4">
            <div className="text-sm">
              <div className="font-medium text-gray-900">
                {t("Delete this query")}
              </div>
              <div className="text-gray-500">
                {t("The query and its history are removed for everyone.")}
              </div>
            </div>
            <DeleteSavedQueryTrigger savedQuery={savedQuery} onDelete={onDeleted}>
              {({ onClick }) => (
                <Button
                  variant="danger"
                  onClick={onClick}
                  leadingIcon={<TrashIcon className="h-4 w-4" />}
                  className="whitespace-nowrap"
                >
                  {t("Delete")}
                </Button>
              )}
            </DeleteSavedQueryTrigger>
          </div>
        </SettingsCard>
      )}
    </div>
  );
};

export default SavedQuerySettings;
