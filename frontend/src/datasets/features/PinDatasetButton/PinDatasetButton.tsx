import { StarIcon as OutlineStarIcon } from "@heroicons/react/24/outline";
import { StarIcon as SolidStarIcon } from "@heroicons/react/24/solid";
import { gql, useMutation } from "@apollo/client";
import useCacheKey from "core/hooks/useCacheKey";
import { PinDatasetButton_LinkFragment } from "datasets/features/PinDatasetButton/PinDatasetButton.generated";

type PinDatasetButtonProps = {
  link: PinDatasetButton_LinkFragment;
};

const PinDatasetButton = ({ link }: PinDatasetButtonProps) => {
  const [pinDataset] = useMutation(gql`
    mutation PinDatasetButton($input: PinDatasetInput!) {
      pinDataset(input: $input) {
        link {
          id
          isPinned
        }
        success
        errors
      }
    }
  `);
  const clearCache = useCacheKey(["datasets"]);
  const onClick = async () => {
    await pinDataset({
      variables: {
        input: { linkId: link.id, pinned: !link.isPinned },
      },
    });
    clearCache();
  };
  const iconClassName = "h-5 w-5 group-hover/pin:scale-125 text-amber-400";

  const icon = link.isPinned ? (
    <SolidStarIcon className={iconClassName} />
  ) : (
    <OutlineStarIcon strokeWidth={2} className={iconClassName} />
  );

  if (!link.permissions.pin) {
    return icon;
  } else {
    return (
      <button
        className={
          "cursor-pointer w-8 h-8 group/pin hover:p-1 transition-all flex items-center justify-center rounded-full"
        }
        onClick={onClick}
      >
        {icon}
      </button>
    );
  }
};

PinDatasetButton.fragments = {
  link: gql`
    fragment PinDatasetButton_link on DatasetLink {
      id
      isPinned
      permissions {
        pin
      }
    }
  `,
};

export default PinDatasetButton;
