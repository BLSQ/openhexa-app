import useForm, { FormInstance } from "core/hooks/useForm";
import { PipelineFunctionalType } from "graphql/types";
import { useTranslation } from "next-i18next";
import { useRouter } from "next/router";
import { useCreatePipelineMutation } from "workspaces/graphql/mutations.generated";
import { CreatePipelineDialog_WorkspaceFragment } from "../CreatePipelineDialog.generated";

export type NotebookFormData = {
  notebookObject: any;
  name: string;
  functionalType: PipelineFunctionalType | null;
};

export function useNotebookForm(
  workspace: CreatePipelineDialog_WorkspaceFragment,
): FormInstance<NotebookFormData> {
  const { t } = useTranslation();
  const router = useRouter();
  const [mutate] = useCreatePipelineMutation();

  return useForm<NotebookFormData>({
    onSubmit: async (values) => {
      const { data } = await mutate({
        variables: {
          input: {
            name: values.name,
            notebookPath: values.notebookObject.key,
            workspaceSlug: workspace.slug,
            functionalType: values.functionalType,
          },
        },
      });
      if (data?.createPipeline.success && data.createPipeline.pipeline) {
        await router.push(
          `/workspaces/${encodeURIComponent(
            router.query.workspaceSlug as string,
          )}/pipelines/${encodeURIComponent(data.createPipeline.pipeline.code)}`,
        );
      } else {
        throw new Error(t("An error occurred while creating the pipeline."));
      }
    },
    validate(values) {
      const errors: any = {};
      if (!values.notebookObject) {
        errors.notebookObject = t("You have to select a notebook");
      }
      return errors;
    },
  });
}
