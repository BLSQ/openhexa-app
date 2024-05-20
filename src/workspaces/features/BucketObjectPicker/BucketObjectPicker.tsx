import { gql, useLazyQuery } from "@apollo/client";
import {
  ChevronRightIcon,
  ChevronUpDownIcon,
  XMarkIcon,
} from "@heroicons/react/24/outline";
import Button from "core/components/Button";
import Popover from "core/components/Popover";
import Input from "core/components/forms/Input";
import { BucketObject, BucketObjectType } from "graphql/types";
import { useTranslation } from "next-i18next";
import { useEffect, useMemo, useState } from "react";
import {
  BucketObjectPicker_WorkspaceFragment,
  ObjectPickerQuery,
  ObjectPickerQueryVariables,
} from "./BucketObjectPicker.generated";
import { HomeIcon } from "@heroicons/react/20/solid";
import Spinner from "core/components/Spinner";
import clsx from "clsx";

type InnerBucketObjectPickerProps = {
  workspaceSlug: string;
  onChange: (value: BucketObject) => void;
  value: string | null;
  exclude?: (item: BucketObject) => boolean;
  close: () => void;
};
type BucketObjectPickerProps = {
  workspace: BucketObjectPicker_WorkspaceFragment;
  placeholder?: string;
  value: string | null;
  onChange: (value: BucketObject | null) => void;
  exclude?: InnerBucketObjectPickerProps["exclude"];
};

const InnerBucketObjectPicker = (props: InnerBucketObjectPickerProps) => {
  const { onChange, value, exclude, close, workspaceSlug } = props;
  const [prefix, _setPrefix] = useState<string | null>(null);
  const { t } = useTranslation();
  const [perPage, setPerPage] = useState(20);
  const onItemClick = (item: BucketObject) => {
    if (item.type === BucketObjectType.Directory) {
      setPrefix(item.key);
    } else {
      onChange(item);
      close();
    }
  };
  const [fetch, { data, previousData, loading }] = useLazyQuery<
    ObjectPickerQuery,
    ObjectPickerQueryVariables
  >(gql`
    query ObjectPicker(
      $slug: String!
      $page: Int
      $perPage: Int
      $prefix: String
    ) {
      workspace(slug: $slug) {
        slug
        bucket {
          objects(page: $page, perPage: $perPage, prefix: $prefix) {
            items {
              name
              key
              path
              type
              updatedAt
            }
            pageNumber
            hasNextPage
          }
        }
      }
    }
  `);

  useEffect(() => {
    fetch({
      variables: {
        slug: workspaceSlug,
        prefix,
        page: 1,
        perPage,
      },
    });
  }, [prefix, fetch, workspaceSlug, perPage]);

  const loadMore = async () => {
    setPerPage((perPage) => perPage + 20);
  };

  const setPrefix = (prefix: string | null) => {
    setPerPage(20);
    _setPrefix(prefix);
  };

  const prefixes: { label: string; value: string }[] = useMemo(() => {
    const arr = [] as any[];
    let last = "";
    prefix
      ?.split("/")
      .filter(Boolean)
      .forEach((part, index) => {
        last = last ? last + "/" + part : part;
        arr.push({
          label: part,
          value: last + "/",
        });
      });
    return arr;
  }, [prefix]);

  const bucket =
    data?.workspace?.bucket ?? previousData?.workspace?.bucket ?? null;
  return (
    <div className="flex-col flex overflow-y-auto flex-1 pt-4 divide-y divide-gray-200">
      {prefixes.length > 0 && (
        <div className="px-4 pb-2 flex gap-0.5 text-sm items-center text-gray-400">
          <button
            className="underline hover:text-gray-600"
            onClick={() => setPrefix(null)}
          >
            <HomeIcon className="w-3 h-3" />
          </button>
          {prefixes.length > 2 && (
            <>
              <ChevronRightIcon className="h-3 w-3" />
              ...
            </>
          )}
          {prefixes.slice(-2).map((part, index, arr) => (
            <>
              <ChevronRightIcon className="h-3 w-3" />
              <button
                key={index}
                className="underline hover:text-gray-600"
                onClick={() => setPrefix(part.value)}
              >
                {part.label}
              </button>
            </>
          ))}
        </div>
      )}
      <ul className="text-sm text-gray-600 pb-4">
        {bucket?.objects.items.map((item, index) => (
          <li key={index}>
            <button
              disabled={exclude && exclude(item)}
              className={clsx(
                "w-full flex items-center justify-between py-2 hover:bg-gray-100 px-4 disabled:opacity-75 disabled:italic",
                item.key === value ? "bg-gray-100 font-semibold" : "",
              )}
              onClick={() => onItemClick(item)}
            >
              <div className="flex flex-col">
                {item.name}
                {item.type === BucketObjectType.Directory && "/"}
              </div>
              {item.type === BucketObjectType.Directory ? (
                <ChevronRightIcon className="h-4 w-4" />
              ) : null}
            </button>
          </li>
        ))}
        {!previousData && loading && (
          <Spinner size="sm" className=" mt-2  mx-auto" />
        )}
        {!loading && !data?.workspace?.bucket?.objects.items.length && (
          <div className="italic text-center mt-3">{t("Empty directory")}</div>
        )}
        {bucket?.objects.hasNextPage && (
          <div className="text-center mt-2">
            <Button
              variant="outlined"
              size="sm"
              className=""
              onClick={loadMore}
            >
              {t("Show more")}
            </Button>
          </div>
        )}
      </ul>
    </div>
  );
};

const BucketObjectPicker = (props: BucketObjectPickerProps) => {
  const { t } = useTranslation();
  const {
    workspace,
    value,
    placeholder = t("Select an object"),
    exclude,
    onChange,
  } = props;

  return (
    <Popover
      withPortal
      placement="bottom-start"
      buttonClassName="w-full"
      className="min-w-[480px] max-w-[550px] gap-4 px-0 py-0 max-h-72 flex flex-col"
      trigger={({ open }) => (
        <Input
          fullWidth
          placeholder={value ?? placeholder}
          readOnly
          className={clsx(open && "ring-blue-500 border-blue-500 ring-1")}
          trailingIcon={
            value ? (
              <XMarkIcon
                onClick={() => onChange(null)}
                className="text-gray-400 hover:text-gray-600 h-4 w-4"
              />
            ) : (
              <ChevronUpDownIcon className="text-gray-400 hover:text-gray-600 h-4 w-4" />
            )
          }
        />
      )}
    >
      {({ close }) => (
        <InnerBucketObjectPicker
          workspaceSlug={workspace.slug}
          exclude={exclude}
          value={value}
          onChange={onChange}
          close={close}
        />
      )}
    </Popover>
  );
};

BucketObjectPicker.fragments = {
  workspace: gql`
    fragment BucketObjectPicker_workspace on Workspace {
      slug
    }
  `,
};

export default BucketObjectPicker;
