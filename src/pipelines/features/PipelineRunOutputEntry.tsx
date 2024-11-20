import { gql } from "@apollo/client";
import { PaperClipIcon } from "@heroicons/react/24/outline";
import Anchor from "core/components/Anchor";
import Spinner from "core/components/Spinner";
import { useTranslation } from "next-i18next";
import { getRunOutputDownloadURL } from "pipelines/helpers/runs";
import { useState } from "react";
import { PipelineRunOutputEntry_OutputFragment } from "./PipelineRunOutputEntry.generated";
import { toast } from "react-toastify";

type PipelineRunOutputEntryProps = {
  output: PipelineRunOutputEntry_OutputFragment;
};

const PipelineRunOutputEntry = (props: PipelineRunOutputEntryProps) => {
  const { output } = props;
  const { t } = useTranslation();
  const [isLoading, setLoading] = useState(false);

  const onClick = async () => {
    setLoading(true);
    const url = await getRunOutputDownloadURL(output.uri);
    if (!url) {
      setLoading(false);
      toast.warning(t("We were unable to create a link for this output."));
      return;
    }

    const anchor = document.createElement("a");
    anchor.href = url;
    document.body.appendChild(anchor);
    anchor.click();
    document.body.removeChild(anchor);
    setLoading(false);
  };

  if (output.uri.startsWith("https://")) {
    return (
      <Anchor href={output.uri} target="_blank" rel="noreferrer">
        {output.title}
      </Anchor>
    );
  } else {
    return (
      <span
        className="inline-flex cursor-pointer items-center gap-1 text-blue-600 hover:text-blue-500"
        onClick={onClick}
      >
        {output.title}
        {isLoading ? <Spinner size="xs" /> : <PaperClipIcon className="w-3" />}
      </span>
    );
  }
};

PipelineRunOutputEntry.fragments = {
  output: gql`
    fragment PipelineRunOutputEntry_output on DAGRunOutput {
      title
      uri
    }
  `,
};

export default PipelineRunOutputEntry;
