import { ReactNode } from "react";
import {
  Dialog,
  DialogBackdrop,
  DialogPanel,
  DialogTitle,
  TransitionChild,
} from "@headlessui/react";
import { XMarkIcon } from "@heroicons/react/24/outline";
import clsx from "clsx";

type DrawerProps = {
  open: boolean;
  width?: string;
  displayClose?: boolean;
  setOpen: (open: boolean) => void;
  children: React.ReactNode;
  backdropBlur?: boolean;
  backdrop?: boolean;
  autoFocus?: boolean;
};

export default function Drawer({
  open,
  setOpen,
  children,
  displayClose = true,
  backdropBlur = true,
  backdrop = true,
  width = "max-w-md 2xl:max-w-xl",
  autoFocus = true,
}: DrawerProps) {
  return (
    <Dialog
      autoFocus={autoFocus}
      open={open}
      onClose={setOpen}
      className="relative z-50"
      data-testid="drawer"
    >
      {backdrop && (
        <DialogBackdrop
          transition
          data-testid="drawer-backdrop"
          className={clsx(
            "fixed inset-0 bg-gray-500/75 transition-opacity duration-500 ease-in-out data-closed:opacity-0",
            backdropBlur && "backdrop-blur-xs data-closed:backdrop-blur-none",
          )}
        />
      )}

      <div className="fixed inset-0 overflow-hidden">
        <div className="absolute inset-0 overflow-hidden">
          <div className="pointer-events-none fixed inset-y-0 right-0 flex max-w-full pl-10">
            <DialogPanel
              transition
              className={clsx(
                "pointer-events-auto overflow-x-hidden relative w-screen transform transition duration-300 ease-in-out data-closed:translate-x-full sm:duration-500",
                width,
              )}
            >
              <TransitionChild>
                <div className="absolute left-0 top-0 -ml-8 flex pr-2 pt-4 duration-500 ease-in-out data-closed:opacity-0 sm:-ml-10 sm:pr-4">
                  {displayClose && (
                    <button
                      type="button"
                      onClick={() => setOpen(false)}
                      className="relative rounded-md text-gray-300 hover:text-white focus:outline-hidden focus:ring-2 focus:ring-white"
                    >
                      <span className="absolute -inset-2.5" />
                      <span className="sr-only">Close panel</span>
                      <XMarkIcon aria-hidden="true" className="size-6" />
                    </button>
                  )}
                </div>
              </TransitionChild>
              <div className="flex h-full flex-col bg-white shadow-xl ">
                {children}
              </div>
            </DialogPanel>
          </div>
        </div>
      </div>
    </Dialog>
  );
}

Drawer.Title = function DrawerTitle({
  children,
  className,
}: {
  children: ReactNode;
  className?: string;
}) {
  return (
    <div className={"bg-gray-50 px-4 py-6 sm:px-6"}>
      <DialogTitle
        className={clsx("text-lg font-semibold text-gray-900", className)}
      >
        {children}
      </DialogTitle>
    </div>
  );
};

Drawer.Content = function DrawerContent({
  children,
  className,
}: {
  children: ReactNode;
  className?: string;
}) {
  return (
    <div
      className={clsx("flex-1 overflow-y-auto px-4 tall:px-6 py-4", className)}
    >
      {children}
    </div>
  );
};

Drawer.Footer = function DrawerFooter({
  children,
  className,
}: {
  children: ReactNode;
  className?: string;
}) {
  return (
    <div
      className={clsx(
        " px-4 py-6 sm:px-6 flex justify-end sm:gap-3",
        className,
      )}
    >
      {children}
    </div>
  );
};
