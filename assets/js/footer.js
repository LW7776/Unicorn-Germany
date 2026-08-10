/** Renders the footer shared by every page.

    It is a second navigation layer, not a row of links. Three labelled groups
    (the register, the site, contributing) so a reader who has reached the bottom
    of a page can see what else exists and pick from a structure rather than
    scanning a sentence of separators. The wordmark and the one line about how to
    read the figures sit alongside them.

    Every href works identically from index.html and from the static pages, which
    is why the register links point at `index.html` rather than at a bare `#`
    fragment: the same markup is rendered on all three pages, and a fragment that
    resolves on one of them and silently does nothing on the others is worse than
    a reload.

    The FX disclosure that backs the combined headline figure used to live here.
    It now sits in the About Q&A, next to the question a reader is actually asking
    when they want it. */
const GROUPS = [
  ["Register", [
    ["All companies", "index.html"],
    ["Weekly funding", "index.html#funding"],
  ]],
  ["Site", [
    ["About", "about.html"],
    ["Impressum", "impressum.html"],
  ]],
  ["Contribute", [
    ["Report an error", "https://github.com/LW7776/Unicorn-Germany/issues/new"],
    ["Source and data", "https://github.com/LW7776/Unicorn-Germany"],
  ]],
];

const external = (href) => href.startsWith("http");

export function renderFooter(container) {
  if (!container) return;
  const groups = GROUPS.map(([heading, links], index) => `
    <div class="footer__group">
      <h2 class="label" id="footer-group-${index}">${heading}</h2>
      <ul aria-labelledby="footer-group-${index}">
        ${links.map(([label, href]) => `
          <li><a href="${href}"${external(href)
            ? ' target="_blank" rel="noopener noreferrer"' : ""}>${label}</a></li>`).join("")}
      </ul>
    </div>`).join("");

  container.innerHTML = `
    <div class="footer__brand">
      <a class="topbar__mark" href="index.html">GERMAN&nbsp;UNICORNS</a>
      <p>Figures are indicative and carry the date they were reported.</p>
    </div>
    <nav class="footer__nav" aria-label="Footer">${groups}</nav>`;
}
