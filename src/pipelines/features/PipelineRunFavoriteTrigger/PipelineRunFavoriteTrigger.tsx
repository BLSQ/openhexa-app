import { gql, useMutation } from "@apollo/client";
import Button from "core/components/Button";
import Dialog from "core/components/Dialog";
import Field from "core/components/forms/Field";
import useToggle from "core/hooks/useToggle";
import { useTranslation } from "next-i18next";
import { ReactElement, useState } from "react";
import PipelineRunFavoriteIcon from "../PipelineRunFavoriteIcon";
import {
  PipelineRunFavoriteTrigger_RunFragment,
  SetFavoriteRunMutation,
  SetFavoriteRunMutationVariables,
} from "./PipelineRunFavoriteTrigger.generated";
import { toast } from "react-toastify";

type PipelineRunFavoriteTriggerProps = {
  run: PipelineRunFavoriteTrigger_RunFragment;
  children?(args: {
    onClick(): void;
    run: PipelineRunFavoriteTrigger_RunFragment;
  }): ReactElement;
};

const PipelineRunFavoriteTrigger = (props: PipelineRunFavoriteTriggerProps) => {
  const { run, children } = props;
  const { t } = useTranslation();
  const [label, setLabel] = useState("");
  const [isToggled, { toggle, setFalse }] = useToggle(false);
  const [setFavorite] = useMutation<
    SetFavoriteRunMutation,
    SetFavoriteRunMutationVariables
  >(gql`
    mutation setFavoriteRun($input: SetDAGRunFavoriteInput!) {
      setDAGRunFavorite(input: $input) {
        success
        errors
        dagRun {
          id
          label
          isFavorite
        }
      }
    }
  `);

  const onClick = async () => {
    if (run.isFavorite) {
      if (
        window.confirm(
          t("Are you sure to remove this run from your favorites?"),
        )
      ) {
        const { data } = await setFavorite({
          variables: { input: { id: run.id, isFavorite: false } },
        });
        if (!data?.setDAGRunFavorite?.success) {
          toast.error(t("We were not able to remove it from your favorites"));
        }
      }
    } else {
      toggle();
    }
  };

  const onSubmit = async (event: { preventDefault(): void }) => {
    event.preventDefault();
    if (!label) return;
    const { data } = await setFavorite({
      variables: { input: { id: run.id, isFavorite: true, label } },
    });
    if (!data?.setDAGRunFavorite?.success) {
      toast.error(t("We were not able to add this run to your favorites"));
    }
    setFalse();
    setLabel("");
  };

  return (
    <>
      {children ? (
        children({ onClick, run })
      ) : (
        <button
          onClick={onClick}
          title={
            run.isFavorite ? t("Remove from favorites") : t("Add to favorites")
          }
        >
          <PipelineRunFavoriteIcon run={run} animate />
        </button>
      )}
      {!run.isFavorite && (
        <Dialog open={isToggled} onClose={setFalse}>
          <form onSubmit={onSubmit}>
            <Dialog.Title>{t("Mark this run as favorite")}</Dialog.Title>
            <Dialog.Content>
              <Dialog.Description>
                {t(
                  "Marking this run as favorite will put it on top of the list of the runs. Please enter a label that better describes it.",
                )}
              </Dialog.Description>
              <Field
                label={t("Favorite label")}
                required
                name="label"
                autoComplete={"off"}
                onChange={(e) => setLabel(e.target.value)}
                value={label}
              />
            </Dialog.Content>
            <Dialog.Actions>
              <Button variant="white" onClick={setFalse}>
                {t("Cancel")}
              </Button>
              <Button type="submit" disabled={!label}>
                {t("Save")}
              </Button>
            </Dialog.Actions>
          </form>
        </Dialog>
      )}
    </>
  );
};

PipelineRunFavoriteTrigger.fragments = {
  run: gql`
    fragment PipelineRunFavoriteTrigger_run on DAGRun {
      id
      label
      isFavorite
      ...PipelineRunFavoriteIcon_run
    }
    ${PipelineRunFavoriteIcon.fragments.run}
  `,
};

export default PipelineRunFavoriteTrigger;
