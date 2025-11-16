const MIN_SIZE = 3;

// ===================== HISTORIAL DE MATRICES =====================
const MATRIX_HISTORY_KEY = "matrix_history";
const MAX_HISTORY_ITEMS = 10;

function saveMatrixToHistory() {
  const A = getMatrixValues("matrixA");
  const b = getVectorValues("matrixB");
  const x0 = getVectorValues("matrixX");

  const timestamp = new Date().toLocaleString();
  const historyItem = {
    id: Date.now(),
    timestamp,
    matrixA: A,
    vectorB: b,
    vectorX: x0
  };

  let history = JSON.parse(localStorage.getItem(MATRIX_HISTORY_KEY) || "[]");
  history.unshift(historyItem);

  // Mantener solo los últimos MAX_HISTORY_ITEMS
  if (history.length > MAX_HISTORY_ITEMS) {
    history = history.slice(0, MAX_HISTORY_ITEMS);
  }

  localStorage.setItem(MATRIX_HISTORY_KEY, JSON.stringify(history));
  updateHistoryUI();
}

function loadMatrixFromHistory(id) {
  const history = JSON.parse(localStorage.getItem(MATRIX_HISTORY_KEY) || "[]");
  const item = history.find(h => h.id === id);

  if (!item) {
    console.error("Historial no encontrado");
    return;
  }

  // Cargar Matrix A
  const matrixAContainer = document.getElementById("matrixA");
  if (matrixAContainer) {
    createMatrixGrid("matrixA", item.matrixA.length, item.matrixA[0].length);
    const inputs = matrixAContainer.querySelectorAll("input");
    let index = 0;
    item.matrixA.forEach(row => {
      row.forEach(value => {
        if (inputs[index]) {
          inputs[index].value = value;
          inputs[index].setAttribute("data-user", value !== 0 ? "1" : "0");
        }
        index++;
      });
    });
  }

  // Cargar Vector B
  const matrixBContainer = document.getElementById("matrixB");
  if (matrixBContainer) {
    createMatrixGrid("matrixB", item.vectorB.length, 1);
    const inputs = matrixBContainer.querySelectorAll("input");
    item.vectorB.forEach((value, index) => {
      if (inputs[index]) {
        inputs[index].value = value;
        inputs[index].setAttribute("data-user", value !== 0 ? "1" : "0");
      }
    });
  }

  // Cargar Vector X (aproximación inicial)
  const matrixXContainer = document.getElementById("matrixX");
  if (matrixXContainer) {
    createMatrixGrid("matrixX", item.vectorX.length, 1);
    const inputs = matrixXContainer.querySelectorAll("input");
    item.vectorX.forEach((value, index) => {
      if (inputs[index]) {
        inputs[index].value = value;
        inputs[index].setAttribute("data-user", value !== 0 ? "1" : "0");
      }
    });
  }

  // Cerrar modal si existe
  const modal = document.getElementById("historyModal");
  if (modal) {
    const bsModal = bootstrap.Modal.getInstance(modal);
    if (bsModal) bsModal.hide();
  }
}

function deleteHistoryItem(id) {
  let history = JSON.parse(localStorage.getItem(MATRIX_HISTORY_KEY) || "[]");
  history = history.filter(h => h.id !== id);
  localStorage.setItem(MATRIX_HISTORY_KEY, JSON.stringify(history));
  updateHistoryUI();
}

function clearAllHistory() {
  if (confirm("¿Estás seguro de que deseas eliminar todo el historial?")) {
    localStorage.removeItem(MATRIX_HISTORY_KEY);
    updateHistoryUI();
  }
}

function updateHistoryUI() {
  const historyList = document.getElementById("historyList");
  if (!historyList) return;

  const history = JSON.parse(localStorage.getItem(MATRIX_HISTORY_KEY) || "[]");

  if (history.length === 0) {
    historyList.innerHTML = '<p class="text-muted">Sin historial guardado</p>';
    return;
  }

  let html = '<div class="list-group">';
  history.forEach(item => {
    const dims = `${item.matrixA.length}x${item.matrixA[0]?.length || 0}`;
    html += `
      <div class="list-group-item d-flex justify-content-between align-items-center">
        <div>
          <small class="text-muted">${item.timestamp}</small>
          <br>
          <strong>Matriz ${dims}</strong>
        </div>
        <div class="btn-group btn-group-sm">
          <button class="btn btn-success" onclick="loadMatrixFromHistory(${item.id})">
            Cargar
          </button>
          <button class="btn btn-danger" onclick="deleteHistoryItem(${item.id})">
            Eliminar
          </button>
        </div>
      </div>
    `;
  });
  html += '</div>';
  historyList.innerHTML = html;
}

function createHistoryModal() {
  // Verificar si el modal ya existe
  if (document.getElementById("historyModal")) return;

  const modal = document.createElement("div");
  modal.id = "historyModal";
  modal.className = "modal fade";
  modal.innerHTML = `
    <div class="modal-dialog modal-lg">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title">Historial de Matrices</h5>
          <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
        </div>
        <div class="modal-body">
          <div id="historyList"></div>
        </div>
        <div class="modal-footer">
          <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cerrar</button>
          <button type="button" class="btn btn-danger" onclick="clearAllHistory()">Limpiar Todo</button>
        </div>
      </div>
    </div>
  `;

  document.body.appendChild(modal);
  updateHistoryUI();
}

function showHistoryModal() {
  if (!document.getElementById("historyModal")) {
    createHistoryModal();
  }
  const modal = new bootstrap.Modal(document.getElementById("historyModal"));
  modal.show();
}

// ===================== FIN HISTORIAL DE MATRICES =====================
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
    syncVectorX(false);
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
          syncVectorX(true);
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

function syncVectorX(forceTrim = false) {
  const A = document.querySelector("#matrixA table");
  if (!A) return;
  const xContainer = document.getElementById("matrixX");
  if (!xContainer) return;
  const currentRows = A.rows.length;

  let xTable = xContainer.querySelector("table");
  if (!xTable) {
    createMatrixGrid("matrixX", Math.max(currentRows, MIN_SIZE), 1);
    return;
  }

  while (xTable.rows.length < currentRows) addRow(xTable);

  while (xTable.rows.length > currentRows && xTable.rows.length > MIN_SIZE) {
    const lastRow = xTable.rows[xTable.rows.length - 1];
    const anyUser = Array.from(lastRow.querySelectorAll("input")).some(inp => !isEmptyValue(inp));
    if (anyUser) break;
    xTable.deleteRow(xTable.rows.length - 1);
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
  createMatrixGrid("matrixX", 3, 1);

  // Crear botones de historial si no existen
  const calcBtn = document.getElementById("calculation-btn");
  if (calcBtn && calcBtn.parentElement) {
    const historyContainer = document.createElement("div");
    historyContainer.className = "mt-3 d-flex gap-2";
    historyContainer.innerHTML = `
      <button type="button" class="btn btn-info" onclick="showHistoryModal()" title="Ver historial de matrices">
        <i class="fas fa-history"></i> Historial
      </button>
      <button type="button" class="btn btn-success" onclick="saveMatrixToHistory()" title="Guardar matriz actual">
        <i class="fas fa-save"></i> Guardar
      </button>
    `;
    calcBtn.parentElement.appendChild(historyContainer);
  }

  // Inicializar UI del historial
  updateHistoryUI();
});
