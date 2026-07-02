import { Menu, MenuButton, MenuItem, MenuItems } from "@headlessui/react";
import { ChevronDownIcon } from "@heroicons/react/24/outline";
import clsx from "clsx";
import { ComponentType } from "react";

type IconType = ComponentType<{ className?: string }>;

export type SplitButtonAction = {
  label: string;
  onClick: () => void;
  icon?: IconType;
  /** Tailwind classes for the action icon; defaults to a neutral gray. */
  iconClassName?: string;
  disabled?: boolean;
};

type SplitButtonProps = {
  /** Label of the primary (left) button. */
  label: string;
  /** Primary action, also triggered by the main button. */
  onClick: () => void;
  /** Secondary actions shown in the chevron dropdown. */
  actions: SplitButtonAction[];
  icon?: IconType;
  disabled?: boolean;
  loading?: boolean;
  /** Label shown on the primary button while loading; falls back to `label`. */
  loadingLabel?: string;
  /** Accessible label for the chevron menu trigger. */
  menuLabel?: string;
  className?: string;
};

// A primary action button joined to a chevron that opens a menu of alternative
// actions. Built on Headless UI's Menu so the dropdown gets focus management,
// Escape-to-close, click-outside and ARIA roles; `anchor` positions and portals
// the panel so it is never clipped by an ancestor's overflow.
const SplitButton = ({
  label,
  onClick,
  actions,
  icon: Icon,
  disabled = false,
  loading = false,
  loadingLabel,
  menuLabel = "More options",
  className,
}: SplitButtonProps) => {
  return (
    <div
      className={clsx(
        "inline-flex h-8 items-stretch rounded-md bg-blue-600 shadow-xs",
        className,
      )}
    >
      <button
        onClick={onClick}
        disabled={disabled}
        className="inline-flex items-center gap-1.5 rounded-l-md px-3 text-xs font-medium text-white hover:bg-blue-700 disabled:opacity-60"
      >
        {loading ? (
          <>
            <span className="h-3 w-3 animate-spin rounded-full border-2 border-white/40 border-t-white" />
            {loadingLabel ?? label}
          </>
        ) : (
          <>
            {Icon && <Icon className="h-3 w-3" />}
            {label}
          </>
        )}
      </button>
      <Menu as="div" className="flex">
        <MenuButton
          aria-label={menuLabel}
          className="inline-flex h-8 w-7 items-center justify-center rounded-r-md border-l border-white/20 text-white hover:bg-blue-700"
        >
          <ChevronDownIcon className="h-3.5 w-3.5" />
        </MenuButton>
        <MenuItems
          anchor={{ to: "bottom end", gap: 4 }}
          className="z-50 w-52 rounded-md bg-white py-1 text-xs shadow-xl ring-1 ring-black/5 focus:outline-none"
        >
          {actions.map((action) => {
            const ActionIcon = action.icon;
            return (
              <MenuItem
                key={action.label}
                as="button"
                onClick={action.onClick}
                disabled={action.disabled}
                className="flex w-full items-center gap-2 px-3 py-1.5 text-left text-gray-800 hover:bg-gray-100 data-[focus]:bg-gray-100 data-[disabled]:text-gray-300"
              >
                {ActionIcon && (
                  <ActionIcon
                    className={clsx(
                      "h-3.5 w-3.5",
                      action.iconClassName ?? "text-gray-400",
                    )}
                  />
                )}
                {action.label}
              </MenuItem>
            );
          })}
        </MenuItems>
      </Menu>
    </div>
  );
};

export default SplitButton;
