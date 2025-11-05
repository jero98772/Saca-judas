// points_grid.js
// ===============================
// Genera una tabla de dos columnas expandible hacia abajo,
// con validación numérica estricta (incluye notación científica estilo Python)
// ===============================

const MIN_ROWS = 1;
const FIXED_COLS = 2;

function createPointsGrid(containerId, rows = 3) {
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

// ============================
// 🔒 Restringir caracteres permitidos
// ============================
function restrictKey(e) {
  // Permitir navegación y edición básica
  const allowedKeys = [
    "Backspace", "Delete", "ArrowLeft", "ArrowRight",
    "ArrowUp", "ArrowDown", "Tab", "Home", "End", "Enter"
  ];
  if (allowedKeys.includes(e.key)) return;

  // Permitir: dígitos, signos +-, punto ., y e/E para notación científica
  const validPattern = /^[0-9eE.+-]$/;

  if (!validPattern.test(e.key)) {
    e.preventDefault();
  }
}

// ============================
// ✅ Validar formato numérico
// ============================
function validateInput(input) {
  const v = input.value.trim();

  // Acepta números normales y notación científica tipo Python (1e-4, -3E10, etc.)
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

// ============================
// 🧹 Utilidades
// ============================
function isEmptyValue(inp) {
  const v = (inp.value || "").trim();
  if (v === "") return true;
  const n = Number(v);
  return isNaN(n) || n === 0;
}

function rowIsEmpty(table, rowIdx) {
  const inputs = table.rows[rowIdx].querySelectorAll("input");
  return Array.from(inputs).every(isEmptyValue);
}

// ============================
// ⬆️⬇️ Navegación y expansión dinámica
// ============================
function handleKey(e, row, col, table) {
  const rows = table.rows.length;
  const cursorPos = e.target.selectionStart;
  const textLength = e.target.value.length;

  // Evita moverse dentro del texto
  if (
    (e.key === "ArrowLeft" && cursorPos > 0) ||
    (e.key === "ArrowRight" && cursorPos < textLength)
  ) {
    return;
  }

  // Movimiento lateral entre las dos columnas
  if (e.key === "ArrowLeft" && col > 0) {
    e.preventDefault();
    table.rows[row].cells[col - 1].querySelector("input").focus();
    return;
  }

  if (e.key === "ArrowRight" && col < FIXED_COLS - 1) {
    e.preventDefault();
    table.rows[row].cells[col + 1].querySelector("input").focus();
    return;
  }

  // Movimiento vertical con expansión/contracción
  if (e.key === "ArrowUp") {
    e.preventDefault();
    if (row > 0) {
      table.rows[row - 1].cells[col].querySelector("input").focus();
    } else if (rows > MIN_ROWS && rowIsEmpty(table, rows - 1)) {
      table.deleteRow(rows - 1);
      const newIdx = Math.max(0, rows - 2);
      table.rows[newIdx].cells[col].querySelector("input").focus();
    }
    return;
  }

  if (e.key === "ArrowDown") {
    e.preventDefault();
    if (row < rows - 1) {
      table.rows[row + 1].cells[col].querySelector("input").focus();
    } else {
      addRow(table);
      setTimeout(() => {
        table.rows[row + 1].cells[col].querySelector("input").focus();
      }, 0);
    }
    return;
  }
}

// ============================
// ➕ Agregar fila
// ============================
function addRow(table) {
  const tr = document.createElement("tr");
  for (let j = 0; j < FIXED_COLS; j++) {
    tr.appendChild(createCellElement(table));
  }
  table.appendChild(tr);
}

// ============================
// 📤 Obtener valores
// ============================
function getPointsValues(containerId) {
  const container = document.getElementById(containerId);
  const rows = Array.from(container.querySelectorAll("tr"));
  return rows.map((row) =>
    Array.from(row.querySelectorAll("input")).map((cell) => {
      const v = cell.value.trim();
      return v === "" ? 0 : parseFloat(v) || 0;
    })
  );
}

// ============================
// 🚀 Inicialización automática
// ============================
document.addEventListener("DOMContentLoaded", () => {
  createPointsGrid("pointsGrid", 3);
});
