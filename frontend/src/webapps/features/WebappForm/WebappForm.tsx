import { useEffect, useMemo, useState } from "react";
import { useRouter } from "next/router";
import { useTranslation } from "next-i18next";
import { toast } from "react-toastify";
import {
  useCreateWebappMutation,
  useUpdateWebappMutation,
} from "webapps/graphql/mutations.generated";
import { useSupersetInstancesQuery } from "webapps/graphql/queries.generated";
import { gql } from "@apollo/client";
import {
  WebappForm_WebappFragment,
  WebappForm_WorkspaceFragment,
} from "./WebappForm.generated";
import DataCard from "core/components/DataCard";
import TextProperty from "core/components/DataCard/TextProperty";
import SimpleSelectProperty from "core/components/DataCard/SimpleSelectProperty";
import LinkProperty from "core/components/DataCard/LinkProperty";
import SubdomainProperty from "core/components/DataCard/SubdomainProperty";
import WorkspaceLayout from "workspaces/layouts/WorkspaceLayout";
import useCacheKey from "core/hooks/useCacheKey";
import ImageProperty from "core/components/DataCard/ImageProperty";
import SwitchProperty from "core/components/DataCard/SwitchProperty";
import useDebounce from "core/hooks/useDebounce";
import WebappIframe from "webapps/features/WebappIframe";
import WebappSourceEditor from "webapps/features/WebappSourceEditor/WebappSourceEditor";
import Checkbox from "core/components/forms/Checkbox/Checkbox";
import Clipboard from "core/components/Clipboard";
import {
  CreateWebappError,
  UpdateWebappError,
  WebappFileInput,
  WebappOperationScope,
  WebappType,
} from "graphql/types";
import { useDataCardSection } from "core/components/DataCard/context";
import { getWebappTypeLabel } from "webapps/helpers";
import { DEFAULT_HTML_TEMPLATE } from "webapps/helpers/templates";

const ALL_SCOPES = Object.values(WebappOperationScope);

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
    [WebappOperationScope.UserRead]: {
      label: t("Read user info"),
      description: t("Access current user details and workspace role"),
    },
  };
}

type ApiAccessSectionProps = {
  serveUrl: string;
  allowedOperations: WebappOperationScope[];
  onToggleScope: (scope: WebappOperationScope) => void;
};

const ApiAccessSection = ({
  serveUrl,
  allowedOperations,
  onToggleScope,
}: ApiAccessSectionProps) => {
  const { t } = useTranslation();
  const section = useDataCardSection();
  const scopeDescriptions = getScopeDescriptions(t);

  if (!section.isEdited) return null;

  return (
    <details className="pt-4">
      <summary className="cursor-pointer text-sm font-medium text-gray-500">
        {t("API Access")}
      </summary>
      <div className="mt-4 space-y-4">
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
            <Clipboard
              value={`const response = await fetch("/graphql/", {
  method: "POST",
  credentials: "include",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({ query: "{ me { user { email } } }" }),
});
const { data } = await response.json();`}
            >
              <pre className="text-xs text-gray-700 whitespace-pre overflow-x-auto">
                {`const response = await fetch("/graphql/", {
  method: "POST",
  credentials: "include",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({ query: "{ me { user { email } } }" }),
});
const { data } = await response.json();`}
              </pre>
            </Clipboard>
          </div>
        </div>

        <div>
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
                checked={allowedOperations.includes(scope)}
                onChange={() => onToggleScope(scope)}
              />
            ))}
          </div>
        </div>
      </div>
    </details>
  );
};

const DEFAULT_BLUESQUARE_SUPERSET_URL = "https://superset.bluesquare.org";

const getDefaultSourceFiles = (type: WebappType): WebappFileInput[] =>
  type === WebappType.Static
    ? [{ path: "index.html", content: DEFAULT_HTML_TEMPLATE }]
    : [];

const buildSource: Record<WebappType, (values: any) => any> = {
  [WebappType.Iframe]: (values) => ({ iframe: { url: values.url } }),
  [WebappType.Superset]: (values) => ({
    superset: {
      instanceId: values.supersetInstanceId?.id,
      dashboardId: values.externalDashboardId,
    },
  }),
  [WebappType.Static]: (values) => ({ static: values.sourceFiles ?? [] }),
};

type WebappFormProps = {
  webapp?: WebappForm_WebappFragment;
  workspace: WebappForm_WorkspaceFragment;
};

const WebappForm = ({ workspace, webapp }: WebappFormProps) => {
  const { t } = useTranslation();
  const router = useRouter();
  const [createWebapp] = useCreateWebappMutation();
  const [updateWebapp] = useUpdateWebappMutation();
  const [loading, setLoading] = useState(false);
  const [url, setUrl] = useState(webapp?.url || "");
  const [selectedType, setSelectedType] = useState<WebappType>(
    webapp?.type ?? WebappType.Iframe,
  );
  const [sourceFiles, setSourceFiles] = useState<WebappFileInput[]>(
    getDefaultSourceFiles(webapp?.type ?? WebappType.Iframe),
  );
  const [isPublic, setIsPublic] = useState(webapp?.isPublic ?? false);
  const debouncedUrl = useDebounce(url, 500);

  const { data: supersetData } = useSupersetInstancesQuery({
    variables: { workspaceSlug: workspace.slug },
  });

  const supersetInstances = supersetData?.supersetInstances ?? [];

  const defaultSupersetInstance = useMemo(
    () =>
      supersetInstances.find((inst) =>
        inst.url.startsWith(DEFAULT_BLUESQUARE_SUPERSET_URL),
      ) ?? supersetInstances[0],
    [supersetInstances],
  );

  const [allowedOperations, setAllowedOperations] = useState<
    WebappOperationScope[]
  >(webapp?.allowedOperations ?? []);

  const clearCache = useCacheKey("webapps");

  const toggleScope = (scope: WebappOperationScope) => {
    setAllowedOperations((prev) =>
      prev.includes(scope) ? prev.filter((s) => s !== scope) : [...prev, scope],
    );
  };

  const updateExistingWebapp = async (values: any) => {
    setLoading(true);
    try {
      const { data } = await updateWebapp({
        variables: {
          input: {
            id: webapp!.id,
            name: values.name,
            icon: values.icon,
            isPublic: values.isPublic,
            allowedOperations,
            subdomain: values.subdomain || null,
            ...(webapp!.type !== WebappType.Static && {
              source: buildSource[webapp!.type](values),
            }),
          },
        },
      });
      if (data?.updateWebapp?.errors?.length) {
        const error = data.updateWebapp.errors[0];
        if (error === UpdateWebappError.PermissionDenied) {
          toast.error(t("You do not have permission to update this web app"));
        } else if (error === UpdateWebappError.WebappNotFound) {
          toast.error(t("Web app not found"));
        } else if (error === UpdateWebappError.SupersetInstanceNotFound) {
          toast.error(t("Superset instance not found"));
        } else if (error === UpdateWebappError.SupersetNotConfigured) {
          toast.error(t("Superset is not configured"));
        } else if (error === UpdateWebappError.TypeMismatch) {
          toast.error(t("Cannot change the type of an existing web app"));
        } else if (error === UpdateWebappError.InvalidUrl) {
          toast.error(t("Invalid URL. Only http and https URLs are allowed"));
        } else if (error === UpdateWebappError.SubdomainNotLowercase) {
          toast.error(t("Subdomain must be lowercase"));
        } else if (error === UpdateWebappError.SubdomainTooShort) {
          toast.error(t("Subdomain must be at least 3 characters"));
        } else if (error === UpdateWebappError.SubdomainHasDots) {
          toast.error(t("Subdomain must be a single label (no dots)"));
        } else if (error === UpdateWebappError.SubdomainReserved) {
          toast.error(t("This subdomain is reserved"));
        } else if (error === UpdateWebappError.SubdomainInvalidFormat) {
          toast.error(
            t(
              "Subdomain must be alphanumeric with hyphens, no leading/trailing hyphens, and 63 characters or fewer",
            ),
          );
        } else if (error === UpdateWebappError.SubdomainAlreadyTaken) {
          toast.error(t("This subdomain is already taken"));
        }
        return;
      }
      toast.success(t("Web app updated successfully"));
      clearCache();
    } catch (error) {
      toast.error(t("An error occurred while updating the web app"));
    } finally {
      setLoading(false);
    }
  };

  const createNewWebapp = async (values: any) => {
    setLoading(true);
    try {
      const type = (values.type as WebappType) ?? WebappType.Iframe;
      const source = buildSource[type]({ ...values, sourceFiles });

      const { data } = await createWebapp({
        variables: {
          input: {
            workspaceSlug: workspace.slug,
            name: values.name,
            icon: values.icon,
            isPublic: values.isPublic,
            source,
          },
        },
      });
      if (data?.createWebapp?.errors?.length) {
        const error = data.createWebapp.errors[0];
        if (error === CreateWebappError.AlreadyExists) {
          toast.error(t("A web app with this name already exists"));
        } else if (error === CreateWebappError.PermissionDenied) {
          toast.error(t("You do not have permission to create a web app"));
        } else if (error === CreateWebappError.SupersetInstanceNotFound) {
          toast.error(t("Superset instance not found"));
        } else if (error === CreateWebappError.SupersetNotConfigured) {
          toast.error(t("Superset is not configured"));
        } else if (error === CreateWebappError.WorkspaceNotFound) {
          toast.error(t("Workspace not found"));
        } else if (error === CreateWebappError.InvalidUrl) {
          toast.error(t("Invalid URL. Only http and https URLs are allowed"));
        }
        return;
      }
      if (!data?.createWebapp?.webapp) {
        throw new Error("Webapp creation failed");
      }
      toast.success(t("Web app created successfully"));
      clearCache();
      router
        .push(
          `/workspaces/${encodeURIComponent(workspace.slug)}/webapps/${encodeURIComponent(data.createWebapp.webapp.slug)}`,
        )
        .then();
    } catch (error) {
      toast.error(t("An error occurred while creating the web app"));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    setUrl(webapp?.url || "");
    setAllowedOperations(webapp?.allowedOperations ?? []);
    setIsPublic(webapp?.isPublic ?? false);
  }, [webapp]);

  return (
    <DataCard item={webapp}>
      <DataCard.FormSection
        title={t("Web app Details")}
        onSave={
          webapp
            ? webapp.permissions.update
              ? updateExistingWebapp
              : undefined
            : createNewWebapp
        }
        collapsible={false}
        confirmButtonLabel={webapp ? t("Save") : t("Create")}
        onCancel={
          webapp
            ? undefined
            : () => router.push(`/workspaces/${workspace.slug}/webapps`)
        }
        forceEditMode={!webapp}
      >
        <TextProperty id="name" accessor="name" label={t("Name")} required />
        <ImageProperty
          id="icon"
          accessor="icon"
          label={""}
          editButtonLabel={t("Change Icon")}
        />
        {!webapp && (
          <SimpleSelectProperty
            id="type"
            accessor="type"
            label={t("Type")}
            required
            defaultValue={WebappType.Iframe}
            options={[
              WebappType.Iframe,
              WebappType.Static,
              ...(supersetInstances.length > 0 ? [WebappType.Superset] : []),
            ]}
            getOptionLabel={getWebappTypeLabel}
            onChange={(value) => {
              setSelectedType(value as WebappType);
              setSourceFiles(getDefaultSourceFiles(value as WebappType));
            }}
          />
        )}
        <TextProperty
          id="url"
          accessor="url"
          label={t("Source URL")}
          visible={selectedType === WebappType.Iframe}
          required={selectedType === WebappType.Iframe}
          onChange={(e) => setUrl(e.target.value)}
        />
        <SimpleSelectProperty
          id="supersetInstanceId"
          accessor="source.instance"
          label={t("Superset Instance")}
          visible={selectedType === WebappType.Superset}
          required={selectedType === WebappType.Superset}
          readonly={supersetInstances.length <= 1}
          defaultValue={defaultSupersetInstance}
          options={supersetInstances}
          getOptionLabel={(inst) => inst?.url ?? ""}
          getOptionValue={(inst) => inst?.id ?? ""}
        />
        <TextProperty
          id="externalDashboardId"
          accessor="source.dashboardId"
          label={t("Dashboard ID")}
          visible={selectedType === WebappType.Superset}
          required={selectedType === WebappType.Superset}
        />
        {webapp && selectedType === WebappType.Superset && (
          <LinkProperty
            id="supersetUrl"
            accessor="url"
            label={t("Dashboard URL")}
          />
        )}
        {webapp && (
          <SubdomainProperty
            id="subdomain"
            accessor="subdomain"
            label={t("Published URL")}
            help={t("The URL where this web app can be accessed")}
            currentSubdomain={webapp.subdomain}
            serveUrl={webapp.serveUrl}
          />
        )}
        <SwitchProperty
          id="isPublic"
          accessor="isPublic"
          label={t("Public access")}
          help={t(
            "When enabled, the play link can be accessed without authentication",
          )}
          onChange={setIsPublic}
        />

        {webapp && !isPublic && (
          <ApiAccessSection
            serveUrl={webapp.serveUrl}
            allowedOperations={allowedOperations}
            onToggleScope={toggleScope}
          />
        )}
      </DataCard.FormSection>
      {!webapp && selectedType === WebappType.Static && (
        <DataCard.Section title={t("Source Files")} collapsible={false}>
          <WebappSourceEditor
            initialTemplate={DEFAULT_HTML_TEMPLATE}
            onChange={(files: WebappFileInput[]) => setSourceFiles(files)}
          />
        </DataCard.Section>
      )}
      {(debouncedUrl || webapp?.url) && !loading && (
        <DataCard.Section title={t("Preview")} collapsible={false}>
          <WebappIframe
            url={
              webapp?.previewUrl && selectedType === WebappType.Static
                ? webapp.previewUrl
                : debouncedUrl || webapp?.url || ""
            }
            type={selectedType}
            style={{ height: "65vh" }}
          />
        </DataCard.Section>
      )}
    </DataCard>
  );
};

WebappForm.fragment = {
  webapp: gql`
    fragment WebappForm_webapp on Webapp {
      id
      slug
      name
      description
      url
      previewUrl
      type
      icon
      isPublic
      allowedOperations
      subdomain
      serveUrl
      source {
        ... on SupersetSource {
          instance {
            id
            name
            url
          }
          dashboardId
        }
        ... on GitSource {
          publishedVersion
        }
      }
      permissions {
        update
        delete
      }
    }
  `,
  workspace: gql`
    fragment WebappForm_workspace on Workspace {
      slug
      ...WorkspaceLayout_workspace
    }
    ${WorkspaceLayout.fragments.workspace}
  `,
};

export default WebappForm;
