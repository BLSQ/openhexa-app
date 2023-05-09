import { Dialog as BaseDialog, Transition } from "@headlessui/react";
import { XMarkIcon } from "@heroicons/react/24/outline";
import clsx from "clsx";
import useEventListener from "core/hooks/useEventListener";
import { Fragment, ReactElement, ReactNode, useRef } from "react";

type DialogProps = {
  open: boolean;
  onClose: (value: any) => void;
  centered?: boolean;
  padding?: string;
  children: ReactElement | ReactElement[];
  closeOnOutsideClick?: boolean;
  closeOnEsc?: boolean;
  className?: string;
  maxWidth?: string;
};

const DialogTitle = (props: { children: ReactNode; onClose?: () => void }) => {
  return (
    <BaseDialog.Title
      as="h3"
      className="mb-5 flex items-center justify-between text-2xl font-medium text-gray-900 md:mb-7"
    >
      {props.children}
      {props.onClose && (
        <XMarkIcon className="h-6 w-6 cursor-pointer" onClick={props.onClose} />
      )}
    </BaseDialog.Title>
  );
};

const DialogContent = (props: { children: ReactNode; className?: string }) => {
  return <div className={props.className}>{props.children}</div>;
};

const DialogActions = (props: { children: ReactNode; className?: string }) => (
  <div className={clsx("mt-5 flex justify-end sm:gap-3 md:mt-7")}>
    {props.children}
  </div>
);

const DialogDescription = (props: {
  children: ReactNode;
  className?: string;
}) => (
  <div className={clsx("mb-3 text-gray-600", props.className)}>
    {props.children}
  </div>
);

function Dialog(props: DialogProps) {
  const {
    open,
    onClose,
    children,
    centered = true,
    padding,
    closeOnOutsideClick = true,
    closeOnEsc = true,
    className,
    maxWidth,
  } = props;

  const dialogRef = useRef(null);

  useEventListener(
    "keydown",
    (event) => {
      if (event.key === "Escape" && !closeOnEsc) {
        event.stopImmediatePropagation();
      }
    },
    dialogRef
  );

  return (
    <Transition.Root show={open} as={Fragment}>
      <BaseDialog
        ref={dialogRef}
        className="fixed inset-0 z-20"
        onClose={onClose}
      >
        <Transition.Child
          as={Fragment}
          enter="ease-out duration-300"
          enterFrom="opacity-0"
          enterTo="opacity-100"
          leave="ease-in duration-200"
          leaveFrom="opacity-100"
          leaveTo="opacity-0"
        >
          <BaseDialog.Overlay
            className={clsx(
              "fixed inset-0 bg-gray-800 bg-opacity-50 backdrop-blur-sm transition-opacity",
              !closeOnOutsideClick && "pointer-events-none" // Let's prevent mouse events to be triggered to ensure the dialog stay open.
            )}
          />
        </Transition.Child>
        <div className="h-screen px-4 pt-4 pb-20 text-center sm:block sm:p-0">
          {/* This element is to trick the browser into centering the modal contents. */}
          <span
            className={clsx(
              "hidden sm:inline-block sm:h-screen",
              centered && "sm:align-middle"
            )}
            aria-hidden="true"
          >
            &#8203;
          </span>
          <Transition.Child
            as={Fragment}
            enter="transition-all transform ease-out duration-300"
            enterFrom="opacity-0 translate-y-4 sm:translate-y-0 sm:scale-95"
            enterTo="opacity-100 translate-y-0 sm:scale-100"
            leave="transition-all transform ease-in duration-200"
            leaveFrom="opacity-100 translate-y-0 sm:scale-100"
            leaveTo="opacity-0 translate-y-4 sm:translate-y-0 sm:scale-95"
          >
            <div
              className={clsx(
                "inline-block transform px-2 transition-all sm:my-24 sm:w-full sm:px-4",
                maxWidth ?? "max-w-lg",
                centered && "sm:align-middle"
              )}
            >
              <div
                className={clsx(
                  "overflow-hidden rounded-lg bg-white text-left text-gray-600 shadow-2xl",
                  padding ?? "px-4 py-5 sm:p-6",
                  className
                )}
              >
                {children}
              </div>
            </div>
          </Transition.Child>
        </div>
      </BaseDialog>
    </Transition.Root>
  );
}

Dialog.Title = DialogTitle;
Dialog.Content = DialogContent;
Dialog.Description = DialogDescription;
Dialog.Actions = DialogActions;

export default Dialog;
