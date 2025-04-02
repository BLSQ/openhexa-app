import { gql } from "@apollo/client";
import Avatar, { AvatarProps } from "core/components/Avatar";

import { UserAvatar_UserFragment } from "./UserAvatar.generated";

type Props = {
  user: UserAvatar_UserFragment;
} & Omit<AvatarProps, "title" | "color" | "initials">;

const UserAvatar = ({ user, ...delegated }: Props) => {
  return (
    <Avatar
      {...delegated}
      title={user.displayName}
      color={user.avatar.color}
      initials={user.avatar.initials}
    />
  );
};

UserAvatar.fragments = {
  user: gql`
    fragment UserAvatar_user on User {
      displayName
      avatar {
        initials
        color
      }
    }
  `,
};

export default UserAvatar;
