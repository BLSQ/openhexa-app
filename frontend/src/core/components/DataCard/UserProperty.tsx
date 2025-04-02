import { gql } from "@apollo/client";
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

UserProperty.fragments = {
  user: gql`
    fragment UserProperty_user on User {
      ...User_user
    }
    ${User.fragments.user}
  `,
};

export default UserProperty;
