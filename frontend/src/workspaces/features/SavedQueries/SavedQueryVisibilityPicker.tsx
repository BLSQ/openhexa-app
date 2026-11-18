import SharingPicker from "core/features/Sharing/SharingPicker";
import { SavedQueryVisibility } from "graphql/types";
import { useTranslation } from "next-i18next";
import {
  canChangeVisibility,
  useSavedQueryVisibilityOptions,
} from "workspaces/features/SavedQueries/savedQueryVisibility";

type SavedQueryVisibilityPickerProps = {
  value: SavedQueryVisibility;
  onChange: (visibility: SavedQueryVisibility) => void;
  disabled?: boolean;
  // Sharing with the workspace (and unsharing) is the author's right; sharing publicly
  // is also open to workspace and organization admins. The two are gated
  // separately because a user can hold either one without the other.
  canUpdateVisibility?: boolean;
  canShare?: boolean;
};

const SavedQueryVisibilityPicker = ({
  value,
  onChange,
  disabled = false,
  canUpdateVisibility = true,
  canShare = false,
}: SavedQueryVisibilityPickerProps) => {
  const { t } = useTranslation();
  const options = useSavedQueryVisibilityOptions();

  return (
    <SharingPicker
      options={options}
      value={value}
      onChange={onChange}
      // The current value always stays selectable (a no-op), so a query whose
      // visibility the user may not change still shows its state as checked.
      isOptionDisabled={(optionValue) =>
        disabled ||
        !canChangeVisibility(value, optionValue, {
          canUpdateVisibility,
          canShare,
        })
      }
      hint={
        !disabled &&
        !canShare &&
        value !== SavedQueryVisibility.Public &&
        t(
          "Only the author, workspace admins and organization admins can make a query public.",
        )
      }
    />
  );
};

export default SavedQueryVisibilityPicker;
