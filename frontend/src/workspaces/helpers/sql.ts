// PostgreSQL's lexer accepts space, tab, newline, carriage return and form feed
// as whitespace and nothing else, so every other blank -- non-breaking space,
// ideographic space, vertical tab, ... -- is a syntax error reported at a
// character the user cannot see. SQL pasted from a chat, a document or a PDF is
// full of them.
//
// Matches such a blank, or any non-ASCII character (a cheap filter that lets the
// replacer run only where something may be wrong; legitimate non-ASCII, e.g. an
// accented identifier, is returned unchanged).
const SUSPICIOUS_CHARACTER = /[^\S \t\n\r\f]|[^\x00-\x7f]/g;

// Zero-width and other formatting characters (ZWSP, BOM, soft hyphen, bidi
// marks): they separate nothing, so dropping them restores the statement the
// user believes they wrote. This is Unicode's Cf category, spelled out because
// `\p{Cf}` needs a regex flag the TypeScript target does not allow.
const INVISIBLE_CHARACTER =
  /[\u00ad\u0600-\u0605\u061c\u06dd\u070f\u08e2\u180e\u200b-\u200f\u202a-\u202e\u2060-\u2064\u2066-\u206f\ufeff\ufff9-\ufffb]/;

const WHITESPACE = /\s/;

// Start of a region PostgreSQL accepts any character in -- comment, string
// literal, quoted identifier, dollar-quoted body -- where an exotic blank is
// data rather than a typo.
const REGION_START = /--|\/\*|'|"|\$[A-Za-z_]*\$/g;

const closingDelimiter = (opening: string): string => {
  switch (opening) {
    case "--":
      return "\n";
    case "/*":
      return "*/";
    // Quotes and dollar tags close on themselves. A doubled quote (the escape
    // for a quote inside a literal) simply reopens the region on the next pass.
    default:
      return opening;
  }
};

const clean = (text: string): string =>
  text.replace(SUSPICIOUS_CHARACTER, (character) => {
    if (INVISIBLE_CHARACTER.test(character)) {
      return "";
    }
    return WHITESPACE.test(character) ? " " : character;
  });

/**
 * Replace the blanks PostgreSQL cannot parse with plain spaces and drop
 * zero-width characters, leaving comments, string literals and quoted
 * identifiers verbatim.
 *
 * Mirrors the backend's `PreparedQuery`, which sanitises every query on its way
 * to the database; this one runs on text entering the editor, so that what the
 * user sees and saves is what actually runs.
 */
export const sanitizeSqlWhitespace = (sql: string): string => {
  let result = "";
  let cursor = 0;
  REGION_START.lastIndex = 0;
  let opening = REGION_START.exec(sql);
  while (opening !== null) {
    const closing = closingDelimiter(opening[0]);
    const closesAt = sql.indexOf(closing, opening.index + opening[0].length);
    // An unterminated region runs to the end of the text.
    const end = closesAt === -1 ? sql.length : closesAt + closing.length;
    result +=
      clean(sql.slice(cursor, opening.index)) + sql.slice(opening.index, end);
    cursor = end;
    REGION_START.lastIndex = end;
    opening = REGION_START.exec(sql);
  }
  return result + clean(sql.slice(cursor));
};
