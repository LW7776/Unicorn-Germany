/** Escape a value for interpolation into HTML text or a quoted attribute.
    Every value rendered from data/companies.json goes through this — those
    files are written by hand and by the update pipeline, so neither is trusted. */
export function escapeHtml(value) {
  if (value === null || value === undefined) return "";
  return String(value)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;");
}
