import { gql } from "@apollo/client";
import { StarIcon } from "@heroicons/react/24/outline";
import clsx from "clsx";
import { MouseEventHandler } from "react";
import { PipelineRunFavoriteIcon_RunFragment } from "./PipelineRunFavoriteIcon.generated";

type PipelineRunFavoriteIconProps = {
  sizeClassName?: string;
  className?: string;
  run: PipelineRunFavoriteIcon_RunFragment;
  animate?: boolean;
};

const PipelineRunFavoriteIcon = (props: PipelineRunFavoriteIconProps) => {
  const { sizeClassName = "h-6 w-6", run, className, animate } = props;

  return (
    <StarIcon
      data-testid="favorite-icon"
      className={clsx(
        className,
        sizeClassName,
        "transition-colors",
        run.isFavorite
          ? "fill-yellow-300 stroke-yellow-400 "
          : "stroke-gray-300 hover:fill-gray-200",
        animate && run.isFavorite && "hover:fill-transparent",
        animate &&
          !run.isFavorite &&
          "hover:fill-yellow-300 hover:stroke-yellow-400",
      )}
    />
  );
};

PipelineRunFavoriteIcon.fragments = {
  run: gql`
    fragment PipelineRunFavoriteIcon_run on DAGRun {
      isFavorite
    }
  `,
};

export default PipelineRunFavoriteIcon;
