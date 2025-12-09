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
import CodeEditor from "core/components/CodeEditor";
import Dropzone from "core/components/Dropzone";

type WebappFormProps = {
  webapp?: WebappForm_WebappFragment;
  workspace: WebappForm_WorkspaceFragment;
};

const HtmlContentEditor = ({ id, accessor, label, required }: any) => {
  const { property, section } = useDataCardProperty({ id, accessor, label, required });

  if (!property.visible) {
    return null;
  }

  if (section.isEdited && !property.readonly) {
    return (
      <DataCard.Property property={property}>
        <CodeEditor
          value={property.formValue || ""}
          onChange={(value) => property.setValue(value)}
          height="400px"
        />
      </DataCard.Property>
    );
  }

  return (
    <DataCard.Property property={property}>
      <div className="text-sm text-gray-500 italic">
        {property.displayValue ? "HTML content provided" : "No content"}
      </div>
    </DataCard.Property>
  );
};

const BundleFileInput = ({ id, accessor, label, required, helpText }: any) => {
  const { property, section } = useDataCardProperty({ id, accessor, label, required });
  const { t } = useTranslation();

  if (!property.visible) {
    return null;
  }

  const handleFilesChange = async (files: readonly File[]) => {
    if (files.length > 0) {
      const file = files[0];
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
          <Dropzone
            accept={{ "application/zip": [".zip"] }}
            maxFiles={1}
            onChange={handleFilesChange}
            label={t("Drag & drop a .zip file here, or click to select")}
            help={helpText}
            className="h-32"
          />
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

const TypeAwareFields = ({
  webapp,
  currentType,
  onTypeChange
}: {
  webapp?: WebappForm_WebappFragment;
  currentType: WebappType;
  onTypeChange: (type: WebappType) => void;
}) => {
  const { t } = useTranslation();
  const [url, setUrl] = useState(webapp?.url || "");
  const debouncedUrl = useDebounce(url, 500);

  const showUrlField =
    currentType === WebappType.Iframe || currentType === WebappType.Superset;
  const showContentField = currentType === WebappType.Html;
  const showBundleField = currentType === WebappType.Bundle;

  return (
    <>
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
        <HtmlContentEditor
          id="content"
          accessor="content"
          label={t("Content")}
          required
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
      {debouncedUrl && showUrlField && (
        <div className="mt-4">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            {t("Preview")}
          </label>
          <WebappIframe url={debouncedUrl} style={{ height: "400px" }} />
        </div>
      )}
    </>
  );
};

const TypeSelectProperty = ({
  currentType,
  onTypeChange,
  ...props
}: any) => {
  const { property } = useDataCardProperty(props);

  // Watch for changes in the form value and update parent state
  useEffect(() => {
    if (property.formValue && property.formValue !== currentType) {
      onTypeChange(property.formValue as WebappType);
    }
  }, [property.formValue, currentType, onTypeChange]);

  return <SelectProperty {...props} />;
};

const WebappForm = ({ workspace, webapp }: WebappFormProps) => {
  const { t } = useTranslation();
  const router = useRouter();
  const [createWebapp] = useCreateWebappMutation();
  const [updateWebapp] = useUpdateWebappMutation();
  const [loading, setLoading] = useState(false);
  const [currentType, setCurrentType] = useState<WebappType>(
    webapp?.type || WebappType.Iframe,
  );

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
    console.log("Creating webapp with values:", values);
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
      console.error("Webapp creation error:", error);
      toast.error(t("An error occurred while creating the webapp"));
    } finally {
      setLoading(false);
    }
  };

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
        <TypeSelectProperty
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
          currentType={currentType}
          onTypeChange={setCurrentType}
        />
        <TypeAwareFields
          webapp={webapp}
          currentType={currentType}
          onTypeChange={setCurrentType}
        />
      </DataCard.FormSection>
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
