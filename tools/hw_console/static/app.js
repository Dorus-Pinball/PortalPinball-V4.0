let selectedComponent = null;

function $(sel, root = document) { return root.querySelector(sel); }
function $all(sel, root = document) { return [...root.querySelectorAll(sel)]; }

function esc(str) {
  return String(str ?? "").replace(/[&<>"']/g, (c) => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;",
  })[c]);
}

// ---- Tabs ----
$all(".tab-btn").forEach((btn) => {
  btn.addEventListener("click", () => {
    $all(".tab-btn").forEach((b) => b.classList.remove("active"));
    $all(".tab").forEach((t) => t.classList.remove("active"));
    btn.classList.add("active");
    $(`#tab-${btn.dataset.tab}`).classList.add("active");
  });
});

// ---- Boards ----
async function loadBoards() {
  const boards = await fetch("/api/boards").then((r) => r.json());
  const tbody = $("#boards-table tbody");
  tbody.innerHTML = "";
  for (const [id, b] of Object.entries(boards)) {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td>${esc(b.display_name)}</td>
      <td>${esc(b.port)} / chain ${esc(b.chain)} / ${esc(b.address)}</td>
      <td>${esc(b.role)}</td>
      <td>${esc(b.firmware)}</td>
      <td><span class="status-badge ${esc(b.status)}">${esc(b.status)}</span></td>
      <td>
        <select data-board="${esc(id)}">
          <option value="scanned" ${b.status === "scanned" ? "selected" : ""}>scanned</option>
          <option value="connected" ${b.status === "connected" ? "selected" : ""}>connected</option>
          <option value="verified" ${b.status === "verified" ? "selected" : ""}>verified</option>
        </select>
      </td>`;
    tbody.appendChild(tr);
  }
  $all("select[data-board]").forEach((sel) => {
    sel.addEventListener("change", async () => {
      await fetch(`/api/boards/${sel.dataset.board}`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ status: sel.value }),
      });
      loadBoards();
    });
  });
}

// ---- Components ----
async function loadComponents() {
  const statusFilter = $("#status-filter").value;
  const url = statusFilter ? `/api/components?status=${statusFilter}` : "/api/components";
  const components = await fetch(url).then((r) => r.json());
  const list = $("#components-list");
  list.innerHTML = "";
  for (const [name, c] of Object.entries(components)) {
    const li = document.createElement("li");
    li.dataset.name = name;
    if (name === selectedComponent) li.classList.add("selected");
    li.innerHTML = `<span>${esc(c.display_name)}</span><span class="status-badge ${esc(c.status)}">${esc(c.status)}</span>`;
    li.addEventListener("click", () => selectComponent(name));
    list.appendChild(li);
  }
}

async function selectComponent(name) {
  selectedComponent = name;
  $all("#components-list li").forEach((li) => li.classList.toggle("selected", li.dataset.name === name));
  const c = await fetch(`/api/components/${name}`).then((r) => r.json());
  renderComponentDetail(name, c);
}

function renderComponentDetail(name, c) {
  const pane = $("#component-detail");
  const rows = (entries, kind) =>
    entries
      .map(
        (e) => `<tr>
          <td>${esc(e.name)}</td><td>${esc(e.number)}</td><td>${esc(e.board || "")}</td>
          <td>
            <select data-kind="${kind}" data-name="${esc(e.name)}">
              <option value="planned" ${e.status === "planned" ? "selected" : ""}>planned</option>
              <option value="wired" ${e.status === "wired" ? "selected" : ""}>wired</option>
              <option value="tested" ${e.status === "tested" ? "selected" : ""}>tested</option>
            </select>
          </td>
        </tr>`
      )
      .join("");

  pane.innerHTML = `
    <h2>${esc(c.display_name)}
      <select id="component-status">
        <option value="planned" ${c.status === "planned" ? "selected" : ""}>planned</option>
        <option value="wired" ${c.status === "wired" ? "selected" : ""}>wired</option>
        <option value="tested" ${c.status === "tested" ? "selected" : ""}>tested</option>
      </select>
    </h2>
    ${c.mpf_devices && c.mpf_devices.length ? `<p><em>MPF devices:</em> ${esc(c.mpf_devices.join(", "))}</p>` : ""}

    <h3>Switches</h3>
    <table><thead><tr><th>Name</th><th>Number</th><th>Board</th><th>Status</th></tr></thead>
      <tbody>${c.switches.length ? rows(c.switches, "switch") : '<tr><td colspan="4">none</td></tr>'}</tbody></table>

    <h3>Coils</h3>
    <table><thead><tr><th>Name</th><th>Number</th><th>Board</th><th>Status</th></tr></thead>
      <tbody>${c.coils.length ? rows(c.coils, "coil") : '<tr><td colspan="4">none</td></tr>'}</tbody></table>

    <h3>Wiring checklist</h3>
    ${c.checklist
      .map(
        (item, i) => `<div class="checklist-item">
          <input type="checkbox" data-checklist-idx="${i}" ${item.done ? "checked" : ""}>
          <label>${esc(item.item)}</label>
        </div>`
      )
      .join("")}

    <h3>Notes</h3>
    <div class="notes-box">${esc(c.notes) || "(none)"}</div>
  `;

  $("#component-status").addEventListener("change", async (e) => {
    await patchComponent(name, { status: e.target.value });
  });

  $all("select[data-kind]", pane).forEach((sel) => {
    sel.addEventListener("change", async () => {
      const key = sel.dataset.kind === "switch" ? "switch_status" : "coil_status";
      await patchComponent(name, { [key]: { name: sel.dataset.name, status: sel.value } });
    });
  });

  $all("input[data-checklist-idx]", pane).forEach((cb) => {
    cb.addEventListener("change", async () => {
      c.checklist[cb.dataset.checklistIdx].done = cb.checked;
      await patchComponent(name, { checklist: c.checklist });
    });
  });
}

async function patchComponent(name, body) {
  const res = await fetch(`/api/components/${name}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  const updated = await res.json();
  loadComponents();
  if (selectedComponent === name) renderComponentDetail(name, updated);
}

$("#status-filter").addEventListener("change", loadComponents);

// ---- Add component dialog ----
const dialog = $("#new-component-dialog");
$("#new-component-btn").addEventListener("click", () => {
  $("#new-switches").innerHTML = "";
  $("#new-coils").innerHTML = "";
  $("#new-component-form").reset();
  $("#new-component-error").hidden = true;
  dialog.showModal();
});
$("#cancel-new-component").addEventListener("click", () => dialog.close());

function entryRowHtml(kind) {
  return `<div class="entry-row" data-kind="${kind}">
    <input placeholder="${kind === "switch" ? "s-" : "c-"}name" data-field="name">
    <input placeholder="chain-card-number" data-field="number">
    <input placeholder="board id" data-field="board">
    <button type="button" class="remove-row-btn">x</button>
  </div>`;
}

$all(".add-row-btn").forEach((btn) => {
  btn.addEventListener("click", () => {
    const container = btn.dataset.kind === "switch" ? $("#new-switches") : $("#new-coils");
    container.insertAdjacentHTML("beforeend", entryRowHtml(btn.dataset.kind));
  });
});

document.addEventListener("click", (e) => {
  if (e.target.classList.contains("remove-row-btn")) {
    e.target.closest(".entry-row").remove();
  }
});

function collectEntries(containerId) {
  return $all(`#${containerId} .entry-row`)
    .map((row) => ({
      name: $('[data-field="name"]', row).value.trim(),
      number: $('[data-field="number"]', row).value.trim(),
      board: $('[data-field="board"]', row).value.trim(),
    }))
    .filter((e) => e.name && e.number);
}

$("#new-component-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const form = e.target;
  const body = {
    name: form.name.value.trim(),
    display_name: form.display_name.value.trim(),
    notes: form.notes.value.trim(),
    switches: collectEntries("new-switches"),
    coils: collectEntries("new-coils"),
  };

  const res = await fetch("/api/components", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });

  if (!res.ok) {
    const err = await res.json();
    const msg = err.conflicts ? err.conflicts.join("; ") : err.error;
    const errEl = $("#new-component-error");
    errEl.textContent = msg;
    errEl.hidden = false;
    return;
  }

  dialog.close();
  loadComponents();
});

loadBoards();
loadComponents();
