import Spinner from "core/components/Spinner";
import Tabs from "core/components/Tabs";
import dynamic from "next/dynamic";
import { useTranslation } from "next-i18next";
import { usePipelineRunProfileQuery } from "pipelines/graphql/queries.generated";
import { ReactNode } from "react";
import { Profile } from "./profile";

const TimelineChart = dynamic(() => import("./TimelineChart"), { ssr: false });
const CodeProfile = dynamic(() => import("./CodeProfile"), { ssr: false });

const Message = ({ children }: { children: ReactNode }) => (
  <div className="w-full text-center text-sm text-gray-500">{children}</div>
);

type RunProfileProps = {
  runId: string;
  enableProfiling: boolean;
  isFinished: boolean;
};

const RunProfile = ({
  runId,
  enableProfiling,
  isFinished,
}: RunProfileProps) => {
  const { t } = useTranslation();
  const { data, loading } = usePipelineRunProfileQuery({
    variables: { runId },
    skip: !enableProfiling || !isFinished,
  });
  const profile = data?.pipelineRun?.profile as Profile | null | undefined;
  const version = data?.pipelineRun?.version;
  if (!enableProfiling) {
    return (
      <Message>
        {t(
          'This run was not profiled. Check "Profile this run" in the advanced settings when launching the pipeline to see where your pipeline spends its time.',
        )}
      </Message>
    );
  }
  if (!isFinished) {
    return <Message>{t("Profile will appear here on run completion")}</Message>;
  }
  if (loading) {
    return (
      <div className="flex justify-center py-4">
        <Spinner size="md" />
      </div>
    );
  }
  if (!profile) {
    return (
      <Message>
        {t(
          "No profile was recorded for this run. The workspace image may not support profiling.",
        )}
      </Message>
    );
  }
  if (!profile.lanes.length) {
    return (
      <Message>{t("No pipeline code was found in this profile.")}</Message>
    );
  }
  const timeline = <TimelineChart profile={profile} />;
  // Notebook pipelines are not versioned, so the code that ran is not available and the line
  // times recorded for their cells (files named after a hash of the cell code) cannot be mapped
  // back to it: they only get the timeline. Profiles recorded before line times were added have
  // no `files` either.
  if (
    !version ||
    !version.files.some((file) => profile.files?.[file.path]?.length)
  ) {
    return timeline;
  }
  return (
    <Tabs>
      <Tabs.Tab label={t("Code")} className="pt-4">
        <CodeProfile
          profile={profile}
          name={version.versionName}
          files={version.files}
        />
      </Tabs.Tab>
      <Tabs.Tab label={t("Timeline")} className="pt-4">
        {timeline}
      </Tabs.Tab>
    </Tabs>
  );
};

export default RunProfile;
