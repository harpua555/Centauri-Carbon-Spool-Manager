class CentauriSpoolHistoryCard extends HTMLElement {
  setConfig(config) {
    if (!config.entity) {
      throw new Error("entity is required (text history entity)");
    }
    if (!config.spool_number) {
      throw new Error("spool_number is required (1-4)");
    }
    this._config = {
      title: "Spool History",
      max_entries: 50,
      ...config,
    };
    this._hass = null;
    this._entries = [];
    this._error = null;
    this._root = this.attachShadow({ mode: "open" });
  }

  set hass(hass) {
    this._hass = hass;
    if (!this._config) return;

    const stateObj = hass.states[this._config.entity];
    if (!stateObj) {
      this._error = `Entity ${this._config.entity} not found`;
      this._entries = [];
      this._render();
      return;
    }

    // Prefer the dedicated `history` attribute provided by the
    // SpoolHistoryText entity. This avoids the 255-character state length
    // limit and keeps history in attributes instead.
    const attrHist = stateObj.attributes && stateObj.attributes.history;

    if (Array.isArray(attrHist)) {
      this._entries = attrHist.slice(-this._config.max_entries);
      this._error = null;
      this._render();
      return;
    }

    // Backwards compatibility: fall back to parsing the state as JSON.
    const raw = (stateObj.state || "").trim();
    if (!raw || raw === "unknown" || raw === "unavailable") {
      this._entries = [];
      this._error = null;
      this._render();
      return;
    }

    try {
      const parsed = JSON.parse(raw);
      if (Array.isArray(parsed)) {
        this._entries = parsed.slice(-this._config.max_entries);
        this._error = null;
      } else {
        this._entries = [];
        this._error = "History JSON is not a list";
      }
    } catch (e) {
      // eslint-disable-next-line no-console
      console.error("Failed to parse spool history JSON", e);
      this._entries = [];
      this._error = "Failed to parse history JSON";
    }

    this._render();
  }

  getCardSize() {
    return 4;
  }

  _render() {
    if (!this._root) return;

    const haCard = document.createElement("ha-card");
    haCard.header = this._config.title;

    const style = document.createElement("style");
    style.textContent = `
      table {
        width: 100%;
        border-collapse: collapse;
      }
      th, td {
        padding: 4px 6px;
        text-align: left;
        font-size: 0.9em;
      }
      th {
        border-bottom: 1px solid var(--divider-color);
      }
      tr:nth-child(even) td {
        background: rgba(0, 0, 0, 0.02);
      }
      button {
        font: inherit;
        border: none;
        background: none;
        color: var(--accent-color);
        cursor: pointer;
        padding: 2px 6px;
        border-radius: 4px;
      }
      button:hover {
        background: rgba(0, 0, 0, 0.04);
      }
      .empty {
        padding: 8px;
        font-size: 0.9em;
        color: var(--secondary-text-color);
      }
      .error {
        padding: 8px;
        font-size: 0.9em;
        color: var(--error-color);
      }
    `;

    const content = document.createElement("div");
    if (this._error) {
      content.innerHTML = `<div class="error">${this._error}</div>`;
    } else if (!this._entries || this._entries.length === 0) {
      content.innerHTML = `<div class="empty">No prints logged yet.</div>`;
    } else {
      const rowsHtml = this._entries
        .map((entry, index) => {
          // Support both old and new history formats.
          const time = entry.t || entry.date || "";
          const file = entry.f || entry.file || "";
          const material = entry.m || entry.material || "";
          const length =
            entry.mm != null
              ? entry.mm
              : entry.length_mm != null
              ? entry.length_mm
              : "";
          const weight =
            entry.w != null
              ? entry.w
              : entry.weight_g != null
              ? entry.weight_g
              : "";

          // Entries are stored oldest-first; we render newest-first.
          const originalIndex = this._entries.length - 1 - index;

          return `
            <tr>
              <td>${time}</td>
              <td>${file}</td>
              <td>${material}</td>
              <td>${length}</td>
              <td>${weight}</td>
              <td>
                <button data-index="${originalIndex}">Undo</button>
              </td>
            </tr>
          `;
        })
        .join("");

      content.innerHTML = `
        <table>
          <thead>
            <tr>
              <th>Time</th>
              <th>File</th>
              <th>Material</th>
              <th>Length (mm)</th>
              <th>Weight (g)</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            ${rowsHtml}
          </tbody>
        </table>
      `;

      content.querySelectorAll("button[data-index]").forEach((btn) => {
        btn.addEventListener("click", (ev) => this._handleUndoClick(ev));
      });
    }

    haCard.appendChild(style);
    haCard.appendChild(content);

    // Clear and reattach
    while (this._root.firstChild) {
      this._root.removeChild(this._root.firstChild);
    }
    this._root.appendChild(haCard);
  }

  _handleUndoClick(ev) {
    if (!this._hass || !this._config) return;

    const target = ev.currentTarget;
    const idxAttr = target.getAttribute("data-index");
    if (idxAttr == null) return;

    const entryIndex = parseInt(idxAttr, 10);
    if (Number.isNaN(entryIndex)) return;

    const spoolNumber = this._config.spool_number;

    this._hass.callService("centauri_spool_manager", "undo_history_entry", {
      spool_number: spoolNumber,
      entry_index: entryIndex,
    });
  }

  static getConfigElement() {
    return document.createElement("hui-element-editor");
  }

  static getStubConfig() {
    return {
      title: "Spool History",
      entity: "text.centauri_spool_manager_spool_1_history",
      spool_number: 1,
    };
  }
}

customElements.define(
  "centauri-spool-history-card",
  CentauriSpoolHistoryCard,
);

window.customCards = window.customCards || [];
window.customCards.push({
  type: "centauri-spool-history-card",
  name: "Centauri Spool History Card",
  description: "Shows spool print history with per-row undo buttons.",
});
