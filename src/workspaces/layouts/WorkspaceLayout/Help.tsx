import { QuestionMarkCircleIcon } from "@heroicons/react/24/outline";
import clsx from "clsx";
import Link from "core/components/Link";
import Popover from "core/components/Popover/Popover";
import Title from "core/components/Title";
import { ReactElement } from "react";
import { useTranslation } from "next-i18next";

type HelpProps = Pick<React.ComponentProps<typeof Popover>, "placement"> & {
  links?: { label: string; href: string }[];
  className?: string;
  children?: ReactElement;
};

const Help = (props: HelpProps) => {
  const { placement, links, className } = props;
  const { t } = useTranslation();

  const children = props.children ?? (
    <QuestionMarkCircleIcon className="m-1.5 h-9 w-9 rounded-full p-1 hover:bg-gray-100" />
  );

  if (links) {
    return (
      <Popover
        buttonClassName={className}
        trigger={children}
        className="w-96"
        placement={placement}
      >
        <Title level={5}>{t("Suggested help topics")}</Title>
        <ul className="list-inside list-disc">
          {links.map((link) => (
            <li key={link.href} className="py-1">
              <Link target="_blank" href={link.href}>
                {link.label}
              </Link>
            </li>
          ))}
        </ul>
        <div className="-mx-4 -mb-4 mt-2 border-t border-gray-300 bg-gray-100 px-4 py-4">
          <Link
            href="https://github.com/BLSQ/openhexa/wiki"
            customStyle="text-gray-900 hover:text-gray-500"
            target="_blank"
          >
            {t("Visit the OpenHEXA documentation homepage")}
          </Link>
        </div>
      </Popover>
    );
  } else {
    return (
      <Link
        href="https://github.com/BLSQ/openhexa/wiki"
        noStyle
        target="_blank"
      >
        {children}
      </Link>
    );
  }
};

export default Help;
