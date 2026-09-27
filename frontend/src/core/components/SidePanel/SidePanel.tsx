import { Transition } from "@headlessui/react";
import { XMarkIcon } from "@heroicons/react/24/outline";
import clsx from "clsx";
import { FormEvent, ReactNode, useEffect } from "react";

type SidePanelProps = {
  open: boolean;
  onClose: () => void;
  children: ReactNode;
  className?: string;
};

// Unlike Drawer (a modal headless-ui Dialog), this panel does not trap focus or
// make the page inert, so users can keep working next to it.
const SidePanel = ({ open, onClose, children, className }: SidePanelProps) => {
  useEffect(() => {
    if (!open) return;
    const onKeyDown = (event: KeyboardEvent) => {
      // Nested modal dialogs handle (and prevent) their own Escape.
      if (event.key === "Escape" && !event.defaultPrevented) {
        onClose();
      }
    };
    window.addEventListener("keydown", onKeyDown);
    return () => window.removeEventListener("keydown", onKeyDown);
  }, [open, onClose]);

  return (
    <Transition
      show={open}
      as="aside"
      enter="transition-transform duration-200 ease-out"
      enterFrom="translate-x-full"
      enterTo="translate-x-0"
      leave="transition-transform duration-150 ease-in"
      leaveFrom="translate-x-0"
      leaveTo="translate-x-full"
      data-testid="side-panel"
      className={clsx(
        "fixed inset-y-0 right-0 z-40 flex w-[480px] max-w-full flex-col border-l border-gray-200 bg-white shadow-[-8px_0_24px_-8px_rgba(0,0,0,0.12)]",
        className,
      )}
    >
      {children}
    </Transition>
  );
};

type SidePanelContentProps = {
  title: ReactNode;
  subtitle?: ReactNode;
  headerActions?: ReactNode;
  footer?: ReactNode;
  onClose: () => void;
  onSubmit?: (event: FormEvent<HTMLFormElement>) => void;
  children: ReactNode;
  className?: string;
};

const SidePanelContent = ({
  title,
  subtitle,
  headerActions,
  footer,
  onClose,
  onSubmit,
  children,
  className,
}: SidePanelContentProps) => {
  const inner = (
    <>
      <div className="flex flex-none items-center gap-2.5 border-b border-gray-200 px-5 py-3.5">
        <div className="min-w-0 flex-1">
          <div className="flex items-center gap-2 text-[15px] font-semibold text-gray-900">
            {title}
          </div>
          {subtitle && (
            <div className="mt-0.5 truncate text-xs text-gray-500">
              {subtitle}
            </div>
          )}
        </div>
        {headerActions}
        <button
          type="button"
          onClick={onClose}
          className="flex rounded-sm p-1.5 text-gray-500 hover:bg-gray-100 hover:text-gray-700"
        >
          <span className="sr-only">Close panel</span>
          <XMarkIcon className="h-4 w-4" />
        </button>
      </div>
      <div className="min-h-0 flex-1 overflow-y-auto">{children}</div>
      {footer && (
        <div className="flex flex-none items-center gap-2 border-t border-gray-200 px-5 py-3">
          {footer}
        </div>
      )}
    </>
  );
  const classes = clsx("flex min-h-0 flex-1 flex-col", className);

  return onSubmit ? (
    <form onSubmit={onSubmit} className={classes}>
      {inner}
    </form>
  ) : (
    <div className={classes}>{inner}</div>
  );
};

SidePanel.Content = SidePanelContent;

export default SidePanel;
