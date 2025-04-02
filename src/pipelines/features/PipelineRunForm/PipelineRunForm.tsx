import { gql } from "@apollo/client";
import { useMemo } from "react";
import GenericForm from "./GenericForm";
import IHPForm from "./IHPForm";
import { PipelineRunForm_DagFragment } from "./PipelineRunForm.generated";

type PipelineRunFormProps = {
  onSubmit(dagId: string, config: object): Promise<void>;
  dag: PipelineRunForm_DagFragment;
  fromConfig?: object;
};

function PipelineRunForm(props: PipelineRunFormProps) {
  const { onSubmit, dag, fromConfig } = props;

  const handleSubmit = (config: object) => onSubmit(dag.id, config);

  const defaultConfig = useMemo(
    () => fromConfig || dag.template.sampleConfig,
    [dag, fromConfig],
  );

  switch (dag.formCode) {
    case "ihp":
      return <IHPForm onSubmit={handleSubmit} fromConfig={defaultConfig} />;
    default:
      return <GenericForm onSubmit={handleSubmit} fromConfig={defaultConfig} />;
  }
}

PipelineRunForm.fragments = {
  dag: gql`
    fragment PipelineRunForm_dag on DAG {
      template {
        sampleConfig
      }
      formCode
      id
    }
  `,
};

export default PipelineRunForm;
