import { useEffect, useState } from "react";
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
import SelectProperty from "core/components/DataCard/SelectProperty";
import LinkProperty from "core/components/DataCard/LinkProperty";
import WorkspaceLayout from "workspaces/layouts/WorkspaceLayout";
import useCacheKey from "core/hooks/useCacheKey";
import ImageProperty from "core/components/DataCard/ImageProperty";
import useDebounce from "core/hooks/useDebounce";
import WebappIframe from "webapps/features/WebappIframe";
import { WebappType } from "graphql/types";
import { getWebappTypeLabel } from "webapps/helpers";

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

  const clearCache = useCacheKey("webapps");

  const updateExistingWebapp = async (values: any) => {
    setLoading(true);
    try {
      const source = buildSource[webapp!.type](values);
      await updateWebapp({
        variables: {
          input: {
            id: webapp!.id,
            name: values.name,
            icon: values.icon,
            source,
          },
        },
      }).then(() => {
        toast.success(t("Webapp updated successfully"));
        clearCache();
      });
    } catch (error) {
      toast.error(t("An error occurred while updating the webapp"));
    } finally {
      setLoading(false);
    }
  };

  const createNewWebapp = async (values: any) => {
    setLoading(true);
    try {
      const source = buildSource[values.type as WebappType](values);

      await createWebapp({
        variables: {
          input: {
            workspaceSlug: workspace.slug,
            name: values.name,
            icon: values.icon,
            source,
          },
        },
      }).then(({ data }) => {
        if (!data?.createWebapp?.webapp) {
          throw new Error("Webapp creation failed");
        }
        toast.success(t("Webapp created successfully"));
        clearCache();
        router.push(`/workspaces/${workspace.slug}/webapps`);
      });
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
          <SelectProperty
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
              WebappType.Superset,
            ]}
            getOptionLabel={getWebappTypeLabel}
            onChange={(value) => setSelectedType(value as WebappType)}
          />
        )}
        {selectedType === WebappType.Iframe && (
          <TextProperty
            id="url"
            accessor="url"
            label={t("URL")}
            required
            onChange={(e) => setUrl(e.target.value)}
          />
        )}
        {selectedType === WebappType.Superset && (
          <>
            <SelectProperty
              id="supersetInstanceId"
              accessor="source.instance"
              label={t("Superset Instance")}
              required
              options={supersetInstances}
              getOptionLabel={(inst) => inst?.name ?? ""}
              by="id"
            />
            <TextProperty
              id="externalDashboardId"
              accessor="source.dashboardId"
              label={t("Dashboard ID")}
              required
            />
            {webapp && (
              <LinkProperty
                id="supersetUrl"
                accessor="url"
                label={t("URL")}
              />
            )}
          </>
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
