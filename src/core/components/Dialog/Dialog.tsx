import {
  Dialog as BaseDialog,
  DialogTitle as BaseDialogTitle,
  DialogBackdrop,
  DialogPanel,
} from "@headlessui/react";
import { XMarkIcon } from "@heroicons/react/24/outline";
import clsx from "clsx";
import useEventListener from "core/hooks/useEventListener";
import { FormEventHandler, ReactElement, ReactNode, useRef } from "react";

type DialogProps = {
  open: boolean;
  onClose: (value: any) => void;
  centered?: boolean;
  padding?: string;
  children: ReactElement | ReactElement[] | ReactNode[] | ReactNode;
  onSubmit?: FormEventHandler;
  closeOnEsc?: boolean;
  className?: string;
  maxWidth?: string;
  persistent?: boolean;
};

const DialogTitle = (props: { children: ReactNode; onClose?: () => void }) => {
  return (
    <BaseDialogTitle
      as="h3"
      className="mb-2 tall:mb-7 flex items-center justify-between text-2xl font-medium text-gray-900"
    >
      {props.children}
      {props.onClose && (
        <XMarkIcon className="h-6 w-6 cursor-pointer" onClick={props.onClose} />
      )}
    </BaseDialogTitle>
  );
};

const DialogContent = (props: { children: ReactNode; className?: string }) => {
  return (
    <div
      className={clsx(
        "flex-1 overflow-y-auto -mx-4 px-4 tall:px-6 tall:-mx-6 -my-1 py-1",
        props.className,
      )}
    >
      {props.children}
    </div>
  );
};

const DialogActions = (props: { children: ReactNode; className?: string }) => (
  <div
    className={clsx(
      "mt-3 flex justify-end sm:gap-3 tall:mt-7",
      props.className,
    )}
  >
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
    onSubmit,
    children,
    centered = true,
    padding,
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
    dialogRef,
  );

  const ContentElement = onSubmit ? "form" : "div";

  return (
    <BaseDialog
      ref={dialogRef}
      className="fixed inset-0 z-20"
      open={open}
      onClose={onClose}
    >
      <DialogBackdrop
        transition
        className="fixed inset-0 bg-black/30 duration-300 backdrop-blur-xs ease-out data-[closed]:opacity-0"
      />
      <div className="h-screen px-4 pb-20 pt-4 text-center sm:block sm:p-0">
        <DialogPanel
          transition
          className={clsx(
            "duration-300 transform ease-out data-[closed]:scale-95 data-[closed]:opacity-0",
            "my-8 inline-block px-2 sm:w-full sm:px-4 tall:my-20 max-h-full",
            maxWidth ?? "max-w-lg",
            centered && "sm:align-middle",
          )}
        >
          <ContentElement
            onSubmit={onSubmit}
            className={clsx(
              "rounded-lg bg-white text-left text-gray-600 shadow-2xl",
              padding ?? "px-4 py-5 tall:p-6",
              "flex flex-col",
              className,
            )}
            style={{ maxHeight: "calc(100vh - 5rem)" }}
          >
            {children}
          </ContentElement>
        </DialogPanel>
      </div>
    </BaseDialog>
  );
}

Dialog.Title = DialogTitle;
Dialog.Content = DialogContent;
Dialog.Description = DialogDescription;
Dialog.Actions = DialogActions;

export default Dialog;
