import React from "react";
import clsx from "clsx";
import Button from "core/components/Button";
import { ListBulletIcon, Squares2X2Icon } from "@heroicons/react/24/outline";

type ViewToggleButtonProps = {
  view: "grid" | "card";
  setView: (view: "grid" | "card") => void;
};

const ViewToggleButton = ({ view, setView }: ViewToggleButtonProps) => {
  return (
    <div className={"bg-gray-50 rounded"}>
      <Button
        data-testid={"card-view"}
        variant={"custom"}
        onClick={() => setView("card")}
        rounded={false}
        focusRing={false}
        className={clsx(
          view === "card" ? "bg-white text-blue-400" : "text-gray-800",
          "rounded-bl rounded-tl",
          "border-transparent hover:bg-white",
        )}
      >
        <Squares2X2Icon className="h-4 w-4" />
      </Button>
      <Button
        data-testid={"grid-view"}
        variant={"custom"}
        onClick={() => setView("grid")}
        rounded={false}
        focusRing={false}
        className={clsx(
          view === "grid" ? "bg-white text-blue-400" : "text-gray-800",
          "rounded-br rounded-tr",
          "border-transparent hover:bg-white",
        )}
      >
        <ListBulletIcon className="h-4 w-4" />
      </Button>
    </div>
  );
};

export default ViewToggleButton;
