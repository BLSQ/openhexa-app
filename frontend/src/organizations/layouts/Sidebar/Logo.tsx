import Image from "next/image";
import logoWithTextWhite from "public/images/logo_with_text_white.svg";
import logo from "public/images/logo.svg";
import React from "react";

type LogoProps = {
  isSidebarOpen: boolean;
};

const Logo = ({ isSidebarOpen }: LogoProps) => {
  return (
    <div className="mb-5 flex shrink-0 flex-col items-center px-4">
      <a href="/frontend/public" className="flex h-8 items-center">
        <Image
          className="h-full w-auto"
          src={isSidebarOpen ? logoWithTextWhite : logo}
          alt="OpenHEXA logo"
          width={140}
          height={32}
        />
      </a>
    </div>
  );
};

export default Logo;
