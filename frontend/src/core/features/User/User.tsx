import { gql } from "@apollo/client";
import UserAvatar from "identity/features/UserAvatar";
import { User_UserFragment } from "./User.generated";

type UserProps = {
  user: User_UserFragment;
  textColor?: string;
  subtext?: boolean;
};

const User = ({ user, subtext, textColor = "text-inherit" }: UserProps) => {
  return (
    <div className="flex items-center gap-2">
      <UserAvatar user={user} size="sm" />
      <div className="truncate">
        <div className={textColor}>{user.displayName}</div>
        {subtext && <div className="text-xs text-gray-400">{user.email}</div>}
      </div>
    </div>
  );
};

User.fragments = {
  user: gql`
    fragment User_user on User {
      id
      email
      displayName
      ...UserAvatar_user
    }
    ${UserAvatar.fragments.user}
  `,
};

export default User;
