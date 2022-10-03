import { gql } from "@apollo/client";
import { TrashIcon } from "@heroicons/react/24/outline";
import Menu from "core/components/Menu";
import { useTranslation } from "next-i18next";
import { CollectionActionsMenu_CollectionFragment } from "./CollectionActionsMenu.generated";
import CollectionDeleteTrigger from "./CollectionDeleteTrigger";
type CollectionActionsMenuProps = {
  collection: CollectionActionsMenu_CollectionFragment;
};

const CollectionActionsMenu = ({ collection }: CollectionActionsMenuProps) => {
  const { t } = useTranslation();

  return (
    <Menu label={t("Actions")}>
      {collection.authorizedActions.canDelete && (
        <CollectionDeleteTrigger collection={collection}>
          {({ onClick }) => (
            <Menu.Item
              activeClassName="bg-red-500 text-white"
              onClick={onClick}
            >
              <TrashIcon className="mr-2 h-4 w-4" />
              {t("Delete")}
            </Menu.Item>
          )}
        </CollectionDeleteTrigger>
      )}
    </Menu>
  );
};

CollectionActionsMenu.fragments = {
  collection: gql`
    fragment CollectionActionsMenu_collection on Collection {
      id
      authorizedActions {
        canDelete
        canUpdate
      }
      ...CollectionDeleteTrigger_collection
    }
    ${CollectionDeleteTrigger.fragments.collection}
  `,
};

export default CollectionActionsMenu;
