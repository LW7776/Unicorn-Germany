/** Renders the footer shared by every page: one line on how to read the figures,
    and the About / Impressum / report-an-error links.

    The FX disclosure that backs the combined headline figure used to live here.
    It now sits in the About Q&A, next to the question a reader is actually asking
    when they want it, rather than in a footer line nobody reads. The signature
    still accepts the stats object every caller already passes, so a future footer
    line that needs the rate can reach it without rewiring three call sites. */
export function renderFooter(container) {
  if (!container) return;
  container.innerHTML = `
    <p>Figures are indicative and carry the date they were reported.</p>
    <nav aria-label="Footer">
      <a href="about.html">About</a> ·
      <a href="impressum.html">Impressum</a> ·
      <a href="https://github.com/LW7776/Unicorn-Germany/issues/new" target="_blank" rel="noopener noreferrer">Report an error</a>
    </nav>`;
}
