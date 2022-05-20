import { Dialog as BaseDialog, Transition } from "@headlessui/react";
import { XIcon } from "@heroicons/react/outline";
import clsx from "clsx";
import useEventListener from "core/hooks/useEventListener";
import { Fragment, ReactElement, ReactNode, useRef } from "react";

type DialogProps = {
  open: boolean;
  onClose: (value: any) => void;
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
        <XIcon className="h-6 w-6 cursor-pointer" onClick={props.onClose} />
      )}
    </BaseDialog.Title>
  );
};

const DialogContent = (props: { children: ReactNode; className?: string }) => {
  return <div className={props.className}>{props.children}</div>;
};

const DialogActions = (props: { children: ReactNode }) => (
  <div className="mt-5 flex justify-end sm:gap-3 md:mt-7">{props.children}</div>
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
        className="fixed inset-0 z-10 overflow-y-auto"
        onClose={onClose}
      >
        <div className="flex min-h-screen items-end justify-center px-4 pt-4 pb-20 text-center sm:block sm:p-0">
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
                "fixed inset-0 bg-gray-500 bg-opacity-80 backdrop-blur-sm transition-opacity",
                !closeOnOutsideClick && "pointer-events-none" // Let's prevent mouse events to be triggered to ensure the dialog stay open.
              )}
            />
          </Transition.Child>

          {/* This element is to trick the browser into centering the modal contents. */}
          <span
            className="hidden sm:inline-block sm:h-screen sm:align-middle"
            aria-hidden="true"
          >
            &#8203;
          </span>
          <Transition.Child
            as={Fragment}
            enter="ease-out duration-300"
            enterFrom="opacity-0 translate-y-4 sm:translate-y-0 sm:scale-95"
            enterTo="opacity-100 translate-y-0 sm:scale-100"
            leave="ease-in duration-200"
            leaveFrom="opacity-100 translate-y-0 sm:scale-100"
            leaveTo="opacity-0 translate-y-4 sm:translate-y-0 sm:scale-95"
          >
            <div
              className={clsx(
                "inline-block transform overflow-hidden rounded-lg bg-white px-4 py-5 text-left text-gray-600 shadow-xl transition-all sm:my-8 sm:w-full sm:p-6 sm:align-middle",
                maxWidth ?? "max-w-lg",
                className
              )}
            >
              {children}
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
