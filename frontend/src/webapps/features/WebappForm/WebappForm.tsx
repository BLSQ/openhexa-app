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
import { getWebappTypeLabel } from "webapps/helpers";
import { useDataCardProperty } from "core/components/DataCard/context";

type WebappFormProps = {
  webapp?: WebappForm_WebappFragment;
  workspace: WebappForm_WorkspaceFragment;
};

const BundleFileInput = ({ id, accessor, label, required, helpText }: any) => {
  const { property, section } = useDataCardProperty({ id, accessor, label, required });
  const { t } = useTranslation();

  if (!property.visible) {
    return null;
  }

  const handleFileChange = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = () => {
        const base64 = reader.result as string;
        const base64Data = base64.split(",")[1];
        property.setValue(base64Data);
      };
      reader.readAsDataURL(file);
    }
  };

  if (section.isEdited && !property.readonly) {
    return (
      <DataCard.Property property={property}>
        <div className="space-y-2">
          <input
            type="file"
            accept=".zip"
            onChange={handleFileChange}
            required={property.required}
            className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-semibold file:bg-indigo-50 file:text-indigo-700 hover:file:bg-indigo-100"
          />
          {helpText && <p className="text-xs text-gray-500">{helpText}</p>}
        </div>
      </DataCard.Property>
    );
  }

  return (
    <DataCard.Property property={property}>
      <div className="text-sm text-gray-500 italic">
        {property.displayValue ? t("Bundle uploaded") : t("No bundle")}
      </div>
    </DataCard.Property>
  );
};

const WebappForm = ({ workspace, webapp }: WebappFormProps) => {
  const { t } = useTranslation();
  const router = useRouter();
  const [createWebapp] = useCreateWebappMutation();
  const [updateWebapp] = useUpdateWebappMutation();
  const [loading, setLoading] = useState(false);
  const [url, setUrl] = useState(webapp?.url || "");
  const [selectedType, setSelectedType] = useState<WebappType>(
    webapp?.type || WebappType.Iframe,
  );
  const debouncedUrl = useDebounce(url, 500);

  const clearCache = useCacheKey("webapps");

  const showUrlField =
    selectedType === WebappType.Iframe || selectedType === WebappType.Superset;
  const showContentField = selectedType === WebappType.Html;
  const showBundleField = selectedType === WebappType.Bundle;

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
    setSelectedType(webapp?.type || WebappType.Iframe);
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
          getOptionLabel={getWebappTypeLabel}
          onChange={(e) => {
            setSelectedType(e.target.value as WebappType);
          }}
        />
        {showUrlField && (
          <TextProperty
            id="url"
            accessor="url"
            label={t("URL")}
            required
            onChange={(e) => {
              setUrl(e.target.value);
            }}
          />
        )}
        {showContentField && (
          <TextProperty
            id="content"
            accessor="content"
            label={t("Content")}
            required
            rows={15}
          />
        )}
        {showBundleField && (
          <BundleFileInput
            id="bundle"
            accessor="bundle"
            label={t("Bundle File")}
            required
            helpText={t(
              "Upload a zip file containing your built React app (index.html + assets)",
            )}
          />
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
      content
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
