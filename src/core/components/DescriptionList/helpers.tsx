import { useContext, createContext } from "react";

export enum DescriptionListDisplayMode {
  LABEL_ABOVE = "above",
  LABEL_LEFT = "left",
}

export type DescriptionListContext = {
  displayMode: DescriptionListDisplayMode;
  compact: boolean;
};

export const ctx = createContext<DescriptionListContext | null>(null);

export const useDescriptionList = () => {
  const config = useContext(ctx);

  if (!config) {
    throw new Error(
      "useDescriptionList must be under a DescriptionList component",
    );
  }
  return config;
};
