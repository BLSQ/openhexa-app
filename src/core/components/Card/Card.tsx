import clsx from "clsx";
import { ReactNode } from "react";
import Link from "../Link";
import CardActions from "./CardActions";
import CardContent from "./CardContent";
import CardHeader from "./CardHeader";

type CardProps = {
  children: ReactNode | ReactNode[];
  title?: ReactNode;
  subtitle?: ReactNode;
  href?: React.ComponentProps<typeof Link>["href"];
  className?: string;
};

const Card = (props: CardProps) => {
  const { children, href, title, subtitle, className } = props;
  const element = (
    <article
      className={clsx(
        "flex flex-col gap-2 overflow-hidden rounded-md bg-white px-4 py-3 shadow-xs lg:px-5 lg:py-4",
        href && "h-full hover:shadow-md",
        className,
      )}
    >
      {title && <CardHeader title={title} subtitle={subtitle} />}
      {children}
    </article>
  );

  if (href) {
    return (
      <Link href={href} noStyle>
        {element}
      </Link>
    );
  }
  return element;
};

Card.Content = CardContent;
Card.Actions = CardActions;
Card.Header = CardHeader;

export default Card;
