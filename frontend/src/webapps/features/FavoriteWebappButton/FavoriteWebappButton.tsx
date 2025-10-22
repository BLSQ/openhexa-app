import { StarIcon as OutlineStarIcon } from "@heroicons/react/24/outline";
import { StarIcon as SolidStarIcon } from "@heroicons/react/24/solid";
import { gql } from "@apollo/client";
import useCacheKey from "core/hooks/useCacheKey";
import { toast } from "react-toastify";
import { useTranslation } from "next-i18next";
import { FavoriteWebappButton_WebappFragment } from "./FavoriteWebappButton.generated";
import { useMutation } from "@apollo/client/react";
import { graphql } from "graphql/gql";

const RemoveFromFavoritesDoc = graphql(`
mutation RemoveFromFavorites($input: RemoveFromFavoritesInput!) {
  removeFromFavorites(input: $input) {
    success
    errors
  }
}
`);

const AddToFavoritesDoc = graphql(`
mutation AddToFavorites($input: AddToFavoritesInput!) {
  addToFavorites(input: $input) {
    success
    errors
  }
}
`);

type FavoriteWebappButtonProps = {
  webapp: FavoriteWebappButton_WebappFragment;
};

const FavoriteWebappButton = ({
  webapp: { id: webappId, isFavorite },
}: FavoriteWebappButtonProps) => {
  const { t } = useTranslation();
  const [addToFavorites] = useMutation(AddToFavoritesDoc);
  const [removeFromFavorites] = useMutation(RemoveFromFavoritesDoc);

  const clearCache = useCacheKey(["webapps"]);

  const handleFavoriteClick = async () => {
    try {
      if (isFavorite) {
        await removeFromFavorites({ variables: { input: { webappId } } });
        toast.success(t("Removed from favorites"));
      } else {
        await addToFavorites({ variables: { input: { webappId } } });
        toast.success(t("Added to favorites"));
      }
      clearCache();
    } catch (error) {
      toast.error(t("Error updating favorites"));
    }
  };

  const iconClassName = "h-5 w-5 group-hover/pin:scale-125 text-amber-400";

  const icon = isFavorite ? (
    <SolidStarIcon className={iconClassName} />
  ) : (
    <OutlineStarIcon strokeWidth={2} className={iconClassName} />
  );

  return (
    <button
      className={
        "cursor-pointer w-8 h-8 group/pin hover:p-1 transition-all flex items-center justify-center rounded-full"
      }
      onClick={handleFavoriteClick}
      data-testid={`favorite-button-${webappId}`}
    >
      {icon}
    </button>
  );
};

FavoriteWebappButton.fragments = {
  webapp: gql`
    fragment FavoriteWebappButton_webapp on Webapp {
      id
      isFavorite
    }
  `,
};

export default FavoriteWebappButton;
