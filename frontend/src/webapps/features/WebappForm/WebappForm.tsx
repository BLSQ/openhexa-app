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
import SwitchProperty from "core/components/DataCard/SwitchProperty";
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

const HtmlContentEditor = ({ id, accessor, label, required, visible }: any) => {
  const { property, section } = useDataCardProperty({ id, accessor, label, required, visible });
  const { t } = useTranslation();
  const debouncedContent = useDebounce(property.formValue || "", 500);

  if (!property.visible) {
    return null;
  }

  if (section.isEdited && !property.readonly) {
    return (
      <>
        <DataCard.Property property={property}>
          <CodeEditor
            value={property.formValue || ""}
            onChange={(value) => property.setValue(value)}
            height="400px"
            lang="html"
          />
        </DataCard.Property>
        {debouncedContent && (
          <div className="mt-4">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              {t("Preview")}
            </label>
            <iframe
              srcDoc={debouncedContent}
              className="w-full border border-gray-300 rounded"
              style={{ height: "400px" }}
              sandbox="allow-scripts"
              title="HTML Preview"
            />
          </div>
        )}
      </>
    );
  }

  return (
    <>
      <DataCard.Property property={property}>
        <div className="text-sm text-gray-500 italic">
          {property.displayValue ? "HTML content provided" : "No content"}
        </div>
      </DataCard.Property>
      {property.displayValue && (
        <div className="mt-4">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            {t("Preview")}
          </label>
          <iframe
            srcDoc={property.displayValue}
            className="w-full border border-gray-300 rounded"
            style={{ height: "400px" }}
            sandbox="allow-scripts"
            title="HTML Preview"
          />
        </div>
      )}
    </>
  );
};

const BundleFileInput = ({ id, accessor, label, required, helpText, visible, webapp, workspace }: any) => {
  const { property, section } = useDataCardProperty({ id, accessor, label, required, visible });
  const { t } = useTranslation();
  const [isLoading, setIsLoading] = useState(false);
  const [fileName, setFileName] = useState<string>("");

  useEffect(() => {
    if (!section.isEdited) {
      setFileName("");
    }
  }, [section.isEdited]);

  if (!property.visible) {
    return null;
  }

  const handleFilesChange = async (files: readonly File[]) => {
    if (files.length > 0) {
      const file = files[0];
      const MAX_FILE_SIZE = 50 * 1024 * 1024; // 50MB
      if (file.size > MAX_FILE_SIZE) {
        toast.error(t("The selected file is too large. Maximum allowed size is 50MB."));
        return;
      }
      setFileName(file.name);
      setIsLoading(true);

      const reader = new FileReader();
      reader.onload = () => {
        const base64 = reader.result as string;
        const base64Data = base64.split(",")[1];
        property.setValue(base64Data);
        setIsLoading(false);
      };
      reader.onerror = () => {
        setIsLoading(false);
      };
      reader.readAsDataURL(file);
    }
  };

  if (section.isEdited && !property.readonly) {
    return (
      <>
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
            {isLoading && (
              <p className="text-sm text-blue-600">{t("Loading file...")}</p>
            )}
          </div>
        </DataCard.Property>
        {fileName && !isLoading && (
          <div className="mt-4 p-4 bg-blue-50 border border-blue-200 rounded">
            <p className="text-sm text-gray-700 mb-2">
              <span className="font-medium">✓ {fileName}</span> {t("uploaded successfully")}
            </p>
            <p className="text-sm text-gray-600">
              {webapp
                ? t("The bundle will be updated after saving. Preview will refresh after the update.")
                : t("Preview will be available after creation. The bundle contains your app's HTML, CSS, JavaScript, and other assets.")}
            </p>
          </div>
        )}
        {!fileName && webapp && webapp.type === WebappType.Bundle && (
          <div className="mt-4">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              {t("Current Bundle Preview")}
            </label>
            <WebappIframe
              type={WebappType.Bundle}
              workspaceSlug={workspace?.slug}
              webappSlug={webapp?.slug}
              style={{ height: "400px" }}
            />
          </div>
        )}
      </>
    );
  }

  return (
    <>
      <DataCard.Property property={property}>
        <div className="text-sm text-gray-500 italic">
          {webapp && webapp.type === WebappType.Bundle ? t("Bundle uploaded") : t("No bundle")}
        </div>
      </DataCard.Property>
      {webapp && webapp.type === WebappType.Bundle && (
        <div className="mt-4">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            {t("Preview")}
          </label>
          <WebappIframe
            type={WebappType.Bundle}
            workspaceSlug={workspace?.slug}
            webappSlug={webapp?.slug}
            style={{ height: "400px" }}
          />
        </div>
      )}
    </>
  );
};

const TypeAwareFields = ({
  webapp,
  workspace,
  currentType,
}: {
  webapp?: WebappForm_WebappFragment;
  workspace: WebappForm_WorkspaceFragment;
  currentType: WebappType;
  onTypeChange: (type: WebappType) => void;
}) => {
  const { t } = useTranslation();
  const [url, setUrl] = useState(webapp?.url || "");
  const debouncedUrl = useDebounce(url, 500);

  const showUrlField =
    currentType === WebappType.Iframe || currentType === WebappType.Superset;

  return (
    <>
      <TextProperty
        id="url"
        accessor="url"
        label={t("URL")}
        required
        defaultValue=""
        visible={(_displayValue: any, _isEdited: any, formData: any) => {
          const type = formData.type || currentType;
          return type === WebappType.Iframe || type === WebappType.Superset;
        }}
        onChange={(e) => {
          setUrl(e.target.value);
        }}
      />
      <HtmlContentEditor
        id="content"
        accessor="content"
        label={t("Content")}
        required
        defaultValue=""
        visible={(_displayValue: any, _isEdited: any, formData: any) => {
          const type = formData.type || currentType;
          return type === WebappType.Html;
        }}
      />
      <BundleFileInput
        id="bundle"
        accessor="bundle"
        label={t("Bundle File")}
        required
        defaultValue=""
        helpText={t(
          "Upload a zip file containing your built React app (index.html + assets)",
        )}
        visible={(_displayValue: any, _isEdited: any, formData: any) => {
          const type = formData.type || currentType;
          return type === WebappType.Bundle;
        }}
        webapp={webapp}
        workspace={workspace}
      />
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
  const [currentType, setCurrentType] = useState<WebappType>(
    webapp?.type || WebappType.Iframe,
  );

  const clearCache = useCacheKey("webapps");

  const getRequiredContentDescription = (type: WebappType): string => {
    switch (type) {
      case WebappType.Iframe:
        return "a valid URL";
      case WebappType.Html:
        return "HTML content";
      case WebappType.Bundle:
        return "a bundle file (.zip)";
      case WebappType.Superset:
        return "a valid Superset URL";
      default:
        return "content";
    }
  };

  const buildWebappContentInput = (values: any, allowMissingContent: boolean = false) => {
    const type = values.type || currentType;

    const cleaned: any = {
      name: values.name,
      description: values.description,
      icon: values.icon,
      isPublic: values.isPublic,
    };

    switch (type) {
      case WebappType.Iframe:
        if (values.url) {
          cleaned.content = { iframe: { url: values.url } };
        }
        break;
      case WebappType.Html:
        if (values.content) {
          cleaned.content = { html: { content: values.content } };
        }
        break;
      case WebappType.Bundle:
        if (values.bundle) {
          cleaned.content = { bundle: { bundle: values.bundle } };
        }
        break;
      case WebappType.Superset:
        if (values.url) {
          cleaned.content = { superset: { url: values.url } };
        }
        break;
    }

    if (!cleaned.content && !allowMissingContent) {
      throw new Error(
        `Content is required for ${type} webapp. Please provide ${getRequiredContentDescription(type)}.`
      );
    }

    return cleaned;
  };

  const updateExistingWebapp = async (values: any) => {
    try {
      const cleanedInput = buildWebappContentInput(values, true);
      const result = await updateWebapp({
        variables: { input: { id: webapp?.id, ...cleanedInput } },
      });

      if (result.data?.updateWebapp?.success) {
        toast.success(t("Webapp updated successfully"));
        clearCache();
      } else {
        toast.error(t("An error occurred while updating the webapp"));
      }
    } catch (error) {
      toast.error(t("An error occurred while updating the webapp"));
    }
  };

  const createNewWebapp = async (values: any) => {
    try {
      const cleanedInput = buildWebappContentInput(values, false);
      await createWebapp({
        variables: { input: { workspaceSlug: workspace.slug, ...cleanedInput } },
      }).then(({ data }) => {
        if (!data?.createWebapp?.webapp) {
          throw new Error("Webapp creation failed");
        }
        toast.success(t("Webapp created successfully"));
        router.push(`/workspaces/${workspace.slug}/webapps`);
      });
    } catch (error) {
      toast.error(t("An error occurred while creating the webapp"));
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
          workspace={workspace}
          currentType={currentType}
          onTypeChange={setCurrentType}
        />
        <SwitchProperty
          id="isPublic"
          accessor="isPublic"
          label={t("Public Access")}
          help={t(
            "Allow anyone with the link to view this web app without logging in",
          )}
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
      isPublic
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
