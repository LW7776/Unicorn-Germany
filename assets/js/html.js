/** Escape a value for interpolation into HTML text or a quoted attribute.
    Every value rendered from data/companies.json goes through this — those
    files are written by hand and by the update pipeline, so neither is trusted.
    Does not escape whitespace, so this is safe inside element text and inside
    a quoted attribute (single- or double-quoted) but NOT inside an unquoted
    attribute value — a space in the escaped output would still terminate it. */
export function escapeHtml(value) {
  if (value === null || value === undefined) return "";
  return String(value)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;");
}
