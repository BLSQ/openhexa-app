import { gql } from "@apollo/client";
import clsx from "clsx";
import Badge from "core/components/Badge";
import { Tag_TagFragment } from "./Tag.generated";

type TagProps = {
  tag: Tag_TagFragment;
  className?: string;
  onClick?: () => void;
  bgColor?: string;
  borderColor?: string;
};

const Tag = (props: TagProps) => {
  const {
    onClick,
    className,
    tag,
    bgColor = "bg-purple-100",
    borderColor = "ring-purple-400/20",
  } = props;
  return (
    <Badge
      title={tag.name}
      className={clsx(
        onClick && "cursor-pointer",
        className,
        "hover:bg-opacity-70",
        borderColor,
        bgColor,
      )}
      onClick={onClick}
    >
      {tag.name}
    </Badge>
  );
};

Tag.fragments = {
  tag: gql`
    fragment Tag_tag on Tag {
      id
      name
    }
  `,
};

export default Tag;
