import { PlusIcon } from "@heroicons/react/24/outline";
import clsx from "clsx";
import Button from "core/components/Button";
import Spinner from "core/components/Spinner";

type Conversation = {
  id: string;
  createdAt: string;
  model: string;
};

type Props = {
  conversations: Conversation[];
  selectedId: string | null;
  onSelect: (id: string) => void;
  onNew: () => void;
  creating: boolean;
};

function formatDate(iso: string) {
  return new Date(iso).toLocaleString(undefined, {
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

export default function ConversationList({
  conversations,
  selectedId,
  onSelect,
  onNew,
  creating,
}: Props) {
  return (
    <div className="flex w-60 shrink-0 flex-col border-r border-gray-200 bg-white">
      <div className="border-b border-gray-200 p-3">
        <Button
          className="w-full"
          onClick={onNew}
          disabled={creating}
          leadingIcon={
            creating ? <Spinner size="xs" /> : <PlusIcon className="h-4 w-4" />
          }
        >
          New conversation
        </Button>
      </div>

      <div className="flex-1 overflow-y-auto">
        {conversations.length === 0 && !creating && (
          <p className="p-4 text-center text-sm text-gray-400">
            No conversations yet
          </p>
        )}
        {conversations.map((conv) => (
          <button
            key={conv.id}
            onClick={() => onSelect(conv.id)}
            className={clsx(
              "w-full px-4 py-3 text-left text-sm transition-colors hover:bg-gray-50",
              selectedId === conv.id
                ? "bg-blue-50 text-blue-700 font-medium"
                : "text-gray-700",
            )}
          >
            {formatDate(conv.createdAt)}
          </button>
        ))}
      </div>
    </div>
  );
}
