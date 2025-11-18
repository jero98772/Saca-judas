function randomColor() {
  return `hsl(${Math.floor(Math.random() * 360)}, 80%, 45%)`;
}

function validatePointsStrict(xArr, yArr, minPoints) {
  if (!Array.isArray(xArr) || !Array.isArray(yArr)) return { ok: false, reason: "Points must be arrays." };
  if (xArr.length !== yArr.length) return { ok: false, reason: "'x' and 'y' must have the same length." };
  if (xArr.length < minPoints) return { ok: false, reason: `At least ${minPoints} points are required.` };


  const xNums = xArr.map(v => Number(v));
  const yNums = yArr.map(v => Number(v));
  for (let i = 0; i < xNums.length; ++i) {
    if (!Number.isFinite(xNums[i])) return { ok: false, reason: `x[${i}] is not a finite number.` };
    if (!Number.isFinite(yNums[i])) return { ok: false, reason: `y[${i}] is not a finite number.` };
  }

  const distinctX = new Set(xNums.map(v => String(v)));
  if (distinctX.size < minPoints) return { ok: false, reason: `At least ${minPoints} distinct x values are required.` };

  return { ok: true, x: xNums, y: yNums };
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
    <strong>interval:</strong> [${interval[0]}, ${interval[1]}]
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
    msg.textContent = "The functionPlot library is not loaded.";
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
    console.error("Render error:", e);
    container.innerHTML = `<div class="text-danger">render error.</div>`;
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



let lastLogs = [];
let xVal = null;


document.addEventListener("DOMContentLoaded", () => {
  const solveBtn = document.getElementById("solve-btn");
  const evalSection = document.getElementById("eval-section");
  const evalBtn = document.getElementById("eval-btn");
  const logsContainer = document.getElementById("logs-container");


  if (!solveBtn) { console.error("#solve-btn was not found"); return; }
  if (!logsContainer) console.warn("#logs-container not found; eval location will be in main.");

  
  if (evalSection) {
    evalSection.style.display = "none";
    
  }

  
  function moveEvalSectionToEndOfTracers() {
    if (!evalSection) return;
    
    const logsCard = logsContainer ? logsContainer.closest(".card") : null;
    if (logsCard) {
      
      if (!logsCard.contains(evalSection)) {
        logsCard.appendChild(evalSection);
      }
    } else {
  
      const content = document.getElementById("content");
      if (content && !content.contains(evalSection)) content.appendChild(evalSection);
    }
  }


  solveBtn.addEventListener("click", async () => {
    clearLogs();
    if (document.getElementById("result-message"))
      document.getElementById("result-message").style.display = "none";

    const pts = (typeof getPointsValues === "function") ? getPointsValues("pointsGrid") : null;
    if (!pts) {
      showMessage("Function getPointsValues doesn't available.", "danger");
      console.error("getPointsValues is not defined.");
      return;
    }
    let { x, y } = pts;


    const v = validatePointsStrict(x, y, 3);
    if (!v.ok) {
      return showMessage(v.reason, "danger");
    }
    x = v.x;
    y = v.y;



    const pairs = x.map((xi, i) => ({ x: xi, y: y[i] }));
    pairs.sort((p1, p2) => p1.x - p2.x);

    for (let i = 1; i < pairs.length; ++i) {
      if (Math.abs(pairs[i].x - pairs[i-1].x) < 1e-14) {
        return showMessage(`Repeated or very close values ​​of X: ${pairs[i].x}. Order or correct the points.`, "danger");
      }
    }

    const x_sorted = pairs.map(p => p.x);
    const y_sorted = pairs.map(p => p.y);


    try {
      console.log("Sending payload (sorted) to the backend:", { x: x_sorted, y: y_sorted });
      const response = await fetch("/eval/cubic_spline", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ x: x_sorted, y: y_sorted })
      });

      let result;
      try {
        result = await response.json();
      } catch (e) {
        console.error("Could not parse JSON from response:", e);
        showMessage("Invalid answer from the server.", "danger");
        return;
      }
      console.log("Answer from the server:", response.status, result);

      if (!response.ok) {
        const err = result && result.error ? result.error : `Server Error (status ${response.status})`;
        return showMessage(err, "danger");
      }

      const logsFromServer = Array.isArray(result.logs) ? result.logs : (Array.isArray(result.data && result.data.logs) ? result.data.logs : null);
      if (!Array.isArray(logsFromServer) || logsFromServer.length === 0) {
        console.warn("Can't find 'logs' valids on the answer:", result);
        return showMessage("The server did not return valid tracers.", "danger");
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
      console.error("Error on fetch /eval/cubic_spline:", err);
      showMessage("Conection error.", "danger");
    }
  });

  /* ---- BOTÓN EVALUAR ---- */
  if (evalBtn) {
    evalBtn.addEventListener("click", () => {
      const resultDiv = document.getElementById("eval-result");
      const input = document.getElementById("eval-x");
      if (!input) {
        if (resultDiv) resultDiv.innerHTML = `<span class="text-danger">Input not found.</span>`;
        return;
      }

      const raw = input.value;
      const xEval = Number(raw);
      if (!raw || isNaN(xEval)) {
        if (resultDiv) resultDiv.innerHTML = `<span class="text-danger">Input a valid number.</span>`;
        return;
      }

      if (!Array.isArray(lastLogs) || lastLogs.length === 0) {
        if (resultDiv) resultDiv.innerHTML = `<span class="text-danger">First you have to calcute the tracers.</span>`;
        return;
      }

      xVal = xEval; // guardar globalmente
      console.log("xVal =", xVal);

      let found = null;
      for (const seg of lastLogs) {
        if (!seg || !Array.isArray(seg.interval)) continue;
        const [x0, x1] = seg.interval.map(Number);
        const xi = Math.min(x0, x1), xf = Math.max(x0, x1);
        if (xEval >= xi - 1e-12 && xEval <= xf + 1e-12) { found = seg; break; }
      }

      if (!found) {
        if (resultDiv) resultDiv.innerHTML = `<span class="text-danger">x=${xEval} it's outside the domain.</span>`;
        console.warn("Evaluation: no tracer was found for x=", xEval, "domains:", lastLogs.map(l=>l.interval));
        return;
      }

      
      const coeff = found.coefficients || {};
      const xi0 = Number(found.interval[0]);
      const dx = xEval - xi0;
      const yEval = Number(coeff.a || 0) + Number(coeff.b || 0)*dx + Number(coeff.c || 0)*(dx*dx) + Number(coeff.d || 0)*(dx*dx*dx);

      if (resultDiv) {
        resultDiv.innerHTML = `
          <div>
            <strong>x inputted:</strong> ${xEval}<br>
            <strong>f(${xEval}) =</strong> ${yEval.toFixed(8)}
            <br><small>Tracer s_${found.segment} on [${found.interval[0]}, ${found.interval[1]}]</small>
          </div>
        `;
      }

      highlightLog(found.segment);
      console.log(`Evaluation: x=${xEval} → y=${yEval} (tracer s_${found.segment})`);
    });
  }

});
