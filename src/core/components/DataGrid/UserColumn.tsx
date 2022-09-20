import { gql } from "@apollo/client";
import User from "core/features/User";
import { BaseColumnProps } from "./BaseColumn";
import { useCellContext } from "./helpers";
import { UserColumn_UserFragment } from "./UserColumn.generated";

type UserColumnProps = BaseColumnProps;

const UserColumn = (props: UserColumnProps) => {
  const cell = useCellContext<UserColumn_UserFragment>();

  return cell.value ? <User user={cell.value} /> : <span>-</span>;
};

UserColumn.fragments = {
  user: gql`
    fragment UserColumn_user on User {
      ...User_user
    }
    ${User.fragments.user}
  `,
};

export default UserColumn;
