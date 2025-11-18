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
    /* Dynamically injected styles for gauss-table (high priority) */
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
  }

  function ensureGaussTableClass(html) {
    if (!html) return html;
    if (!/<table[\s>]/i.test(html)) return html;

    return html.replace(/<table([^>]*)>/i, (match, attr) => {
      let newAttr = attr;

      if (/class\s*=/i.test(attr)) {
        if (!/gauss-table/i.test(attr)) {
          newAttr = newAttr.replace(/class\s*=\s*["']([^"']*)["']/, (m, cls) => {
            return `class="${(cls + " gauss-table").trim()}"`;
          });
        }
      } else {
        newAttr = ` class="gauss-table" ${newAttr}`;
      }

      if (/style\s*=/i.test(newAttr)) {
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

  function escapeHtml(unsafe) {
    if (unsafe === null || unsafe === undefined) return "";
    return String(unsafe).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;").replace(/'/g, "&#039;");
  }

  // --- VALIDATION: reusar el comportamiento que ya tenías (claro y estricto) ---
  function validateMatrixAndVector() {
    const Acontainer = document.getElementById("matrixA");
    const bcontainer = document.getElementById("matrixB");

    if (!Acontainer || !bcontainer) {
      return { valid: false, message: "Internal error: matrix containers not found." };
    }

    const tableA = Acontainer.querySelector("table");
    if (!tableA) return { valid: false, message: "Matrix A is not available." };
    const rowsA = Array.from(tableA.rows);

    for (let i = 0; i < rowsA.length; i++) {
      const inputs = Array.from(rowsA[i].querySelectorAll("input"));
      if (inputs.length === 0) continue;
      const valsStr = inputs.map(inp => (inp.value || "").trim());

      const allEmpty = valsStr.every(s => s === "");
      if (allEmpty) {
        return { valid: false, message: `Row ${i + 1} of matrix A is empty. Please fill in all missing values before running the method.` };
      }

      const numericVals = valsStr.map(s => {
        if (s === "") return NaN;
        const s2 = s.replace(",", ".");
        const n = Number(s2);
        return Number.isFinite(n) ? n : NaN;
      });

      const hasNonZero = numericVals.some(n => !isNaN(n) && n !== 0);
      if (!hasNonZero) {
        return { valid: false, message: `Row ${i + 1} of matrix A contains only zeros or invalid values. Please fill in all missing values before running the method.` };
      }
    }

    const tableB = bcontainer.querySelector("table");
    if (!tableB) return { valid: false, message: "Vector b is not available." };
    const rowsB = Array.from(tableB.rows);
    if (rowsB.length !== rowsA.length) return { valid: false, message: "Vector b does not match the size of matrix A." };

    for (let i = 0; i < rowsB.length; i++) {
      const inp = rowsB[i].querySelector("input");
      const s = inp ? (inp.value || "").trim() : "";
      if (s === "") {
        return { valid: false, message: `Entry b[${i + 1}] is empty. Please fill in all missing values before running the method.` };
      }
      const s2 = s.replace(",", ".");
      const n = Number(s2);
      if (!Number.isFinite(n)) {
        return { valid: false, message: `Entry b[${i + 1}] is not numeric. Please fill in all missing values before running the method.` };
      }
    }

    return { valid: true };
  }

  // --- READ DOM VALUES: devuelve A como [[num,...],...] (Number) ---
  function getMatrixValues(containerId) {
    const container = document.getElementById(containerId);
    if (!container) return [];
    const table = container.querySelector("table");
    if (!table) return [];

    const rows = Array.from(table.rows);
    return rows.map(row => {
      const inputs = Array.from(row.querySelectorAll("input"));
      return inputs.map(inp => {
        const s = (inp.value || "").trim().replace(",", ".");
        return s === "" ? null : Number(s);
      });
    });
  }

  // --- READ VECTOR b: devuelve [num, num, ...] (Number) ---
  function getVectorValues(containerId) {
    const container = document.getElementById(containerId);
    if (!container) return [];
    const table = container.querySelector("table");
    if (!table) return [];

    const rows = Array.from(table.rows);
    return rows.map(row => {
      const inp = row.querySelector("input");
      const s = inp ? (inp.value || "").trim().replace(",", ".") : "";
      return s === "" ? null : Number(s);
    });
  }

  // --- MAIN ---
  btn.addEventListener("click", async () => {
    ensureInlineStyles();

    hideMessage();
    if (logsDiv) logsDiv.innerHTML = "";
    if (solDiv) solDiv.style.display = "none";

    // Validar valores del DOM antes de armar y enviar JSON
    const check = validateMatrixAndVector();
    if (!check.valid) {
      showMessage(check.message, "danger");
      return;
    }

    let A, b;
    try {
      A = getMatrixValues("matrixA");
      b = getVectorValues("matrixB");

      // Convertir nulos a cadenas vacías es peligroso en backend: mejor cortar aquí
      // Verificamos que no existan nulls (celdas vacías) después de parsear
      for (let i = 0; i < A.length; i++) {
        for (let j = 0; j < (A[i] || []).length; j++) {
          if (A[i][j] === null || !Number.isFinite(A[i][j])) {
            showMessage(`Entry A[${i+1}][${j+1}] is empty or invalid.`, "danger");
            return;
          }
        }
      }
      for (let i = 0; i < b.length; i++) {
        if (b[i] === null || !Number.isFinite(b[i])) {
          showMessage(`Entry b[${i+1}] is empty or invalid.`, "danger");
          return;
        }
      }
    } catch (err) {
      console.error("Error reading matrices:", err);
      showMessage("Internal error: unable to read input matrices.", "danger");
      return;
    }

    const decimalsInput = document.getElementById("decimals");
    let decimals = 6;
    if (decimalsInput) {
      decimals = parseInt(decimalsInput.value, 10);
      if (!Number.isInteger(decimals) || decimals < 0) decimals = 6;
    }

    try {
      // Enviar A y b correctamente como listas de números
      const resp = await fetch("/eval/gauss_total", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ A, b, decimals }),
      });

      let data;
      try {
        data = await resp.json();
      } catch (err) {
        console.error("Invalid server response:", err);
        showMessage("Invalid response from server.", "danger");
        return;
      }

      if (!resp.ok || data.error) {
        const errMsg = data.error || `HTTP ${resp.status} ${resp.statusText}`;
        showMessage(errMsg, "danger");
        return;
      }
      console.log(data)
      showMessage("Computation completed successfully.", "success");

      // Render logs igual que gauss_simple
      if (Array.isArray(data.logs) && logsDiv) {
        logsDiv.innerHTML = "";
        data.logs.forEach((log, idx) => {
          const card = document.createElement("div");
          card.className = "card mb-3 shadow-sm";

          let matrixHtml = "";
          if (log.matrix) {
            matrixHtml = ensureGaussTableClass(String(log.matrix));
          } else if (log.matrix_html) {
            matrixHtml = ensureGaussTableClass(String(log.matrix_html));
          } else if (log.A || log.b) {
            const prettyA = log.A ? JSON.stringify(log.A, null, 2) : null;
            const prettyB = log.b ? JSON.stringify(log.b, null, 2) : null;
            matrixHtml = `<pre style="white-space:pre-wrap;">${prettyA ? "A = " + prettyA + "\n" : ""}${prettyB ? "b = " + prettyB : ""}</pre>`;
          } else {
            matrixHtml = "<em>No matrix available for this step.</em>";
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

      if (Array.isArray(data.solution) && solDiv) {
        const values = data.solution.map((v) => {
          const num = Number(v);
          return Number.isFinite(num) ? num.toFixed(decimals) : String(v);
        });

        let html = '<div class="solution-grid">';
        values.forEach((val, idx) => {
          html += `
            <div class="sol-box" role="group" aria-label="Solution x${idx+1}">
              <div class="sol-label">x<sub>${idx + 1}</sub></div>
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
      console.error("Fetch error:", err);
      showMessage("Communication error with server.", "danger");
    }
  });
})();
