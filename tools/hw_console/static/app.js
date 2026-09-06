let selectedComponent = null;

const STATUS_LABELS = {
  1: "Idea - no hardware yet",
  2: "Hardware - no idea yet",
  3: "Hardware with a purpose - not renovated",
  4: "Renovated hardware with a purpose - not wired",
  5: "Fully connected - not tested",
  6: "Ready - connected & tested",
};

function statusOptionsHtml(selected) {
  return Object.entries(STATUS_LABELS)
    .map(([value, label]) => `<option value="${value}" ${Number(selected) === Number(value) ? "selected" : ""}>${value} - ${esc(label)}</option>`)
    .join("");
}

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
    li.innerHTML = `<span>${esc(c.display_name)}</span><span class="status-badge status-${esc(c.status)}">${esc(c.status)} - ${esc(STATUS_LABELS[c.status])}</span>`;
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
  const rows = (entries) =>
    entries
      .map(
        (e) => `<tr>
          <td>${esc(e.name)}</td><td>${esc(e.number)}</td><td>${esc(e.board || "")}</td>
        </tr>`
      )
      .join("");

  pane.innerHTML = `
    <h2>
      <input type="text" id="component-name" value="${esc(c.display_name)}">
      <select id="component-status">${statusOptionsHtml(c.status)}</select>
    </h2>
    ${c.mpf_devices && c.mpf_devices.length ? `<p><em>MPF devices:</em> ${esc(c.mpf_devices.join(", "))}</p>` : ""}

    <h3>Switches <span class="readonly-hint">(read-only - change via chat)</span></h3>
    <table><thead><tr><th>Name</th><th>Number</th><th>Board</th></tr></thead>
      <tbody>${c.switches.length ? rows(c.switches) : '<tr><td colspan="3">none</td></tr>'}</tbody></table>

    <h3>Coils <span class="readonly-hint">(read-only - change via chat)</span></h3>
    <table><thead><tr><th>Name</th><th>Number</th><th>Board</th></tr></thead>
      <tbody>${c.coils.length ? rows(c.coils) : '<tr><td colspan="3">none</td></tr>'}</tbody></table>

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

  $("#component-name").addEventListener("change", async (e) => {
    await patchComponent(name, { display_name: e.target.value });
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

// ---- Add element dialog ----
const dialog = $("#new-component-dialog");
$("#new-component-btn").addEventListener("click", () => {
  $("#new-component-form").reset();
  $("#new-component-error").hidden = true;
  dialog.showModal();
});
$("#cancel-new-component").addEventListener("click", () => dialog.close());

$("#new-component-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const form = e.target;
  const body = {
    name: form.name.value.trim(),
    display_name: form.display_name.value.trim(),
    status: Number(form.status.value),
    notes: form.notes.value.trim(),
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

// ---- Review-all mode: walk every element one at a time ----
let reviewEntries = [];
let reviewIndex = 0;
const reviewDialog = $("#review-dialog");

$("#review-btn").addEventListener("click", async () => {
  const components = await fetch("/api/components").then((r) => r.json());
  reviewEntries = Object.entries(components);
  if (!reviewEntries.length) return;
  reviewIndex = 0;
  renderReviewStep();
  reviewDialog.showModal();
});

function renderReviewStep() {
  const [name, c] = reviewEntries[reviewIndex];
  $("#review-progress").textContent = `Element ${reviewIndex + 1} of ${reviewEntries.length}`;
  $("#review-name").textContent = c.display_name;

  const pinCount = c.switches.length + c.coils.length;
  $("#review-hint").textContent = pinCount
    ? `${c.switches.length} switch(es), ${c.coils.length} coil(s) assigned.`
    : "No pins assigned yet.";

  $("#review-options").innerHTML = Object.entries(STATUS_LABELS)
    .map(
      ([value, label]) => `<label class="review-option">
        <input type="radio" name="review-status" value="${value}" ${Number(c.status) === Number(value) ? "checked" : ""}>
        ${value} - ${esc(label)}
      </label>`
    )
    .join("");

  $all('input[name="review-status"]', reviewDialog).forEach((radio) => {
    radio.addEventListener("change", async () => {
      await patchComponent(name, { status: Number(radio.value) });
      reviewEntries[reviewIndex][1].status = Number(radio.value);
    });
  });

  $("#review-prev").disabled = reviewIndex === 0;
  $("#review-next").textContent = reviewIndex === reviewEntries.length - 1 ? "Done" : "Next →";
}

$("#review-prev").addEventListener("click", () => {
  if (reviewIndex > 0) {
    reviewIndex -= 1;
    renderReviewStep();
  }
});

$("#review-next").addEventListener("click", () => {
  if (reviewIndex < reviewEntries.length - 1) {
    reviewIndex += 1;
    renderReviewStep();
  } else {
    reviewDialog.close();
  }
});

$("#review-close").addEventListener("click", () => reviewDialog.close());
reviewDialog.addEventListener("close", () => loadComponents());

loadBoards();
loadComponents();
