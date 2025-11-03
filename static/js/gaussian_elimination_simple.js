(function () {
  const btn = document.getElementById("calculation-btn");
  const resultMessage = document.getElementById("result-message");
  const logsDiv = document.getElementById("logs-container");
  const solDiv = document.getElementById("solution-container");
  let inlineStylesInjected = false;

  if (!btn) {
    console.error("Button #calculation-btn not found.");
    return;
  }

  function ensureInlineStyles() {
    if (inlineStylesInjected) return;
    inlineStylesInjected = true;

    const css = `
    /* Estilos inyectados dinámicamente para gauss-table (alta prioridad) */
    #content .gauss-table-wrapper { display:flex; justify-content:center; align-items:flex-start; padding:6px 0; overflow-x:auto; }
    #content table.gauss-table { border-collapse: separate !important; border-spacing: 8px !important; width: auto !important; margin: 0 auto !important; table-layout: auto !important; font-family: "Courier New", monospace; font-size: 0.95rem; color: #0f0f23 !important; }
    #content table.gauss-table th, #content table.gauss-table td { display: table-cell !important; vertical-align: middle !important; white-space: nowrap !important; border: 1px solid #00ff41 !important; background: #ffffff !important; padding: 8px 12px !important; border-radius: 8px !important; box-shadow: 0 0 4px rgba(0,255,65,0.18) !important; color: #0f0f23 !important; }
    #content table.gauss-table thead th { background-color: #00ff41 !important; color: #0f0f23 !important; font-weight: bold !important; padding: 6px 10px !important; border-radius: 6px !important; text-align: center !important; }
    #content table.gauss-table tbody tr:nth-child(even) td { background: #f3fff3 !important; }
    `;

    const style = document.createElement("style");
    style.id = "gauss-inline-styles";
    style.appendChild(document.createTextNode(css));
    document.head.appendChild(style);

    // small delay to ensure rules apply if called very early
    setTimeout(() => {}, 0);
  }

  // Forzar class gauss-table y añadir inline table style backup (border-spacing)
  function ensureGaussTableClass(html) {
    if (!html) return html;
    if (!/<table[\s>]/i.test(html)) return html;

    // Add class and inline style to first <table ...>
    return html.replace(/<table([^>]*)>/i, (match, attr) => {
      let newAttr = attr;

      // add/append class
      if (/class\s*=/i.test(attr)) {
        if (!/gauss-table/i.test(attr)) {
          newAttr = newAttr.replace(/class\s*=\s*["']([^"']*)["']/, (m, cls) => {
            return `class="${(cls + " gauss-table").trim()}"`;
          });
        }
      } else {
        newAttr = ` class="gauss-table" ${newAttr}`;
      }

      // ensure inline style backup contains border-spacing & border-collapse
      if (/style\s*=/i.test(newAttr)) {
        // if a style exists, append our props if missing
        newAttr = newAttr.replace(/style\s*=\s*["']([^"']*)["']/, (m, s) => {
          let styleStr = s;
          if (!/border-spacing/i.test(styleStr)) styleStr += " border-spacing:8px;";
          if (!/border-collapse/i.test(styleStr)) styleStr += " border-collapse:separate;";
          return `style="${styleStr}"`;
        });
      } else {
        newAttr = `${newAttr} style="border-spacing:8px; border-collapse:separate;"`;
      }

      return `<table${newAttr}>`;
    });
  }

  function showMessage(text, type = "success") {
    if (!resultMessage) return;
    resultMessage.className = `alert alert-${type}`;
    resultMessage.textContent = text;
    resultMessage.style.display = "block";
  }
  function hideMessage() { if (resultMessage) resultMessage.style.display = "none"; }

  // Escape básico para step/message
  function escapeHtml(unsafe) {
    if (unsafe === null || unsafe === undefined) return "";
    return String(unsafe).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;").replace(/'/g, "&#039;");
  }

  btn.addEventListener("click", async () => {
    // ensure styles applied once per session
    ensureInlineStyles();

    hideMessage();
    if (logsDiv) logsDiv.innerHTML = "";
    if (solDiv) solDiv.style.display = "none";

    let A, b;
    try {
      A = getMatrixValues("matrixA");
      b = getVectorValues("matrixB");
    } catch (err) {
      console.error("Error leyendo matrices:", err);
      showMessage("Error interno: no se pudo leer las matrices de entrada.", "danger");
      return;
    }

    const decimalsInput = document.getElementById("decimals");
    let decimals = 6;
    if (decimalsInput) {
      decimals = parseInt(decimalsInput.value, 10);
      if (!Number.isInteger(decimals) || decimals < 0) decimals = 6;
    }

    try {
      const resp = await fetch("/eval/gauss_simple", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ A, b, decimals }),
      });

      let data;
      try { data = await resp.json(); } catch (err) {
        console.error("Respuesta inválida del servidor:", err);
        showMessage("Respuesta inválida del servidor.", "danger");
        return;
      }

      if (!resp.ok || data.error) {
        const errMsg = data.error || `HTTP ${resp.status} ${resp.statusText}`;
        showMessage(errMsg, "danger");
        return;
      }

      showMessage("Cálculo realizado correctamente.", "success");

      // RENDER LOGS
      if (Array.isArray(data.logs) && logsDiv) {
        logsDiv.innerHTML = "";
        data.logs.forEach((log, idx) => {
          const card = document.createElement("div");
          card.className = "card mb-3 shadow-sm";

          let matrixHtml = "";
          if (log.matrix) {
            matrixHtml = ensureGaussTableClass(String(log.matrix));
          } else if (log.A || log.b) {
            const prettyA = log.A ? JSON.stringify(log.A, null, 2) : null;
            const prettyB = log.b ? JSON.stringify(log.b, null, 2) : null;
            matrixHtml = `<pre style="white-space:pre-wrap;">${prettyA ? "A = " + prettyA + "\n" : ""}${prettyB ? "b = " + prettyB : ""}</pre>`;
          } else {
            matrixHtml = "<em>No hay matriz disponible en este paso.</em>";
          }

          card.innerHTML = `
            <div class="card-header bg-light"><b>${escapeHtml(log.step || `Step ${idx+1}`)}</b> - ${escapeHtml(log.message || "")}</div>
            <div class="card-body">
              <div class="gauss-table-wrapper">
                ${matrixHtml}
              </div>
            </div>
          `;

          logsDiv.appendChild(card);
        });
      }

      // RENDER SOLUTION
      if (Array.isArray(data.solution) && solDiv) {
        const values = data.solution.map((v) => {
          const num = Number(v);
          return Number.isFinite(num) ? num.toFixed(decimals) : String(v);
        });

        let html = '<div class="solution-grid">';
        values.forEach((val, idx) => {
          html += `
            <div class="sol-box" role="group" aria-label="Solución x${idx+1}">
              <div class="sol-label">x${idx + 1}</div>
              <div class="sol-value">${escapeHtml(val)}</div>
            </div>
          `;
        });
        html += '</div>';

        solDiv.style.display = "block";
        solDiv.innerHTML = html;
      } else if (solDiv) {
        solDiv.style.display = "none";
      }

    } catch (err) {
      console.error("Error en fetch:", err);
      showMessage("Error en la comunicación con el servidor.", "danger");
    }
  });
})();
