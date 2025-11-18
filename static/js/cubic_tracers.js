// ======================================================
// cubic_tracers.js — versión final corregida
// ======================================================

/* -------------------------
   UTILIDADES
------------------------- */

function randomColor() {
  return `hsl(${Math.floor(Math.random() * 360)}, 80%, 45%)`;
}

function clearLogs() {
  const lc = document.getElementById("logs-container");
  if (lc) lc.innerHTML = "";
}

function addLog(entry) {
  const logs = document.getElementById("logs-container");
  if (!logs) return;

  const div = document.createElement("div");
  div.className = "card mb-2 p-2 border";

  if (entry.segment !== undefined) div.dataset.segment = entry.segment;

  const { a, b, c, d } = entry.coefficients || {};
  const interval = entry.interval || [];

  div.innerHTML = `
    <strong>s_${entry.segment}:</strong>
      a=${a}, b=${b}, c=${c}, d=${d}
    <br>
    <strong>intervalo:</strong> [${interval[0]}, ${interval[1]}]
  `;
  logs.appendChild(div);
}

function buildPlotData(xNodes, logs) {
  const data = [];
  if (!Array.isArray(logs)) return data;

  logs.forEach(log => {
    if (!log || !log.coefficients || !Array.isArray(log.interval)) return;

    const { a, b, c, d } = log.coefficients;
    const [xi, xi1] = log.interval;
    const expr = `${Number(a)} + ${Number(b)}*(x - ${Number(xi)}) + ${Number(c)}*(x - ${Number(xi)})^2 + ${Number(d)}*(x - ${Number(xi)})^3`;

    data.push({
      fn: expr,
      color: randomColor(),
      range: [xi, xi1]
    });
  });

  return data;
}

function renderPlot(plotData) {
  const container = document.getElementById("graph-container");
  if (!container) return;

  container.innerHTML = "";

  if (typeof functionPlot !== "function") {
    const msg = document.createElement("div");
    msg.className = "text-warning";
    msg.textContent = "La librería functionPlot no está cargada.";
    container.appendChild(msg);
    return;
  }

  try {
    functionPlot({
      target: "#graph-container",
      width: container.clientWidth,
      height: container.clientHeight,
      grid: true,
      data: plotData,
      xAxis: { label: "X" },
      yAxis: { label: "Y" },
      tip: { xLine: true, yLine: true }
    });
  } catch (e) {
    console.error("Error al renderizar:", e);
    container.innerHTML = `<div class="text-danger">Error al renderizar gráfica.</div>`;
  }
}

function showMessage(msg, level = "info") {
  const div = document.getElementById("result-message");
  if (!div) return console.log(msg);

  div.textContent = msg;
  div.className = `alert alert-${level}`;
  div.style.display = "block";
}

function highlightLog(segmentId) {
  const logs = document.getElementById("logs-container");
  if (!logs) return;

  Array.from(logs.children).forEach(el => {
    if (String(el.dataset.segment) === String(segmentId)) {
      el.classList.add("border-success");
      el.scrollIntoView({ behavior: "smooth", block: "center" });
    } else {
      el.classList.remove("border-success");
    }
  });
}

/* ------------------------------
   VARIABLES DE CONTROL
------------------------------ */

let lastLogs = [];
let xVal = null;     // valor evaluado (global)

/* ------------------------------
   CONTROL PRINCIPAL
------------------------------ */

document.addEventListener("DOMContentLoaded", () => {
  const solveBtn = document.getElementById("solve-btn");
  const evalSection = document.getElementById("eval-section");
  const evalBtn = document.getElementById("eval-btn");
  const logsContainer = document.getElementById("logs-container");

  // defensive checks
  if (!solveBtn) { console.error("No se encontró #solve-btn"); return; }
  if (!logsContainer) console.warn("No se encontró #logs-container; ubicación de eval se hará en el main.");

  // ocultar eval-section al inicio (doble defensa)
  if (evalSection) {
    evalSection.style.display = "none";
    // lo dejamos fuera de su lugar hasta que tengamos logs
  }

  // ---- Helper: mover el evalSection al final del panel de Tracers ----
  function moveEvalSectionToEndOfTracers() {
    if (!evalSection) return;
    // intento ubicar la tarjeta (card) que contiene logs
    const logsCard = logsContainer ? logsContainer.closest(".card") : null;
    if (logsCard) {
      // evitar mover si ya está allí
      if (!logsCard.contains(evalSection)) {
        logsCard.appendChild(evalSection);
      }
    } else {
      // fallback: poner al final del body del contenido
      const content = document.getElementById("content");
      if (content && !content.contains(evalSection)) content.appendChild(evalSection);
    }
  }

  /* ---- BOTÓN CALCULAR TRAZADORES ---- */
  solveBtn.addEventListener("click", async () => {
    clearLogs();
    if (document.getElementById("result-message"))
      document.getElementById("result-message").style.display = "none";

    // Obtener puntos del grid
    const pts = (typeof getPointsValues === "function") ? getPointsValues("pointsGrid") : null;
    if (!pts) {
      showMessage("Función getPointsValues no disponible.", "danger");
      console.error("getPointsValues no está definida");
      return;
    }
    let { x, y } = pts;

    // Validaciones y normalizaciones: convertir a números finitos
    x = x.map(v => Number(v));
    y = y.map(v => Number(v));
    if (x.length < 2) return showMessage("Debes ingresar al menos dos puntos.", "danger");
    if (x.some(v => !isFinite(v)) || y.some(v => !isFinite(v))) return showMessage("Hay valores inválidos.", "danger");

    // Ordenar por x (crear pares y ordenar) — evita intervalos invertidos y h==0
    const pairs = x.map((xi, i) => ({ x: xi, y: y[i] }));
    pairs.sort((p1, p2) => p1.x - p2.x);

    // Detectar x duplicadas (h == 0)
    for (let i = 1; i < pairs.length; ++i) {
      if (Math.abs(pairs[i].x - pairs[i-1].x) < 1e-14) {
        return showMessage(`Valores de X repetidos o muy cercanos: ${pairs[i].x}. Ordene o corrija los puntos.`, "danger");
      }
    }

    const x_sorted = pairs.map(p => p.x);
    const y_sorted = pairs.map(p => p.y);

    // Envío al backend con puntos ordenados
    try {
      console.log("Enviando payload (ordenado) al backend:", { x: x_sorted, y: y_sorted });
      const response = await fetch("/eval/cubic_spline", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ x: x_sorted, y: y_sorted })
      });

      let result;
      try {
        result = await response.json();
      } catch (e) {
        console.error("No se pudo parsear JSON de la respuesta:", e);
        showMessage("Respuesta inválida del servidor.", "danger");
        return;
      }
      console.log("Respuesta del servidor:", response.status, result);

      if (!response.ok) {
        const err = result && result.error ? result.error : `Error del servidor (status ${response.status})`;
        return showMessage(err, "danger");
      }

      const logsFromServer = Array.isArray(result.logs) ? result.logs : (Array.isArray(result.data && result.data.logs) ? result.data.logs : null);
      if (!Array.isArray(logsFromServer) || logsFromServer.length === 0) {
        console.warn("No se hallaron 'logs' válidos en la respuesta:", result);
        return showMessage("El servidor no devolvió trazadores válidos.", "danger");
      }

      // Guardar logs (ya en orden ascendente según x_sorted)
      lastLogs = logsFromServer;
      console.log("lastLogs guardados:", lastLogs);

      // Mostrar logs y graficar
      lastLogs.forEach(addLog);
      renderPlot(buildPlotData(x_sorted, lastLogs));
      showMessage("Cubic tracers computed successfully.", "success");

      // Mover el apartado de evaluación al final del panel de Tracers y mostrarlo
      moveEvalSectionToEndOfTracers();
      if (evalSection) evalSection.style.display = "flex";
      evalSection.classList.add("d-flex", "align-items-center", "justify-content-center");


    } catch (err) {
      console.error("Error en fetch /eval/cubic_spline:", err);
      showMessage("Error de conexión con el servidor.", "danger");
    }
  });

  /* ---- BOTÓN EVALUAR ---- */
  if (evalBtn) {
    evalBtn.addEventListener("click", () => {
      const resultDiv = document.getElementById("eval-result");
      const input = document.getElementById("eval-x");
      if (!input) {
        if (resultDiv) resultDiv.innerHTML = `<span class="text-danger">Input no encontrado.</span>`;
        return;
      }

      const raw = input.value;
      const xEval = Number(raw);
      if (!raw || isNaN(xEval)) {
        if (resultDiv) resultDiv.innerHTML = `<span class="text-danger">Ingrese un número válido.</span>`;
        return;
      }

      if (!Array.isArray(lastLogs) || lastLogs.length === 0) {
        if (resultDiv) resultDiv.innerHTML = `<span class="text-danger">Primero calcule los trazadores.</span>`;
        return;
      }

      xVal = xEval; // guardar globalmente
      console.log("xVal =", xVal);
      // Buscar segmento: usar min/max para no depender del orden interno (tolerancia)
      let found = null;
      for (const seg of lastLogs) {
        if (!seg || !Array.isArray(seg.interval)) continue;
        const [x0, x1] = seg.interval.map(Number);
        const xi = Math.min(x0, x1), xf = Math.max(x0, x1);
        if (xEval >= xi - 1e-12 && xEval <= xf + 1e-12) { found = seg; break; }
      }

      if (!found) {
        if (resultDiv) resultDiv.innerHTML = `<span class="text-danger">x=${xEval} está fuera del dominio de los trazadores.</span>`;
        console.warn("Evaluación: no se encontró segmento para x=", xEval, "dominios:", lastLogs.map(l=>l.interval));
        return;
      }

      // Para calcular f(x) usamos exactamente el origen (left endpoint) que envió el servidor en found.interval[0]
      const coeff = found.coefficients || {};
      const xi0 = Number(found.interval[0]);
      const dx = xEval - xi0;
      const yEval = Number(coeff.a || 0) + Number(coeff.b || 0)*dx + Number(coeff.c || 0)*(dx*dx) + Number(coeff.d || 0)*(dx*dx*dx);

      if (resultDiv) {
        resultDiv.innerHTML = `
          <div>
            <strong>x ingresado:</strong> ${xEval}<br>
            <strong>f(${xEval}) =</strong> ${yEval.toFixed(8)}
            <br><small>Segmento s_${found.segment} en [${found.interval[0]}, ${found.interval[1]}]</small>
          </div>
        `;
      }

      highlightLog(found.segment);
      console.log(`Evaluación: x=${xEval} → y=${yEval} (segmento s_${found.segment})`);
    });
  }

}); // end DOMContentLoaded
