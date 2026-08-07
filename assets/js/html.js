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

/** True only for absolute http/https URLs — blocks `javascript:`, `data:`, and
    anything else that would be unsafe to drop into an href even once escaped.
    Escaping alone does not make a URL safe: it stops the string from breaking
    out of the attribute, but a syntactically valid `javascript:` URL still
    executes on click regardless of how cleanly it's escaped. Any value bound
    for an href — from data/companies.json or from a future form editor
    (Task 13) — should be checked here before it is ever rendered as a link. */
export function isSafeUrl(value) {
  try {
    const url = new URL(value, location.href);
    return url.protocol === "http:" || url.protocol === "https:";
  } catch {
    return false;
  }
}
