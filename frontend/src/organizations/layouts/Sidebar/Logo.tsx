import React from "react";

type LogoProps = {
  isSidebarOpen: boolean;
};

const Logo = ({ isSidebarOpen }: LogoProps) => {
  return (
    <div className="mb-5 flex shrink-0 flex-col items-center px-4">
      <a href="/frontend/public" className="flex h-8 items-center">
        <img
          className="h-full"
          src={
            isSidebarOpen
              ? "/images/logo_with_text_white.svg"
              : "/images/logo.svg"
          }
          alt="OpenHEXA logo"
        />
      </a>
    </div>
  );
};

export default Logo;
