import { PlusIcon } from "@heroicons/react/24/outline";
import clsx from "clsx";
import Spinner from "core/components/Spinner";
import { useTranslation } from "next-i18next";
import { AssistantPageQuery } from "assistant/graphql/queries.generated";

type Conversation = NonNullable<
  AssistantPageQuery["workspace"]
>["assistantConversations"][0];

type ConversationListProps = {
  conversations: Conversation[];
  selectedId: string | null;
  onSelect: (id: string) => void;
  onNew: () => void;
  creating: boolean;
};

const ConversationList = ({
  conversations,
  selectedId,
  onSelect,
  onNew,
  creating,
}: ConversationListProps) => {
  const { t } = useTranslation();

  return (
    <div className="flex flex-col w-64 shrink-0 border-r border-gray-200 bg-white h-full overflow-hidden">
      <div className="p-3 border-b border-gray-200">
        <button
          onClick={onNew}
          disabled={creating}
          className="flex items-center gap-2 w-full rounded-md px-3 py-2 text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          {creating ? (
            <Spinner size="xs" className="text-white" />
          ) : (
            <PlusIcon className="h-4 w-4" />
          )}
          {t("New conversation")}
        </button>
      </div>
      <div className="flex-1 overflow-y-auto py-1">
        {conversations.map((conv) => (
          <button
            key={conv.id}
            onClick={() => onSelect(conv.id)}
            className={clsx(
              "w-full text-left px-3 py-2 text-sm truncate hover:bg-gray-100 transition-colors",
              conv.id === selectedId
                ? "bg-gray-100 font-medium text-gray-900"
                : "text-gray-700",
            )}
            title={conv.name ?? t("Untitled conversation")}
          >
            {conv.name ?? t("Untitled conversation")}
          </button>
        ))}
      </div>
    </div>
  );
};

export default ConversationList;
