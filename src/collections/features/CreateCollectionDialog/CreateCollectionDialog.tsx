import useCollectionForm from "collections/hooks/useCollectionForm";
import Button from "core/components/Button";
import Dialog from "core/components/Dialog";
import { useTranslation } from "next-i18next";
import { useRouter } from "next/router";
import { useCallback } from "react";
import CollectionPartialForm from "../CollectionPartialForm";

type CreateCollectionDialogProps = {
  open: boolean;
  onClose(): void;
};

const CreateCollectionDialog = (props: CreateCollectionDialogProps) => {
  const { open, onClose } = props;
  const router = useRouter();
  const form = useCollectionForm((collection) =>
    router.push({ pathname: "/collections/[id]", query: { id: collection.id } })
  );
  const { t } = useTranslation();

  const handleClose = useCallback(() => onClose(), [onClose]);
  return (
    <Dialog onClose={handleClose} open={open}>
      <Dialog.Title onClose={handleClose}>
        {t("Create a collection")}
      </Dialog.Title>
      <form onSubmit={form.handleSubmit}>
        <Dialog.Content>
          <CollectionPartialForm form={form} />
        </Dialog.Content>
        <Dialog.Actions>
          <Button variant="white" onClick={handleClose}>
            {t("Cancel")}
          </Button>
          <Button disabled={form.isSubmitting || !form.isValid} type="submit">
            {t("Create")}
          </Button>
        </Dialog.Actions>
      </form>
    </Dialog>
  );
};

export default CreateCollectionDialog;
