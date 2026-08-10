import { formatDialect, postgresql } from "sql-formatter";

// Workspace databases are PostgreSQL, so parse with its dialect: the ANSI
// dialect chokes on Postgres-only syntax (casts with `::`, `RETURNING`, …).
// Naming the dialect rather than passing `language` to `format` also keeps the
// other ~22 dialects out of the bundle.
const OPTIONS = {
  dialect: postgresql,
  keywordCase: "upper",
  tabWidth: 2,
} as const;

/**
 * Pretty-print a SQL query. A query that cannot be parsed — which is the normal
 * state of a half-typed one — is returned untouched rather than mangled, so
 * formatting is never destructive.
 */
export const formatSql = (sql: string): string => {
  try {
    return formatDialect(sql, OPTIONS);
  } catch {
    return sql;
  }
};
