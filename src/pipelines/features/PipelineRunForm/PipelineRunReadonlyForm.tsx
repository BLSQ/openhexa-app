import { gql } from "@apollo/client";
import { useMemo } from "react";
import GenericForm from "./GenericForm";
import IHPForm from "./IHPForm";
import { PipelineRunForm_DagFragment } from "./PipelineRunForm.generated";
import {
  PipelineRunReadonlyForm_DagFragment,
  PipelineRunReadonlyForm_DagRunFragment,
} from "./PipelineRunReadonlyForm.generated";

type PipelineRunReadonlyFormProps = {
  dag: PipelineRunReadonlyForm_DagFragment;
  dagRun: PipelineRunReadonlyForm_DagRunFragment;
};

function PipelineRunReadonlyForm(props: PipelineRunReadonlyFormProps) {
  const { dag, dagRun } = props;

  switch (dag.formCode) {
    case "ihp":
      return <IHPForm readOnly fromConfig={dagRun.config} />;
    default:
      return <GenericForm readOnly fromConfig={dagRun.config} />;
  }
}

PipelineRunReadonlyForm.fragments = {
  dag: gql`
    fragment PipelineRunReadonlyForm_dag on DAG {
      formCode
      id
    }
  `,
  dagRun: gql`
    fragment PipelineRunReadonlyForm_dagRun on DAGRun {
      config
    }
  `,
};

export default PipelineRunReadonlyForm;
