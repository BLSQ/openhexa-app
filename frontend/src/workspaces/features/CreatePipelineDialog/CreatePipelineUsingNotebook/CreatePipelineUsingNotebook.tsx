import Field from "core/components/forms/Field/Field";
import Select from "core/components/forms/Select";
import { FormInstance } from "core/hooks/useForm";
import { BucketObjectType, PipelineFunctionalType } from "graphql/types";
import { Trans, useTranslation } from "next-i18next";
import { formatPipelineFunctionalType } from "workspaces/helpers/pipelines";
import BucketObjectPicker from "workspaces/features/BucketObjectPicker";
import { CreatePipelineDialog_WorkspaceFragment } from "../CreatePipelineDialog.generated";
import { NotebookFormData } from "./useNotebookForm";

type CreatePipelineUsingNotebookProps = {
  form: FormInstance<NotebookFormData>;
  workspace: CreatePipelineDialog_WorkspaceFragment;
};

const CreatePipelineUsingNotebook = ({
  form,
  workspace,
}: CreatePipelineUsingNotebookProps) => {
  const { t } = useTranslation();

  return (
    <form onSubmit={form.handleSubmit}>
      <p className="mb-6">
        <Trans>
          You can use a Notebook from the workspace file system to be run as a
          pipeline. This is the easiest way to create a pipeline. Keep in mind
          that Notebooks are not versioned. If a user changes the notebook, the
          pipeline will be updated.
        </Trans>
      </p>
      <div className="grid gap-6">
        <Field
          name="name"
          label={t("Pipeline Name")}
          required
          placeholder={t("My Pipeline")}
          error={form.touched.name && form.errors.name}
          value={form.formData.name}
          onChange={form.handleInputChange}
        />
        <Field
          name="functionalType"
          label={t("Functional Type")}
          help={t("The functional purpose of this pipeline")}
          className="max-w-xs"
        >
          <Select
            options={Object.values(PipelineFunctionalType)}
            value={form.formData.functionalType}
            onChange={(value) =>
              form.setFieldValue("functionalType", value)
            }
            getOptionLabel={(option) =>
              option ? formatPipelineFunctionalType(option) : t("Not specified")
            }
            displayValue={(option) =>
              option ? formatPipelineFunctionalType(option) : ""
            }
            placeholder={t("Select functional type (optional)")}
            className="max-w-xs"
          />
        </Field>
        <Field
          name="notebookObject"
          label={t("Notebook")}
          required
          error={form.touched.notebookObject && form.errors.notebookObject}
          className="max-w-[230px]"
        >
          <BucketObjectPicker
            onChange={(value) =>
              form.setFieldValue("notebookObject", value)
            }
            value={form.formData.notebookObject?.key}
            exclude={(item) =>
              item.type === BucketObjectType.File &&
              !item.name.endsWith(".ipynb")
            }
            placeholder={t("Select a Jupyter notebook")}
            workspace={workspace}
          />
        </Field>
        {form.submitError && (
          <p className="text-sm text-red-500">{form.submitError}</p>
        )}
      </div>
    </form>
  );
};

export default CreatePipelineUsingNotebook;
