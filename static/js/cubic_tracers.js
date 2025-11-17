// ======================================================
// cubic_tracers.js
// ======================================================

// Genera colores aleatorios agradables
function randomColor() {
  return `hsl(${Math.floor(Math.random() * 360)}, 80%, 45%)`;
}

// Limpia logs
function clearLogs() {
  const logs = document.getElementById("logs-container");
  logs.innerHTML = "";
}

// Imprime un log en el panel
function addLog(entry) {
  const logs = document.getElementById("logs-container");

  const div = document.createElement("div");
  div.className = "card mb-2 p-2 border";

  const seg = entry.segment;
  const a = entry.coefficients.a;
  const b = entry.coefficients.b;
  const c = entry.coefficients.c;
  const d = entry.coefficients.d;
  const interval = entry.interval;

  div.innerHTML = `
    <strong>s_${seg}:</strong>  
    a=${a}, b=${b}, c=${c}, d=${d}  
    <br>
    <strong>intervalo:</strong> [${interval[0]}, ${interval[1]}]
  `;
  logs.appendChild(div);
}

// Construye trazadores para function-plot
function buildPlotData(xNodes, logs) {
  const data = [];

  logs.forEach(log => {
    const { a, b, c, d } = log.coefficients;
    const [xi, xi1] = log.interval;

    const color = randomColor();

    const expr = `${a} + ${b}*(x - ${xi}) + ${c}*(x - ${xi})^2 + ${d}*(x - ${xi})^3`;

    data.push({
      fn: expr,
      color: color,
      range: [xi, xi1]
    });
  });

  return data;
}

// Renderiza la gráfica con function-plot
function renderPlot(plotData, xNodes) {
  const container = document.getElementById("graph-container");
  container.innerHTML = "";

  functionPlot({
    target: "#graph-container",
    width: container.clientWidth,
    height: container.clientHeight,
    grid: true,
    data: plotData,
    tip: {
      xLine: true,
      yLine: true
    },
    xAxis: { label: "X" },
    yAxis: { label: "Y" }
  });
}

// Manejar el click del botón
document.addEventListener("DOMContentLoaded", () => {

  document.getElementById("solve-btn").addEventListener("click", async () => {

    clearLogs();
    document.getElementById("result-message").style.display = "none";

    const { x, y } = getPointsValues("pointsGrid");

    // Validación
    if (x.length < 2) {
      showMessage("Debes ingresar al menos dos puntos.", "danger");
      return;
    }

    if (x.some(v => Number.isNaN(v)) || y.some(v => Number.isNaN(v))) {
      showMessage("Hay valores inválidos en la tabla.", "danger");
      return;
    }

    // Ensamble datos
    const payload = { x: x, y: y };

    try {
      const response = await fetch("/eval/cubic_spline", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });

      const result = await response.json();

      if (!response.ok) {
        showMessage(result.error || "Hubo un error en el servidor.", "danger");
        return;
      }

      // Logs del servidor (con coeficientes ya listos)
      const logs = result.logs;

      logs.forEach(addLog); // mostrar en panel

      // Preparar para graficar
      const plotData = buildPlotData(x, logs);

      // Mostrar gráfica
      renderPlot(plotData, x);

      showMessage("Cubic tracers computed successfully.", "success");

    } catch (err) {
      showMessage("Error de conexión con el servidor.", "danger");
    }

  });

});


// ======================================================
// Helper para mostrar mensajes
// ======================================================
function showMessage(msg, level) {
  const div = document.getElementById("result-message");
  div.textContent = msg;
  div.className = `alert alert-${level}`;
  div.style.display = "block";
}
