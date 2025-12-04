import React, { useEffect, useState } from "react";
import { useRouter } from "next/router";
import { useTranslation } from "next-i18next";
import { toast } from "react-toastify";
import {
  useCreateWebappMutation,
  useUpdateWebappMutation,
} from "webapps/graphql/mutations.generated";
import { gql } from "@apollo/client";
import {
  WebappForm_WebappFragment,
  WebappForm_WorkspaceFragment,
} from "./WebappForm.generated";
import DataCard from "core/components/DataCard";
import TextProperty from "core/components/DataCard/TextProperty";
import SelectProperty from "core/components/DataCard/SelectProperty";
import WorkspaceLayout from "workspaces/layouts/WorkspaceLayout";
import useCacheKey from "core/hooks/useCacheKey";
import ImageProperty from "core/components/DataCard/ImageProperty";
import useDebounce from "core/hooks/useDebounce";
import WebappIframe from "webapps/features/WebappIframe";
import { WebappType } from "graphql/types";

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
  const debouncedUrl = useDebounce(url, 500);

  const clearCache = useCacheKey("webapps");

  const updateExistingWebapp = async (values: any) => {
    setLoading(true);
    try {
      await updateWebapp({
        variables: { input: { id: webapp?.id, ...values } },
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
      await createWebapp({
        variables: { input: { workspaceSlug: workspace.slug, ...values } },
      }).then(({ data }) => {
        if (!data?.createWebapp?.webapp) {
          throw new Error("Webapp creation failed");
        }
        toast.success(t("Webapp created successfully"));
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
        <SelectProperty
          id="type"
          accessor="type"
          label={t("Type")}
          required
          defaultValue={WebappType.Iframe}
          options={[
            WebappType.Iframe,
            WebappType.Html,
            WebappType.Bundle,
            WebappType.Superset,
          ]}
          getOptionLabel={(option) => {
            switch (option) {
              case WebappType.Iframe:
                return "iFrame";
              case WebappType.Html:
                return "HTML";
              case WebappType.Bundle:
                return "Bundle";
              case WebappType.Superset:
                return "Superset";
              default:
                return option;
            }
          }}
        />
        <TextProperty
          id="url"
          accessor="url"
          label={t("URL")}
          required
          onChange={(e) => {
            setUrl(e.target.value);
          }}
        />
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
      permissions {
        update
        delete
      }
    }
  `,
  workspace: gql`
    fragment WebappForm_workspace on Workspace {
      ...WorkspaceLayout_workspace
    }
    ${WorkspaceLayout.fragments.workspace}
  `,
};

export default WebappForm;
