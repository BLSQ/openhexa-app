import {
  CreateSavedQueryError,
  DeleteSavedQueryError,
  UpdateSavedQueryError,
} from "graphql/types";
import type { TFunction } from "i18next";

// Maps backend saved-query mutation error codes to user-facing messages. Shared
// by the editor hook (which toasts them) and the save dialog (which surfaces
// them as a form error), so the handled cases and their copy stay in one place.
export const createSavedQueryErrorMessage = (
  errors: CreateSavedQueryError[] | undefined | null,
  t: TFunction,
): string => {
  if (errors?.includes(CreateSavedQueryError.PermissionDenied)) {
    return t("You are not authorized to perform this action");
  }
  if (errors?.includes(CreateSavedQueryError.WorkspaceNotFound)) {
    return t("Workspace not found");
  }
  console.error("Unhandled createSavedQuery error", errors);
  return t("Unknown error");
};

export const updateSavedQueryErrorMessage = (
  errors: UpdateSavedQueryError[] | undefined | null,
  t: TFunction,
): string => {
  if (errors?.includes(UpdateSavedQueryError.PermissionDenied)) {
    return t("You are not authorized to perform this action");
  }
  if (errors?.includes(UpdateSavedQueryError.SavedQueryNotFound)) {
    return t("Saved query not found");
  }
  console.error("Unhandled updateSavedQuery error", errors);
  return t("Unknown error");
};

export const deleteSavedQueryErrorMessage = (
  errors: DeleteSavedQueryError[] | undefined | null,
  t: TFunction,
): string => {
  if (errors?.includes(DeleteSavedQueryError.PermissionDenied)) {
    return t("You are not authorized to perform this action");
  }
  if (errors?.includes(DeleteSavedQueryError.SavedQueryNotFound)) {
    return t("Saved query not found");
  }
  console.error("Unhandled deleteSavedQuery error", errors);
  return t("Unknown error");
};
