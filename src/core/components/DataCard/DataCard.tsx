import clsx from "clsx";
import { ItemProvider } from "core/hooks/useItemContext";
import { ReactNode } from "react";
import Block, { BlockSection } from "../Block";
import FormSection from "./FormSection";
import Heading from "./Heading";
import PropertyDisplay from "./PropertyDisplay";

export type DataCardProps = {
  item: any;
  children: ReactNode;
  className?: string;
};

const DataCard = (props: DataCardProps) => {
  const { children, className, item } = props;
  return (
    <ItemProvider item={item}>
      <Block className={clsx("divide-y divide-gray-200", className)}>
        {children}
      </Block>
    </ItemProvider>
  );
};

DataCard.Section = BlockSection;
DataCard.FormSection = FormSection;
DataCard.Property = PropertyDisplay;
DataCard.Heading = Heading;

export default DataCard;
