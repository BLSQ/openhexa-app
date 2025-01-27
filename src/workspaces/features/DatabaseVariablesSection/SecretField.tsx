import Clipboard from "core/components/Clipboard";
import {
  EyeIcon,
  EyeSlashIcon,
  LockClosedIcon,
} from "@heroicons/react/24/outline";
import { useCallback, useState } from "react";

const SecretField = (field: { value: string | number }) => {
  const { value } = field;
  const [showSecret, setShowSecret] = useState<boolean>(false);
  const toggleSecret = useCallback(
    () => setShowSecret((showSecet) => !showSecet),
    [],
  );

  if (showSecret) {
    return (
      <div className="flex w-3/4 items-start justify-start gap-x-2 ">
        <span className="truncate">{value}</span>
        <button
          onClick={toggleSecret}
          type="button"
          className="flex cursor-pointer gap-1 hover:text-blue-500 focus:outline-hidden"
        >
          <EyeSlashIcon className="h-4 w-4" />
        </button>
        <Clipboard iconClassName="h-4 w-4" value={value.toString()} />
      </div>
    );
  }
  return (
    <div className="flex items-start gap-x-2">
      <LockClosedIcon className="h-3 w-3" />
      <span>*********</span>
      <button
        onClick={toggleSecret}
        type="button"
        className="flex cursor-pointer gap-1 hover:text-blue-500 focus:outline-hidden"
      >
        <EyeIcon className="h-4 w-4" />
      </button>
      <Clipboard iconClassName="h-4 w-4" value={value.toString()} />
    </div>
  );
};

export default SecretField;
