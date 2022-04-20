import { DocumentDownloadIcon } from "@heroicons/react/outline";
import { ChevronRightIcon } from "@heroicons/react/solid";
import Button from "components/Button";
import Dialog from "components/Dialog";
import { TableClasses } from "components/Table";
import { useTranslation } from "next-i18next";

type CollectionDataSourceViewerDialogProps = {
  open: boolean;
  onClose: () => void;
};

const CollectionDataSourceViewerDialog = (
  props: CollectionDataSourceViewerDialogProps
) => {
  const { open, onClose } = props;
  const { t } = useTranslation();
  return (
    <Dialog open={open} onClose={onClose} maxWidth="max-w-3xl">
      <Dialog.Title onClose={onClose}>{t("Details")}</Dialog.Title>
      <Dialog.Content>
        <table className={TableClasses.table}>
          <thead className={TableClasses.thead}>
            <tr>
              <th className={TableClasses.thCondensed} scope="col">
                {t("Name")}
              </th>
              <th className={TableClasses.thCondensed} scope="col">
                {t("Type")}
              </th>
              <th className={TableClasses.thCondensed} scope="col">
                {t("Code")}
              </th>
            </tr>
          </thead>
          <tbody className={TableClasses.tbody}>
            <tr>
              <td className={TableClasses.tdCondensed}>HF Visits</td>
              <td className={TableClasses.tdCondensed}>Data element</td>
              <td className={TableClasses.tdCondensed}>data_element_de</td>
            </tr>
            <tr>
              <td className={TableClasses.tdCondensed}>
                Level of water per month
              </td>
              <td className={TableClasses.tdCondensed}>Indicator</td>
              <td className={TableClasses.tdCondensed}>id_indicator_lwpm</td>
            </tr>
            <tr>
              <td className={TableClasses.tdCondensed}>An indicator</td>
              <td className={TableClasses.tdCondensed}>Indicator</td>
              <td className={TableClasses.tdCondensed}>id_indicator_xaz</td>
            </tr>
          </tbody>
        </table>
      </Dialog.Content>
      <Dialog.Actions>
        <Button onClick={onClose} variant="secondary">
          {t("Close")}
        </Button>
      </Dialog.Actions>
    </Dialog>
  );
};

export default CollectionDataSourceViewerDialog;
