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
      <Dialog.Title onClose={onClose}>{t("Preview data source")}</Dialog.Title>
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
                {t("Id")}
              </th>
              <th className={TableClasses.thCondensed} scope="col">
                {t("Code")}
              </th>
              <th className={TableClasses.thCondensed} scope="col">
                <span className="sr-only">{t("Actions")}</span>
              </th>
            </tr>
          </thead>
          <tbody className={TableClasses.tbody}>
            <tr>
              <td className={TableClasses.tdCondensed}>Psychoses</td>
              <td className={TableClasses.tdCondensed}>-</td>
              <td className={TableClasses.tdCondensed}>aAzdq921</td>
              <td className={TableClasses.tdCondensed}>DE_xZAs</td>
              <td className={TableClasses.tdCondensed}>
                <div className="flex items-center justify-end gap-6">
                  <Button
                    size="sm"
                    variant="white"
                    leadingIcon={<DocumentDownloadIcon className="h-4" />}
                  >
                    {t("Extract")}
                  </Button>
                  <a
                    href=""
                    className="inline-flex items-center font-medium text-blue-600 hover:text-blue-900"
                  >
                    {t("Preview")}
                    <ChevronRightIcon className="ml-1 h-4" />
                  </a>
                </div>
              </td>
            </tr>
            <tr>
              <td className={TableClasses.tdCondensed}>Psychoses</td>
              <td className={TableClasses.tdCondensed}>-</td>
              <td className={TableClasses.tdCondensed}>aAzdq921</td>
              <td className={TableClasses.tdCondensed}>DE_xZAs</td>
              <td className={TableClasses.tdCondensed}>
                <div className="flex items-center justify-end gap-6">
                  <Button
                    size="sm"
                    variant="white"
                    leadingIcon={<DocumentDownloadIcon className="h-4" />}
                  >
                    {t("Extract")}
                  </Button>
                  <a
                    href=""
                    className="inline-flex items-center font-medium text-blue-600 hover:text-blue-900"
                  >
                    {t("Preview")}
                    <ChevronRightIcon className="ml-1 h-4" />
                  </a>
                </div>
              </td>
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
