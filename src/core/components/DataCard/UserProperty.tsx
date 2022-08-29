import User from "core/features/User";
import { User_UserFragment } from "core/features/User/User.generated";
import { useDataCardProperty } from "./context";
import DataCard from "./DataCard";
import { PropertyDefinition } from "./types";

type UserPropertyProps = { multiple?: boolean } & PropertyDefinition;

const UserProperty = (props: UserPropertyProps) => {
  const { multiple, ...delegated } = props;
  const { property, section } =
    useDataCardProperty<User_UserFragment>(delegated);

  return (
    <DataCard.Property property={property}>
      {property.displayValue ? <User user={property.displayValue} /> : "-"}
    </DataCard.Property>
  );
};

export default UserProperty;
