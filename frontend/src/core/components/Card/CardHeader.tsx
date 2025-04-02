import { ReactNode } from "react";
import Link from "../Link";
import Title from "../Title";

type CardHeaderProps = {
  title: ReactNode;
  href?: React.ComponentProps<typeof Link>["href"];
  className?: string;
  subtitle?: ReactNode;
};

const CardHeader = (props: CardHeaderProps) => {
  const { title, subtitle, className, href } = props;
  const element = (
    <div className={className}>
      <Title level={4} className="mb-0 line-clamp-3 leading-5">
        {title}
      </Title>
      {subtitle && <div className=" text-sm text-gray-500">{subtitle}</div>}
    </div>
  );
  if (href) {
    return (
      <Link customStyle="hover:text-gray-700" href={href}>
        {element}
      </Link>
    );
  }

  return element;
};

export default CardHeader;
