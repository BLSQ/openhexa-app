import { gql } from "@apollo/client";
import { CollectionIcon } from "@heroicons/react/outline";
import clsx from "clsx";
import Link from "core/components/Link";
import { useTranslation } from "next-i18next";
import { ReactElement } from "react";
import { SearchResult_ResultFragment } from "./SearchResult.generated";

export type SearchResultProps = {
  result: SearchResult_ResultFragment;
  renderActions?: (element: SearchResult_ResultFragment) => ReactElement;
  className?: string;
};

const SearchResult = (props: SearchResultProps) => {
  const { result, renderActions, className } = props;
  const { t } = useTranslation();

  return (
    <div
      className={clsx(
        "flex items-center gap-3 py-2.5 px-4 text-sm hover:bg-gray-50",
        className
      )}
      key={result.object.id}
    >
      {result.object.__typename === "CatalogEntry" && (
        <>
          {result.object.symbol && (
            <div className="w-5">
              <img
                loading="eager"
                className="h-5 w-5 flex-shrink-0"
                src={result.object.symbol}
                alt={result.object.name}
              />
            </div>
          )}

          <div className="flex-1 truncate">
            <Link className="font-medium" href={result.object.objectUrl}>
              {result.object.name}
            </Link>
            <span className="ml-2 font-sans text-xs text-gray-300">
              #{Math.round(result.rank * 100) / 100}
            </span>
            <div className="mt-1 text-xs text-gray-500">
              {[result.object.type.name, result.object.datasource?.name]
                .filter(Boolean)
                .join(" / ")}
            </div>
          </div>
          {renderActions && renderActions(result)}
        </>
      )}
      {result.object.__typename === "Collection" && (
        <>
          <div className="w-5">
            <CollectionIcon className="h-5 w-5 flex-shrink-0" />
          </div>

          <div className="flex-1 truncate">
            <Link
              className="font-medium"
              href={{
                pathname: "/collections/[collectionId]",
                query: { collectionId: result.object.id },
              }}
            >
              {result.object.name}
            </Link>
            <span className="ml-2 font-sans text-xs text-gray-300">
              #{Math.round(result.rank * 100) / 100}
            </span>
            <div className="mt-1 text-xs text-gray-500">{t("Collection")}</div>
          </div>
        </>
      )}
    </div>
  );
};

SearchResult.fragments = {
  result: gql`
    fragment SearchResult_result on SearchResult {
      rank
      object {
        __typename
        ... on Collection {
          id
          name
        }
        ... on CatalogEntry {
          id
          name
          datasource {
            id
            name
          }
          type {
            model
            app
            name
          }
          objectId
          objectUrl
          symbol
        }
      }
    }
  `,
};

export default SearchResult;
