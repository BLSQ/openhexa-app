import { PlayIcon } from "@heroicons/react/24/outline";
import Button from "core/components/Button";
import SidePanel from "core/components/SidePanel";
import Spinner from "core/components/Spinner";
import { useTranslation } from "next-i18next";
import { RunPipelineDialog_PipelineFragment } from "workspaces/features/RunPipelineDialog/RunPipelineDialog.generated";
import RunPipelineFormFields from "workspaces/features/RunPipelineDialog/RunPipelineFormFields";
import useRunPipelineForm, {
  RunPipelineInput,
} from "workspaces/features/RunPipelineDialog/useRunPipelineForm";

type RunPipelinePanelProps = {
  pipeline: RunPipelineDialog_PipelineFragment & { name?: string | null };
  onClose: () => void;
  onLaunch: (input: RunPipelineInput) => Promise<unknown>;
};

const RunPipelinePanel = ({
  pipeline,
  onClose,
  onLaunch,
}: RunPipelinePanelProps) => {
  const { t } = useTranslation();
  const formState = useRunPipelineForm({
    pipeline,
    open: true,
    async onSubmit(input) {
      await onLaunch(input);
    },
  });
  const { form, activeVersion } = formState;

  return (
    <SidePanel.Content
      title={t("Run pipeline")}
      subtitle={`${pipeline.name ?? pipeline.code} · ${t("configure and launch")}`}
      onClose={onClose}
      onSubmit={form.handleSubmit}
      footer={
        <div className="flex flex-1 justify-end gap-2">
          <Button variant="white" onClick={onClose}>
            {t("Cancel")}
          </Button>
          <Button
            type="submit"
            variant="primary"
            disabled={form.isSubmitting || !activeVersion}
            leadingIcon={<PlayIcon className="h-4 w-4" />}
          >
            {t("Run")}
          </Button>
        </div>
      }
    >
      <div className="px-5 py-4">
        {!pipeline.currentVersion ? (
          <p className="text-sm text-gray-500">
            {t("This pipeline has not been uploaded yet")}
          </p>
        ) : !activeVersion ? (
          <div className="flex items-center justify-center py-8">
            <Spinner size="md" />
          </div>
        ) : (
          <RunPipelineFormFields
            pipeline={pipeline}
            state={formState}
            singleColumn
          />
        )}
      </div>
    </SidePanel.Content>
  );
};

export default RunPipelinePanel;
