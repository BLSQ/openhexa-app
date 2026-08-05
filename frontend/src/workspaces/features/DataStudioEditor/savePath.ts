type SavePathArgs = {
  isSaved: boolean;
  hasContent: boolean;
  canUpdate: boolean;
  canCreate: boolean;
};

// Whether the buffer can be written anywhere: over the loaded query, or forked
// into a new one. The Save control and the navigation guard both read this, so
// the editor cannot warn about changes it offers no way to keep — an emptied
// buffer, or a viewer who can neither update this query nor fork it.
export const hasSavePath = ({
  isSaved,
  hasContent,
  canUpdate,
  canCreate,
}: SavePathArgs) => hasContent && (canCreate || (isSaved && canUpdate));
