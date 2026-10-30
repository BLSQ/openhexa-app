import {
  CreateSavedQueryError,
  DeleteSavedQueryError,
  UpdateSavedQueryError,
} from "graphql/types";
import type { TFunction } from "i18next";

// Maps backend saved-query mutation error codes to user-facing messages. Shared
// by the editor hook (which toasts them) and the save dialog (which surfaces
// them as a form error), so the handled cases and their copy stay in one place.

// A saved query's history lives on the git server, and the backend refuses a change
// it cannot record rather than losing a point in that history. Nothing was kept, so
// the one useful thing to tell the user is to try again.
const VERSIONING_UNAVAILABLE_MESSAGE = (t: TFunction): string =>
  t("Could not save: the query history is unavailable. Please try again.");
// The backend only reports a code for a save, not the offending name, so the copy
// can at most point at the two things that must agree: the SQL and the declarations.
const INVALID_TEMPLATE_MESSAGE = (t: TFunction): string =>
  t(
    "Could not save: the query uses parameters that are not declared, or its template syntax is invalid.",
  );
const INVALID_PARAMETERS_MESSAGE = (t: TFunction): string =>
  t("Could not save: the parameter declarations are not valid.");
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
  if (errors?.includes(CreateSavedQueryError.VersioningUnavailable)) {
    return VERSIONING_UNAVAILABLE_MESSAGE(t);
  }
  if (errors?.includes(CreateSavedQueryError.InvalidTemplate)) {
    return INVALID_TEMPLATE_MESSAGE(t);
  }
  if (errors?.includes(CreateSavedQueryError.InvalidParameters)) {
    return INVALID_PARAMETERS_MESSAGE(t);
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
  if (errors?.includes(UpdateSavedQueryError.VersioningUnavailable)) {
    return VERSIONING_UNAVAILABLE_MESSAGE(t);
  }
  if (errors?.includes(UpdateSavedQueryError.InvalidTemplate)) {
    return INVALID_TEMPLATE_MESSAGE(t);
  }
  if (errors?.includes(UpdateSavedQueryError.InvalidParameters)) {
    return INVALID_PARAMETERS_MESSAGE(t);
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
