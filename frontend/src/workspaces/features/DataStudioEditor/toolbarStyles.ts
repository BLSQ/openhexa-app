// Shared classes for the editor toolbar's ghost buttons, so every control in the
// bar keeps the same height, spacing and disabled treatment.
export const GHOST =
  "inline-flex h-8 items-center gap-1.5 rounded-md px-2.5 text-xs font-medium text-gray-700 hover:bg-gray-100 disabled:cursor-not-allowed disabled:text-gray-300 disabled:hover:bg-transparent";

// Muted sibling of GHOST for secondary actions, so they read as clearly
// subordinate to the primary one without hiding in a menu.
export const GHOST_SECONDARY =
  "inline-flex h-8 items-center gap-1.5 rounded-md px-2.5 text-xs font-medium text-gray-500 hover:bg-gray-100 hover:text-gray-700 disabled:cursor-not-allowed disabled:text-gray-300 disabled:hover:bg-transparent";

// Amber accent for the primary Save when a saved query has unsaved edits, so the
// button itself signals "you have work to persist" (no separate dirty dot). Only
// applied while the button is actionable, so it never tints the disabled state.
export const GHOST_DIRTY =
  "inline-flex h-8 items-center gap-1.5 rounded-md px-2.5 text-xs font-medium text-amber-600 hover:bg-amber-50 hover:text-amber-700";
