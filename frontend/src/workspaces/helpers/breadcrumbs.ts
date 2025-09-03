/**
 * Utility functions for handling breadcrumb navigation in bucket file systems
 */

export interface BreadcrumbItem {
  label: string;
  value: string;
}

/**
 * Generates breadcrumb items from a prefix path
 * @param prefix - The current prefix path (e.g., "folder1/folder2/")
 * @returns Array of breadcrumb items with label and value for navigation
 */
export function generateBreadcrumbs(prefix: string | null): BreadcrumbItem[] {
  if (!prefix) return [];

  const breadcrumbs: BreadcrumbItem[] = [];
  let accumulated = "";

  prefix
    .split("/")
    .filter(Boolean)
    .forEach((part) => {
      accumulated = accumulated ? `${accumulated}/${part}` : part;
      breadcrumbs.push({
        label: part,
        value: `${accumulated}/`,
      });
    });

  return breadcrumbs;
}
