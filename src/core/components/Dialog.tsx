import {
  Dialog as BaseDialog,
  DialogTitle as BaseDialogTitle,
  Transition,
  TransitionChild,
} from "@headlessui/react";
import { XMarkIcon } from "@heroicons/react/24/outline";
import clsx from "clsx";
import useEventListener from "core/hooks/useEventListener";
import {
  FormEventHandler,
  Fragment,
  ReactElement,
  ReactNode,
  useRef,
} from "react";

type DialogProps = {
  open: boolean;
  onClose: (value: any) => void;
  centered?: boolean;
  padding?: string;
  children: ReactElement | ReactElement[] | ReactNode[] | ReactNode;
  onSubmit?: FormEventHandler;
  closeOnOutsideClick?: boolean;
  closeOnEsc?: boolean;
  className?: string;
  maxWidth?: string;
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
    dialogRef,
  );

  const ContentElement = onSubmit ? "form" : "div";

  return (
    <Transition show={open} as={Fragment}>
      <BaseDialog
        ref={dialogRef}
        className="fixed inset-0 z-20"
        onClose={onClose}
      >
        <TransitionChild
          as="div"
          enter="ease-out duration-300"
          enterFrom="opacity-0"
          enterTo="opacity-100"
          leave="ease-in duration-200"
          leaveFrom="opacity-100"
          leaveTo="opacity-0"
          className={clsx(
            "fixed inset-0 -z-10 bg-gray-800 bg-opacity-50 backdrop-blur-sm transition-opacity",
            !closeOnOutsideClick && "pointer-events-none", // Let's prevent mouse events to be triggered to ensure the dialog stay open.
          )}
        />
        <div className="h-screen px-4 pb-20 pt-4 text-center sm:block sm:p-0">
          {/* This element is to trick the browser into centering the modal contents. */}
          <span
            className={clsx(
              "hidden sm:inline-block sm:h-screen",
              centered && "sm:align-middle",
            )}
            aria-hidden="true"
          >
            &#8203;
          </span>
          <TransitionChild
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
                "my-8 inline-block transform px-2 transition-all sm:w-full sm:px-4 tall:my-20 max-h-full",
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
            </div>
          </TransitionChild>
        </div>
      </BaseDialog>
    </Transition>
  );
}

Dialog.Title = DialogTitle;
Dialog.Content = DialogContent;
Dialog.Description = DialogDescription;
Dialog.Actions = DialogActions;

export default Dialog;
