import { CreateSavedQueryInput, UpdateSavedQueryInput } from "graphql/types";
import useCacheKey from "core/hooks/useCacheKey";
import { useTranslation } from "next-i18next";
import { useCallback } from "react";
import {
  SavedQuery_SavedQueryFragment,
  useCreateSavedQueryMutation,
  useUpdateSavedQueryMutation,
} from "workspaces/features/SavedQueries/SavedQueries.generated";
import {
  createSavedQueryErrorMessage,
  updateSavedQueryErrorMessage,
} from "workspaces/features/SavedQueries/savedQueryErrors";

// Normalised outcome shared by every caller: either the persisted query, or a
// ready-to-surface message. Callers decide how to surface it (toast vs form
// error) and what to do on success (navigate vs update local state).
export type SavedQueryMutationResult =
  | { ok: true; savedQuery: SavedQuery_SavedQueryFragment }
  | { ok: false; message: string };

// Single owner of the create/update write path: runs the mutation, unwraps the
// success/errors envelope, invalidates the saved-queries cache, and maps error
// codes to copy. The editor hook and the save dialog both go through here so
// this envelope handling lives in one place.
export const useSavedQueryMutations = () => {
  const { t } = useTranslation();
  const clearCache = useCacheKey("savedQueries");
  const [createMutation, { loading: creating }] = useCreateSavedQueryMutation();
  const [updateMutation, { loading: updating }] = useUpdateSavedQueryMutation();

  const create = useCallback(
    async (input: CreateSavedQueryInput): Promise<SavedQueryMutationResult> => {
      const { data } = await createMutation({ variables: { input } });
      const result = data?.createSavedQuery;
      if (result?.success && result.savedQuery) {
        clearCache();
        return { ok: true, savedQuery: result.savedQuery };
      }
      return {
        ok: false,
        message: createSavedQueryErrorMessage(result?.errors, t),
      };
    },
    [createMutation, clearCache, t],
  );

  const update = useCallback(
    async (input: UpdateSavedQueryInput): Promise<SavedQueryMutationResult> => {
      const { data } = await updateMutation({ variables: { input } });
      const result = data?.updateSavedQuery;
      if (result?.success && result.savedQuery) {
        clearCache();
        return { ok: true, savedQuery: result.savedQuery };
      }
      return {
        ok: false,
        message: updateSavedQueryErrorMessage(result?.errors, t),
      };
    },
    [updateMutation, clearCache, t],
  );

  return { create, update, creating, updating };
};
