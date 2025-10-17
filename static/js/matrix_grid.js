// static/js/matrix_grid.js

function createMatrixGrid(containerId, rows = 3, cols = 3) {
  const container = document.getElementById(containerId);
  container.innerHTML = "";
  container.classList.add("matrix-table");

  const table = document.createElement("table");
  table.className = "table table-bordered table-sm text-center";

  for (let i = 0; i < rows; i++) {
    const tr = document.createElement("tr");
    for (let j = 0; j < cols; j++) {
      const td = document.createElement("td");
      const input = document.createElement("input");
      input.type = "text";
      input.className = "matrix-input form-control form-control-sm text-center";
      input.value = "0";
      td.appendChild(input);
      tr.appendChild(td);

      // expansión dinámica
      input.addEventListener("keydown", (e) => {
        const isLastRow = i === table.rows.length - 1;
        const isLastCol = j === table.rows[0].cells.length - 1;

        // expandir hacia abajo (y sincronizar vector b)
        if (e.key === "ArrowDown" && isLastRow) {
          addRow(table);
          addColumn(table)
          if (containerId === "matrixA") syncVectorB();
        }

        // expandir hacia la derecha solo si es A (mantener cuadrática)
        if (e.key === "ArrowRight" && isLastCol && containerId === "matrixA") {
          addColumn(table);
          makeSquareMatrix(table);
        }
      });
    }
    table.appendChild(tr);
  }

  container.appendChild(table);
}

function addRow(table) {
  const cols = table.rows[0].cells.length;
  const tr = document.createElement("tr");
  for (let j = 0; j < cols; j++) {
    const td = document.createElement("td");
    const input = document.createElement("input");
    input.type = "text";
    input.className = "matrix-input form-control form-control-sm text-center";
    input.value = "0";
    td.appendChild(input);
    tr.appendChild(td);
  }
  table.appendChild(tr);
}

function addColumn(table) {
  for (let i = 0; i < table.rows.length; i++) {
    const td = document.createElement("td");
    const input = document.createElement("input");
    input.type = "text";
    input.className = "matrix-input form-control form-control-sm text-center";
    input.value = "0";
    td.appendChild(input);
    table.rows[i].appendChild(td);
  }
}

// asegura que A siga siendo cuadrada
function makeSquareMatrix(table) {
  const rows = table.rows.length;
  const cols = table.rows[0].cells.length;
  if (rows < cols) {
    while (table.rows.length < cols) addRow(table);
    syncVectorB();
  } else if (cols < rows) {
    while (table.rows[0].cells.length < rows) addColumn(table);
  }
}

// sincroniza el tamaño de b con el número de filas de A
function syncVectorB() {
  const A = document.querySelector("#matrixA table");
  const bContainer = document.getElementById("matrixB");
  const currentRows = A.rows.length;

  let bTable = bContainer.querySelector("table");
  if (!bTable) {
    createMatrixGrid("matrixB", currentRows, 1);
    return;
  }

  const bRows = bTable.rows.length;
  if (bRows < currentRows) {
    for (let i = bRows; i < currentRows; i++) addRow(bTable);
  }
}

// Obtener valores de A
function getMatrixValues(containerId) {
  const container = document.getElementById(containerId);
  const rows = Array.from(container.querySelectorAll("tr"));
  return rows.map((row) =>
    Array.from(row.querySelectorAll("input")).map((cell) => parseFloat(cell.value) || 0)
  );
}

// Obtener valores de b
function getVectorValues(containerId) {
  const container = document.getElementById(containerId);
  const rows = Array.from(container.querySelectorAll("tr"));
  return rows.map((row) =>
    parseFloat(row.querySelector("input").value) || 0
  );
}

// Inicializar cuadrículas al cargar
document.addEventListener("DOMContentLoaded", () => {
  createMatrixGrid("matrixA", 3, 3);
  createMatrixGrid("matrixB", 3, 1);
});
