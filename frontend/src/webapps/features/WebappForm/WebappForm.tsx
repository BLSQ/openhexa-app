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
import WorkspaceLayout from "workspaces/layouts/WorkspaceLayout";
import useCacheKey from "core/hooks/useCacheKey";
import ImageProperty from "core/components/DataCard/ImageProperty";
import useDebounce from "core/hooks/useDebounce";
import WebappIframe from "webapps/features/WebappIframe";
import {
  CreateWebappError,
  UpdateWebappError,
  WebappType,
} from "graphql/types";
import { getWebappTypeLabel } from "webapps/helpers";

const DEFAULT_BLUESQUARE_SUPERSET_URL = "https://superset.bluesquare.org";
const buildSource: Record<WebappType, (values: any) => any> = {
  [WebappType.Iframe]: (values) => ({ iframe: { url: values.url } }),
  [WebappType.Superset]: (values) => ({
    superset: {
      instanceId: values.supersetInstanceId?.id,
      dashboardId: values.externalDashboardId,
    },
  }),
  [WebappType.Html]: (values) => ({}), //Coming soon
  [WebappType.Bundle]: (values) => ({}), //Coming soon
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

  const clearCache = useCacheKey("webapps");

  const updateExistingWebapp = async (values: any) => {
    setLoading(true);
    try {
      const source = buildSource[webapp!.type](values);
      const { data } = await updateWebapp({
        variables: {
          input: {
            id: webapp!.id,
            name: values.name,
            icon: values.icon,
            source,
          },
        },
      });
      if (data?.updateWebapp?.errors?.length) {
        const error = data.updateWebapp.errors[0];
        if (error === UpdateWebappError.PermissionDenied) {
          toast.error(t("You do not have permission to update this webapp"));
        } else if (error === UpdateWebappError.WebappNotFound) {
          toast.error(t("Webapp not found"));
        } else if (error === UpdateWebappError.SupersetInstanceNotFound) {
          toast.error(t("Superset instance not found"));
        } else if (error === UpdateWebappError.SupersetNotConfigured) {
          toast.error(t("Superset is not configured"));
        } else if (error === UpdateWebappError.TypeMismatch) {
          toast.error(t("Cannot change the type of an existing webapp"));
        }
        return;
      }
      toast.success(t("Webapp updated successfully"));
      clearCache();
    } catch (error) {
      toast.error(t("An error occurred while updating the webapp"));
    } finally {
      setLoading(false);
    }
  };

  const createNewWebapp = async (values: any) => {
    setLoading(true);
    try {
      const type = (values.type as WebappType) ?? WebappType.Iframe;
      const source = buildSource[type](values);

      const { data } = await createWebapp({
        variables: {
          input: {
            workspaceSlug: workspace.slug,
            name: values.name,
            icon: values.icon,
            source,
          },
        },
      });
      if (data?.createWebapp?.errors?.length) {
        const error = data.createWebapp.errors[0];
        if (error === CreateWebappError.AlreadyExists) {
          toast.error(t("A webapp with this name already exists"));
        } else if (error === CreateWebappError.PermissionDenied) {
          toast.error(t("You do not have permission to create a webapp"));
        } else if (error === CreateWebappError.SupersetInstanceNotFound) {
          toast.error(t("Superset instance not found"));
        } else if (error === CreateWebappError.SupersetNotConfigured) {
          toast.error(t("Superset is not configured"));
        } else if (error === CreateWebappError.WorkspaceNotFound) {
          toast.error(t("Workspace not found"));
        }
        return;
      }
      if (!data?.createWebapp?.webapp) {
        throw new Error("Webapp creation failed");
      }
      toast.success(t("Webapp created successfully"));
      clearCache();
      router.push(`/workspaces/${workspace.slug}/webapps`).then();
    } catch (error) {
      toast.error(t("An error occurred while creating the webapp"));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    setUrl(webapp?.url || "");
  }, [webapp]);

  return (
    <DataCard item={webapp}>
      <DataCard.Heading
        titleAccessor={(item) => item?.name || t("New Webapp")}
      />
      <DataCard.FormSection
        title={t("Webapp Details")}
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
              // Coming soon
              // WebappType.Html,
              // WebappType.Bundle,
              ...(supersetInstances.length > 0
                ? [WebappType.Superset]
                : []),
            ]}
            getOptionLabel={getWebappTypeLabel}
            onChange={(value) => setSelectedType(value as WebappType)}
          />
        )}
        <TextProperty
          id="url"
          accessor="url"
          label={t("URL")}
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
          <LinkProperty id="supersetUrl" accessor="url" label={t("URL")} />
        )}
      </DataCard.FormSection>
      {debouncedUrl && (
        <DataCard.Section
          title={t("Preview")}
          collapsible={false}
          loading={loading}
        >
          <WebappIframe url={debouncedUrl} style={{ height: "65vh" }} />
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
      type
      icon
      source {
        ... on SupersetSource {
          instance {
            id
            name
            url
          }
          dashboardId
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
