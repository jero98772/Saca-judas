const MIN_SIZE = 3;

function createMatrixGrid(containerId, rows = 3, cols = 3) {
  const container = document.getElementById(containerId);
  if (!container) return;

  if (containerId === "matrixA") {
    rows = Math.max(rows, MIN_SIZE);
    cols = Math.max(cols, MIN_SIZE);
  } else if (containerId === "matrixB") {
    rows = Math.max(rows, MIN_SIZE);
    cols = Math.max(cols, 1);
  }

  container.innerHTML = "";
  container.classList.add("matrix-table");

  const table = document.createElement("table");
  table.className = "table table-bordered table-sm text-center";

  for (let r = 0; r < rows; r++) {
    const tr = document.createElement("tr");
    for (let c = 0; c < cols; c++) {
      tr.appendChild(createCellElement(table, containerId));
    }
    table.appendChild(tr);
  }

  container.appendChild(table);
}

function createCellElement(table, containerId) {
  const td = document.createElement("td");
  const input = document.createElement("input");
  input.type = "text";
  input.className = "matrix-input form-control form-control-sm text-center";
  input.value = "0";
  input.placeholder = "0";
  input.setAttribute("data-user", "0");

  input.addEventListener("input", () => {
    const v = input.value.trim();
    if (v === "") {
      input.setAttribute("data-user", "0");
    } else {
      input.setAttribute("data-user", "1");
    }

    const vv = input.value.trim();
    if (
      vv !== "" &&
      !/^[-+]?(\d+(\.\d*)?|\.\d+)([eE][-+]?\d+)?$/.test(vv)
    ) {
      input.classList.add("is-invalid");
    } else {
      input.classList.remove("is-invalid");
    }

  });

  input.addEventListener("keydown", (ev) => {
    const row = input.closest("tr").rowIndex;
    const col = input.closest("td").cellIndex;
    handleKey(ev, row, col, table, table.parentElement.id, input);
  });

  td.appendChild(input);
  return td;
}

function isEmptyValue(inp) {
  const v = (inp.value || "").trim();
  if (v === "") return true;
  const n = Number(v);
  return !isNaN(n) && n === 0;
}

function rowIsEmpty(table, rowIdx) {
  const inputs = table.rows[rowIdx].querySelectorAll("input");
  return Array.from(inputs).every(isEmptyValue);
}

function colIsEmpty(table, colIdx) {
  return Array.from(table.rows).every(row => {
    const inp = row.cells[colIdx].querySelector("input");
    return isEmptyValue(inp);
  });
}

function handleKey(e, row, col, table, containerId, inputEl) {
  const rows = table.rows.length;
  const cols = table.rows[0].cells.length;
  const isMatrixA = containerId === "matrixA";

  // === NUEVO: detección de posición del cursor dentro del texto ===
  const cursorPos = inputEl.selectionStart;
  const textLength = inputEl.value.length;

  // Si se mueve dentro del texto, no cambiar de celda
  if (
    (e.key === "ArrowLeft" && cursorPos > 0) ||
    (e.key === "ArrowRight" && cursorPos < textLength)
  ) {
    return;
  }

  // ==============================
  // Navegación entre celdas
  // ==============================

  if (e.key === "ArrowUp" && row > 0 && !(isMatrixA && row === rows - 1)) {
    e.preventDefault();
    table.rows[row - 1].cells[col].querySelector("input").focus();
    return;
  }

  if (e.key === "ArrowDown" && row < rows - 1) {
    e.preventDefault();
    table.rows[row + 1].cells[col].querySelector("input").focus();
    return;
  }

  if (e.key === "ArrowLeft" && col > 0 && !(isMatrixA && col === cols - 1)) {
    e.preventDefault();
    table.rows[row].cells[col - 1].querySelector("input").focus();
    return;
  }

  if (e.key === "ArrowRight" && col < cols - 1) {
    e.preventDefault();
    table.rows[row].cells[col + 1].querySelector("input").focus();
    return;
  }

  if (!["ArrowUp", "ArrowDown", "ArrowLeft", "ArrowRight"].includes(e.key)) return;
  e.preventDefault();

  // ==============================
  // Expansión o reducción dinámica
  // ==============================

  if (isMatrixA && ((e.key === "ArrowRight" && col === cols - 1) || (e.key === "ArrowDown" && row === rows - 1))) {
    addRowAndColumn(table);
    syncVectorB(false);
    setTimeout(() => {
      const targetRow = (e.key === "ArrowDown") ? Math.min(row + 1, table.rows.length - 1) : row;
      const targetCol = (e.key === "ArrowRight") ? Math.min(col + 1, table.rows[0].cells.length - 1) : col;
      table.rows[targetRow].cells[targetCol].querySelector("input").focus();
    }, 0);
    return;
  }

  if (isMatrixA && (e.key === "ArrowLeft" || e.key === "ArrowUp")) {
    const lastRowIdx = rows - 1;
    const lastColIdx = cols - 1;

    setTimeout(() => {
      if (rows > MIN_SIZE && cols > MIN_SIZE && rowIsEmpty(table, lastRowIdx) && colIsEmpty(table, lastColIdx)) {
        if ((e.key === "ArrowLeft" && col === lastColIdx) || (e.key === "ArrowUp" && row === lastRowIdx)) {
          removeRowAndColumn(table);
          syncVectorB(true);
          setTimeout(() => {
            const newRows = table.rows.length;
            const newCols = table.rows[0].cells.length;
            const newRow = Math.max(0, Math.min(row - (e.key === 'ArrowUp' ? 1 : 0), newRows - 1));
            const newCol = Math.max(0, Math.min(col - (e.key === 'ArrowLeft' ? 1 : 0), newCols - 1));
            table.rows[newRow].cells[newCol].querySelector("input").focus();
          }, 0);
          return;
        }
      }

      if (e.key === "ArrowLeft" && col > 0) {
        table.rows[row].cells[col - 1].querySelector("input").focus();
      } else if (e.key === "ArrowUp" && row > 0) {
        table.rows[row - 1].cells[col].querySelector("input").focus();
      }
    }, 0);
    return;
  }

  if (containerId === "matrixB") {
    if (e.key === "ArrowDown" && row === rows - 1) {
      addRow(table);
      setTimeout(() => table.rows[rows].cells[0].querySelector("input").focus(), 0);
      return;
    }
    if (e.key === "ArrowUp" && row === rows - 1) {
      const lastRow = table.rows[rows - 1];
      const anyUser = Array.from(lastRow.querySelectorAll("input")).some(inp => !isEmptyValue(inp));
      if (!anyUser && rows > 1) {
        table.deleteRow(rows - 1);
        setTimeout(() => {
          const tgtRow = Math.min(row - 1, table.rows.length - 1);
          table.rows[tgtRow].cells[0].querySelector("input").focus();
        }, 0);
      } else if (row > 0) {
        table.rows[row - 1].cells[0].querySelector("input").focus();
      }
      return;
    }
  }
}

function addRow(table) {
  const cols = table.rows[0].cells.length;
  const tr = document.createElement("tr");
  for (let j = 0; j < cols; j++) tr.appendChild(createCellElement(table, table.parentElement.id));
  table.appendChild(tr);
}

function addColumn(table) {
  for (let i = 0; i < table.rows.length; i++) {
    table.rows[i].appendChild(createCellElement(table, table.parentElement.id));
  }
}

function addRowAndColumn(table) {
  addRow(table);
  addColumn(table);
}

function removeRowAndColumn(table) {
  if (table.rows.length <= MIN_SIZE || table.rows[0].cells.length <= MIN_SIZE) return;

  table.deleteRow(table.rows.length - 1);
  const cols = table.rows[0].cells.length;
  for (let i = 0; i < table.rows.length; i++) {
    table.rows[i].deleteCell(cols - 1);
  }
}

function syncVectorB(forceTrim = false) {
  const A = document.querySelector("#matrixA table");
  if (!A) return;
  const bContainer = document.getElementById("matrixB");
  if (!bContainer) return;
  const currentRows = A.rows.length;

  let bTable = bContainer.querySelector("table");
  if (!bTable) {
    createMatrixGrid("matrixB", Math.max(currentRows, MIN_SIZE), 1);
    return;
  }

  while (bTable.rows.length < currentRows) addRow(bTable);

  while (bTable.rows.length > currentRows && bTable.rows.length > MIN_SIZE) {
    const lastRow = bTable.rows[bTable.rows.length - 1];
    const anyUser = Array.from(lastRow.querySelectorAll("input")).some(inp => !isEmptyValue(inp));
    if (anyUser) break;
    bTable.deleteRow(bTable.rows.length - 1);
  }
}

function getMatrixValues(containerId) {
  const container = document.getElementById(containerId);
  const rows = Array.from(container.querySelectorAll("tr"));
  return rows.map((row) =>
    Array.from(row.querySelectorAll("input")).map((cell) => {
      const v = cell.value.trim();
      return v === "" ? 0 : parseFloat(v) || 0;
    })
  );
}

function getVectorValues(containerId) {
  const container = document.getElementById(containerId);
  const rows = Array.from(container.querySelectorAll("tr"));
  return rows.map((row) => {
    const inp = row.querySelector("input");
    const v = inp.value.trim();
    return v === "" ? 0 : parseFloat(v) || 0;
  });
}

document.addEventListener("DOMContentLoaded", () => {
  createMatrixGrid("matrixA", 3, 3);
  createMatrixGrid("matrixB", 3, 1);
});
