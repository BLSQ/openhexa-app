import { ensureArray } from "core/helpers/array";
import { TabularColumn } from "datasets/hooks/useTabularFileMetadata";
import { MetadataAttribute } from "graphql/types";
import { useMemo } from "react";

const RenderColumnAttribute = ({
  column,
  attributeKeys,
  children,
}: {
  column: TabularColumn;
  attributeKeys: string | string[];
  children: (
    ...attributes: (TabularColumn["attributes"][0] | undefined)[]
  ) => React.ReactNode;
}) => {
  const attributes = useMemo(() => {
    return ensureArray(attributeKeys).map((attributeKey) =>
      column.attributes.find(
        (attr) => attr.key === `${column.key}.${attributeKey}`,
      ),
    );
  }, [column, attributeKeys]);

  return <>{children.apply(null, attributes)}</>;
};

export default RenderColumnAttribute;
