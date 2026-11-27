import { ReactNode } from "react";
import OidcProviderIcon from "identity/features/OidcProviderIcon";

type OidcProviderButtonProps = {
  providerId: string;
  href: string;
  children: ReactNode;
};

const OidcProviderButton = ({
  providerId,
  href,
  children,
}: OidcProviderButtonProps) => (
  <a
    href={href}
    className="flex w-full items-center justify-center gap-3 rounded-md border border-gray-300 bg-white px-4 py-2.5 text-sm font-medium text-gray-800 shadow-xs transition-colors hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
  >
    <OidcProviderIcon providerId={providerId} />
    <span>{children}</span>
  </a>
);

export default OidcProviderButton;
