import { gql } from "@apollo/client";
import Avatar, { AvatarProps } from "core/components/Avatar";

import { useMemo } from "react";
import { UserAvatar_UserFragment } from "./UserAvatar.generated";

type Props = {
  user: UserAvatar_UserFragment;
} & AvatarProps;

const UserAvatar = ({ user, ...delegated }: Props) => {
  const name = useMemo(
    () => [user.firstName, user.lastName].filter(Boolean).join(" "),
    [user]
  );
  return (
    <Avatar
      {...delegated}
      title={name}
      color={user.avatar.color}
      initials={user.avatar.initials}
    />
  );
};

UserAvatar.fragments = {
  user: gql`
    fragment UserAvatar_user on User {
      firstName
      lastName
      avatar {
        initials
        color
      }
    }
  `,
};

export default UserAvatar;
