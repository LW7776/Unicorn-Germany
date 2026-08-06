import { escapeHtml } from "./html.js";

const SORTS = {
  newest: (a, b) => cmp(b.sort.newest, a.sort.newest),
  valuation: (a, b) => b.sort.valuationEur - a.sort.valuationEur,
  latest: (a, b) => cmp(b.sort.latestRound, a.sort.latestRound),
  name: (a, b) => a.sort.name.localeCompare(b.sort.name),
};

function cmp(a, b) { return a[0] - b[0] || a[1] - b[1]; }

export function applyState(companies, state) {
  const query = state.query.trim().toLowerCase();
  return companies
    .filter((c) => !state.sector || c.sectors.includes(state.sector))
    .filter((c) => !state.city || c.hq.city === state.city)
    .filter((c) => !query
      || c.name.toLowerCase().includes(query)
      || c.sectors.join(" ").toLowerCase().includes(query)
      || c.hq.city.toLowerCase().includes(query)
      || (c.investors || []).join(" ").toLowerCase().includes(query))
    .sort(SORTS[state.sort]);
}

export function mountControls({ container, companies, onChange }) {
  const state = { query: "", sector: "", city: "", sort: "newest" };
  const sectors = [...new Set(companies.flatMap((c) => c.sectors))].sort();
  const cities = [...new Set(companies.map((c) => c.hq.city))].sort();

  // Every sector and city string below comes from data/companies.json — hand-
  // written and pipeline-generated, so untrusted like every other company
  // value. escapeHtml() is safe inside these quoted attributes and text
  // nodes (but not inside an unquoted attribute), so every attribute here
  // stays quoted.
  container.innerHTML = `
    <div class="controls__row">
      <label class="controls__search">
        <span class="visually-hidden">Search companies</span>
        <input type="search" data-query placeholder="Search company, city or investor"
               autocomplete="off">
        <kbd aria-hidden="true">⌘K</kbd>
      </label>
      <label class="controls__select">
        <span class="label">Sort</span>
        <select data-sort>
          <option value="newest">Newest unicorn</option>
          <option value="valuation">Highest valuation</option>
          <option value="latest">Latest round</option>
          <option value="name">A–Z</option>
        </select>
      </label>
      <label class="controls__select">
        <span class="label">City</span>
        <select data-city>
          <option value="">All cities</option>
          ${cities.map((c) => `<option value="${escapeHtml(c)}">${escapeHtml(c)}</option>`).join("")}
        </select>
      </label>
    </div>
    <div class="chips" role="group" aria-label="Filter by sector">
      <button class="chip" type="button" data-sector="" aria-pressed="true">All sectors</button>
      ${sectors.map((s) => `<button class="chip" type="button" data-sector="${escapeHtml(s)}" aria-pressed="false">${escapeHtml(s)}</button>`).join("")}
    </div>
    <p class="controls__count" role="status" data-count></p>`;

  const queryInput = container.querySelector("[data-query]");

  const emit = () => {
    const visible = applyState(companies, state);
    // companies.length can be 0 before Tasks 15–18 populate data/companies.json;
    // "0 of 0 companies" still reads sensibly, no NaN or blank string.
    container.querySelector("[data-count]").textContent =
      `${visible.length} of ${companies.length} companies`;
    onChange(visible);
  };

  queryInput.addEventListener("input", (event) => {
    state.query = event.target.value; emit();
  });
  container.querySelector("[data-sort]").addEventListener("change", (event) => {
    state.sort = event.target.value; emit();
  });
  container.querySelector("[data-city]").addEventListener("change", (event) => {
    state.city = event.target.value; emit();
  });
  container.querySelectorAll("[data-sector]").forEach((chip) => {
    chip.addEventListener("click", () => {
      state.sector = chip.dataset.sector;
      container.querySelectorAll("[data-sector]").forEach((other) =>
        other.setAttribute("aria-pressed", String(other === chip)));
      emit();
    });
  });

  addEventListener("keydown", (event) => {
    if (!(event.metaKey || event.ctrlKey) || event.key.toLowerCase() !== "k") return;
    // Skip while the search field already has focus: macOS text fields bind
    // Ctrl+K natively to "delete to end of line", and the input is already
    // where ⌘K would send focus, so there is nothing useful to preempt.
    // Hijacking it here would silently eat that native editing shortcut
    // while someone is mid-edit in the very field the shortcut targets.
    if (document.activeElement === queryInput) return;
    event.preventDefault();
    queryInput.focus();
  });
  document.querySelector("[data-open-search]")?.addEventListener("click", () => {
    queryInput.focus();
  });

  emit();
  return { state, setCity: (city) => { state.city = city; container.querySelector("[data-city]").value = city; emit(); } };
}
