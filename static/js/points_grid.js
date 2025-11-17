const MIN_ROWS = 4;
const FIXED_COLS = 2;

function createPointsGrid(containerId, rows = 2) {
  const container = document.getElementById(containerId);
  if (!container) return;

  rows = Math.max(rows, MIN_ROWS);
  container.innerHTML = "";
  container.classList.add("matrix-table");

  const table = document.createElement("table");
  table.className = "table table-bordered table-sm text-center";

  for (let r = 0; r < rows; r++) {
    const tr = document.createElement("tr");
    for (let c = 0; c < FIXED_COLS; c++) {
      tr.appendChild(createCellElement(table));
    }
    table.appendChild(tr);
  }

  container.appendChild(table);
}

function createCellElement(table) {
  const td = document.createElement("td");
  const input = document.createElement("input");
  input.type = "text";
  input.className = "matrix-input form-control form-control-sm text-center";
  input.placeholder = "0";

  input.addEventListener("input", () => validateInput(input));
  input.addEventListener("keydown", (ev) => {
    restrictKey(ev);
    const row = input.closest("tr").rowIndex;
    const col = input.closest("td").cellIndex;
    handleKey(ev, row, col, table);
  });

  td.appendChild(input);
  return td;
}

function restrictKey(e) {
  const allowedKeys = [
    "Backspace", "Delete", "ArrowLeft", "ArrowRight",
    "ArrowUp", "ArrowDown", "Tab", "Home", "End", "Enter"
  ];
  if (allowedKeys.includes(e.key)) return;

  const validPattern = /^[0-9eE.+-]$/;
  if (!validPattern.test(e.key)) {
    e.preventDefault();
  }
}

function validateInput(input) {
  const v = input.value.trim();
  const numRegex = /^[-+]?(\d+(\.\d*)?|\.\d+)([eE][-+]?\d+)?$/;

  if (v === "") {
    input.classList.remove("is-invalid");
    return;
  }

  if (!numRegex.test(v)) {
    input.classList.add("is-invalid");
  } else {
    input.classList.remove("is-invalid");
  }
}

function isEmptyValue(inp) {
  const v = (inp.value || "").trim();
  return v === "";
}

// TRUE si TODA la fila está vacía
function rowIsEmpty(table, rowIdx) {
  const inputs = table.rows[rowIdx].querySelectorAll("input");
  return Array.from(inputs).every(isEmptyValue);
}

function handleKey(e, row, col, table) {
  const rows = table.rows.length;
  const cursorPos = e.target.selectionStart;
  const textLength = e.target.value.length;

  if (
    (e.key === "ArrowLeft" && cursorPos > 0) ||
    (e.key === "ArrowRight" && cursorPos < textLength)
  ) {
    return;
  }

  // LEFT
  if (e.key === "ArrowLeft" && col > 0) {
    e.preventDefault();
    table.rows[row].cells[col - 1].querySelector("input").focus();
    return;
  }

  // RIGHT
  if (e.key === "ArrowRight" && col < FIXED_COLS - 1) {
    e.preventDefault();
    table.rows[row].cells[col + 1].querySelector("input").focus();
    return;
  }

  // UP
  if (e.key === "ArrowUp") {
    e.preventDefault();

    if (row === rows - 1 && rows > MIN_ROWS && rowIsEmpty(table, row)) {
      table.deleteRow(row);
      const newIdx = Math.max(0, row - 1);
      table.rows[newIdx].cells[col].querySelector("input").focus();
      return;
    }

    if (row > 0) {
      table.rows[row - 1].cells[col].querySelector("input").focus();
    }
    return;
  }

  // DOWN
  if (e.key === "ArrowDown") {
    e.preventDefault();

    if (row < rows - 1) {
      table.rows[row + 1].cells[col].querySelector("input").focus();
      return;
    }

    addRow(table);

    setTimeout(() => {
      const newRows = table.rows.length;
      const targetRow = Math.min(newRows - 1, row + 1);
      table.rows[targetRow].cells[col].querySelector("input").focus();
    }, 0);
    return;
  }

  // ENTER → igual que ArrowDown
  if (e.key === "Enter") {
    e.preventDefault();

    if (row < rows - 1) {
      table.rows[row + 1].cells[col].querySelector("input").focus();
      return;
    }

    addRow(table);
    setTimeout(() => {
      const newRows = table.rows.length;
      const targetRow = Math.min(newRows - 1, row + 1);
      table.rows[targetRow].cells[col].querySelector("input").focus();
    }, 0);
    return;
  }
}

function addRow(table) {
  const tr = document.createElement("tr");
  for (let j = 0; j < FIXED_COLS; j++) {
    tr.appendChild(createCellElement(table));
  }
  table.appendChild(tr);
}

function getPointsValues(containerId) {
  const container = document.getElementById(containerId);
  if (!container) return { x: [], y: [] };

  const rows = Array.from(container.querySelectorAll("tr"));
  const xs = [];
  const ys = [];

  rows.forEach((row) => {
    const inputs = row.querySelectorAll("input");
    if (inputs.length < 2) return;

    const xStr = inputs[0].value.trim();
    const yStr = inputs[1].value.trim();

    if (xStr === "" && yStr === "") return;

    const xv = xStr === "" ? NaN : Number(xStr);
    const yv = yStr === "" ? NaN : Number(yStr);

    xs.push(xv);
    ys.push(yv);
  });

  return { x: xs, y: ys };
}

document.addEventListener("DOMContentLoaded", () => {
  createPointsGrid("pointsGrid", 3);
});
