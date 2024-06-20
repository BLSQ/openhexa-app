import get from "lodash/get";
import { createContext, ReactNode, useContext } from "react";

export type ValueAccessorFn = (item: any) => any;
export type ValueAccessor = string | ValueAccessorFn;

export interface ItemInstance {
  [key: string]: any;
}

const ItemContext = createContext<{ item: ItemInstance } | null>(null);

export function useItemContext<T extends ItemInstance = {}>() {
  const value = useContext(ItemContext);
  if (!value) {
    throw new Error("useItemContext must be called inside a ItemProvider");
  }

  return { item: value.item as T };
}

type ItemProviderProps<T extends ItemInstance = {}> = {
  item: T;
  children: ReactNode;
};

export const getValue = (item: any, accessor?: ValueAccessor) => {
  if (!accessor) {
    return item;
  } else if (typeof accessor === "string") {
    try {
      return get(item, accessor);
    } catch (err) {
      return null;
    }
  } else {
    return accessor(item);
  }
};

export function ItemProvider<T extends ItemInstance>(
  props: ItemProviderProps<T>,
) {
  const { item, children } = props;
  return (
    <ItemContext.Provider value={{ item }}>{children}</ItemContext.Provider>
  );
}
