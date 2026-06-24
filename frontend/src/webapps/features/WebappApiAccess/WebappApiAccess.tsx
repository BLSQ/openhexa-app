import { gql } from "@apollo/client";
import clsx from "clsx";
import { useCallback, useEffect, useMemo, useState } from "react";
import { useTranslation } from "next-i18next";
import { toast } from "react-toastify";
import DataCard from "core/components/DataCard";
import { useDataCardSection } from "core/components/DataCard/context";
import Checkbox from "core/components/forms/Checkbox/Checkbox";
import Clipboard from "core/components/Clipboard";
import useCacheKey from "core/hooks/useCacheKey";
import { useUpdateWebappMutation } from "webapps/graphql/mutations.generated";
import { UpdateWebappError, WebappOperationScope } from "graphql/types";
import { WebappApiAccess_WebappFragment } from "./WebappApiAccess.generated";

const ALL_SCOPES = Object.values(WebappOperationScope);

const EXAMPLE_SNIPPET = `const response = await fetch("/graphql/", {
  method: "POST",
  credentials: "include",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({ query: "{ me { user { email } } }" }),
});
const { data } = await response.json();`;

function getScopeDescriptions(t: (key: string) => string) {
  return {
    [WebappOperationScope.PipelinesRead]: {
      label: t("Read pipelines"),
      description: t("Access pipeline metadata, versions, and run details"),
    },
    [WebappOperationScope.PipelinesRun]: {
      label: t("Run pipelines"),
      description: t("Start and stop pipeline runs"),
    },
    [WebappOperationScope.FilesRead]: {
      label: t("Read files"),
      description: t("Access workspace files and download objects"),
    },
    [WebappOperationScope.FilesWrite]: {
      label: t("Write files"),
      description: t("Upload, create, and delete workspace files"),
    },
    [WebappOperationScope.DatasetsRead]: {
      label: t("Read datasets"),
      description: t("Access workspace datasets, versions, and links"),
    },
    [WebappOperationScope.DatasetsWrite]: {
      label: t("Write datasets"),
      description: t("Create, update, and delete datasets and versions"),
    },
    [WebappOperationScope.UserRead]: {
      label: t("Read user info"),
      description: t("Access current user details and workspace role"),
    },
  };
}

type ApiAccessContentProps = {
  serveUrl: string;
  savedOperations: WebappOperationScope[];
  draftOperations: WebappOperationScope[];
  onToggleScope: (scope: WebappOperationScope) => void;
  onResetDraft: () => void;
};

const ApiAccessContent = ({
  serveUrl,
  savedOperations,
  draftOperations,
  onToggleScope,
  onResetDraft,
}: ApiAccessContentProps) => {
  const { t } = useTranslation();
  const section = useDataCardSection();
  const scopeDescriptions = getScopeDescriptions(t);

  // Sync the draft to the persisted value on each edit-mode transition so a
  // previous cancel never leaks unsaved toggles into the next edit session.
  useEffect(() => {
    onResetDraft();
  }, [section.isEdited, onResetDraft]);

  const operations = section.isEdited ? draftOperations : savedOperations;

  return (
    <div className="space-y-4">
      <p className="text-sm text-gray-500">
        {t(
          "Your web app can query the OpenHEXA GraphQL API on behalf of the connected user. Requests are scoped to the permissions you enable below.",
        )}
      </p>

      <div className="rounded-md bg-gray-50 p-3 space-y-2">
        <div>
          <p className="text-xs font-medium text-gray-500 mb-1">
            {t("Endpoint")}
          </p>
          <Clipboard value={`${serveUrl}graphql/`}>
            <code className="text-sm text-gray-800">{serveUrl}graphql/</code>
          </Clipboard>
        </div>
        <div>
          <p className="text-xs font-medium text-gray-500 mb-1">
            {t("Example")}
          </p>
          <Clipboard value={EXAMPLE_SNIPPET}>
            <pre className="text-xs text-gray-700 whitespace-pre overflow-x-auto">
              {EXAMPLE_SNIPPET}
            </pre>
          </Clipboard>
        </div>
      </div>

      <div
        className={clsx(
          "rounded-md border p-3",
          section.isEdited
            ? "border-blue-300 bg-blue-50"
            : "border-gray-200 bg-gray-100",
        )}
      >
        <p className="text-xs font-medium text-gray-500 mb-2">
          {t("Allowed operations")}
        </p>
        <div className="space-y-2">
          {ALL_SCOPES.map((scope) => (
            <Checkbox
              key={scope}
              name={scope}
              label={scopeDescriptions[scope].label}
              description={scopeDescriptions[scope].description}
              checked={operations.includes(scope)}
              disabled={!section.isEdited}
              onChange={() => onToggleScope(scope)}
            />
          ))}
        </div>
      </div>
    </div>
  );
};

type WebappApiAccessProps = {
  webapp: WebappApiAccess_WebappFragment;
};

const WebappApiAccess = ({ webapp }: WebappApiAccessProps) => {
  const { t } = useTranslation();
  const [updateWebapp] = useUpdateWebappMutation();
  const clearCache = useCacheKey("webapps");

  const savedOperations = useMemo(
    () => webapp.allowedOperations ?? [],
    [webapp.allowedOperations],
  );
  const [draftOperations, setDraftOperations] =
    useState<WebappOperationScope[]>(savedOperations);

  // Start each edit from the persisted value so a previous cancel never leaks
  // unsaved toggles into the next edit session.
  const resetDraft = useCallback(
    () => setDraftOperations(savedOperations),
    [savedOperations],
  );

  const toggleScope = useCallback((scope: WebappOperationScope) => {
    setDraftOperations((prev) =>
      prev.includes(scope) ? prev.filter((s) => s !== scope) : [...prev, scope],
    );
  }, []);

  const onSave = async () => {
    try {
      const { data } = await updateWebapp({
        variables: {
          input: { id: webapp.id, allowedOperations: draftOperations },
        },
      });
      const error = data?.updateWebapp?.errors?.[0];
      if (error) {
        if (error === UpdateWebappError.PermissionDenied) {
          toast.error(t("You do not have permission to update this web app"));
        } else if (error === UpdateWebappError.WebappNotFound) {
          toast.error(t("Web app not found"));
        } else {
          toast.error(t("An error occurred while updating the web app"));
        }
        return;
      }
      toast.success(t("API access updated successfully"));
      clearCache();
    } catch {
      toast.error(t("An error occurred while updating the web app"));
    }
  };

  return (
    <DataCard item={webapp}>
      <DataCard.FormSection
        title={t("API access")}
        onSave={webapp.permissions.update ? onSave : undefined}
        confirmButtonLabel={t("Save")}
        collapsible={false}
      >
        <ApiAccessContent
          serveUrl={webapp.serveUrl}
          savedOperations={savedOperations}
          draftOperations={draftOperations}
          onToggleScope={toggleScope}
          onResetDraft={resetDraft}
        />
      </DataCard.FormSection>
    </DataCard>
  );
};

WebappApiAccess.fragment = {
  webapp: gql`
    fragment WebappApiAccess_webapp on Webapp {
      id
      serveUrl
      allowedOperations
      permissions {
        update
      }
    }
  `,
};

export default WebappApiAccess;
