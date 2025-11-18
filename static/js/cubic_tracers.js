// ===============================
// cubic_tracers.js (VERSIÓN CORREGIDA)
// ===============================

console.log("JS cargado correctamente");

const solveBtn = document.getElementById("solve-btn");
const evalBtn = document.getElementById("eval-btn");
const evalSection = document.getElementById("eval-section");
const evalInput = document.getElementById("eval-x");
const evalResult = document.getElementById("eval-result");
const logsContainer = document.getElementById("logs-container");

let lastSplines = null;

// Utilidad clásica del oficio
const showMessage = (text, level = "info") => {
  const msgEl = document.getElementById("result-message");
  msgEl.className = `alert alert-${level}`;
  msgEl.textContent = text;
  msgEl.style.display = "block";
};

// Insertar el evaluador al final de la tarjeta de logs
function moveEvalSectionToEndOfTracers() {
  const logsCard = logsContainer.closest(".card");
  if (!logsCard) return;
  logsCard.appendChild(evalSection);
}

// Evaluar un x usando los splines del backend
function evaluateSplineAt(x, splines) {
  for (const s of splines) {
    const { a, b, c, d, x_i, x_ip1 } = s;

    if (x >= x_i && x <= x_ip1) {
      const t = x - x_i;
      return a + b * t + c * t * t + d * t * t * t;
    }
  }
  return null;
}

// ===============================
// MANEJO DEL BOTÓN "COMPUTE"
// ===============================
solveBtn.addEventListener("click", async () => {
  showMessage("Computing cubic tracers...", "info");
  evalResult.innerHTML = `<span class="text-muted">Introduce un valor y pulsa Evaluar</span>`;
  evalSection.style.display = "none";

  let points = getVectorsFromGrid()
  console.log(points)
  if (!points || points.length < 2) {
    showMessage("Need at least two valid points.", "danger");
    return;
  }

  try {
    const response = await fetch("/eval/cubic_spline", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify( points ),
    });

    if (!response.ok) {
      showMessage("Error en el servidor (status).", "danger");
      return;
    }

    const data = await response.json();
    console.log("Respuesta del servidor:", data);

    if (!data.splines) {
      showMessage("Error: no se recibieron trazadores del servidor.", "danger");
      return;
    }

    points = getPointsFromGrid();

    lastSplines = data.splines;

    // LOGS
    logsContainer.innerHTML = "";
    data.logs?.forEach((line) => {
      const p = document.createElement("p");
      p.textContent = line;
      logsContainer.appendChild(p);
    });

    showMessage("Cubic tracers computed successfully!", "success");

    // === MOSTRAR EVALUADOR (CORREGIDO) ===
    moveEvalSectionToEndOfTracers();

    evalSection.classList.add("d-flex", "align-items-center", "justify-content-center");
    evalSection.style.display = "flex";

    // Desplazar la vista hacia el evaluador
    try {
      evalSection.scrollIntoView({ behavior: "smooth", block: "end" });
    } catch (e) {
      const logsCard = logsContainer.closest(".card");
      if (logsCard) logsCard.scrollIntoView({ behavior: "smooth", block: "end" });
    }

    // Darle foco para que el usuario pueda escribir de inmediato
    evalInput.focus({ preventScroll: true });

  } catch (err) {
    console.error(err);
    showMessage("Unexpected error.", "danger");
  }

  evalSection.style.display = "flex";
});

// ===============================
// MANEJO DEL BOTÓN "EVALUAR"
// ===============================
evalBtn.addEventListener("click", () => {
  if (!lastSplines) {
    showMessage("Compute the tracers first.", "danger");
    return;
  }

  const x = parseFloat(evalInput.value);
  if (isNaN(x)) {
    evalResult.innerHTML = `<span class="text-danger">Valor inválido.</span>`;
    return;
  }

  const y = evaluateSplineAt(x, lastSplines);
  if (y === null) {
    evalResult.innerHTML = `<span class="text-danger">x fuera del dominio.</span>`;
    return;
  }

  evalResult.innerHTML = `
      <span class="fw-bold text-success">
        f(${x.toFixed(4)}) = ${y.toFixed(6)}
      </span>
    `;
});

