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

  function hideMessage() {
    if (resultMessage) resultMessage.style.display = "none";
  }

  function escapeHtml(unsafe) {
    if (unsafe === null || unsafe === undefined) return "";
    return String(unsafe)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#039;");
  }

  function validateMatrixAndVector() {
    const Acontainer = document.getElementById("matrixA");
    const bcontainer = document.getElementById("matrixB");

    if (!Acontainer || !bcontainer)
      return { valid: false, message: "Internal error: matrix containers not found." };

    const tableA = Acontainer.querySelector("table");
    if (!tableA) return { valid: false, message: "Matrix A is not available." };
    const rowsA = Array.from(tableA.rows);

    for (let i = 0; i < rowsA.length; i++) {
      const inputs = Array.from(rowsA[i].querySelectorAll("input"));
      if (inputs.length === 0) continue;
      const valsStr = inputs.map(inp => (inp.value || "").trim());

      if (valsStr.every(s => s === "")) {
        return { valid: false, message: `Row ${i + 1} of matrix A is empty.` };
      }

      const numericVals = valsStr.map(s => {
        const s2 = s.replace(",", ".");
        const n = Number(s2);
        return Number.isFinite(n) ? n : NaN;
      });

      const hasValid = numericVals.some(n => !isNaN(n) && n !== 0);
      if (!hasValid) {
        return { valid: false, message: `Row ${i + 1} of matrix A contains only zeros or invalid values.` };
      }
    }

    const tableB = bcontainer.querySelector("table");
    if (!tableB) return { valid: false, message: "Vector b is not available." };
    const rowsB = Array.from(tableB.rows);
    if (rowsB.length !== rowsA.length)
      return { valid: false, message: "Vector b does not match matrix A size." };

    for (let i = 0; i < rowsB.length; i++) {
      const inp = rowsB[i].querySelector("input");
      const s = inp ? (inp.value || "").trim() : "";
      if (s === "") return { valid: false, message: `Entry b[${i + 1}] is empty.` };
      const s2 = s.replace(",", ".");
      if (!Number.isFinite(Number(s2))) return { valid: false, message: `Entry b[${i + 1}] is not numeric.` };
    }

    return { valid: true };
  }

  function getMatrixValues(containerId) {
    const container = document.getElementById(containerId);
    if (!container) return [];
    const table = container.querySelector("table");
    if (!table) return [];

    return Array.from(table.rows).map(row =>
      Array.from(row.querySelectorAll("input")).map(inp => {
        const s = (inp.value || "").trim().replace(",", ".");
        return s === "" ? null : Number(s);
      })
    );
  }

  function getVectorValues(containerId) {
    const container = document.getElementById(containerId);
    if (!container) return [];
    const table = container.querySelector("table");
    if (!table) return [];

    return Array.from(table.rows).map(row => {
      const inp = row.querySelector("input");
      const s = inp ? (inp.value || "").trim().replace(",", ".") : "";
      return s === "" ? null : Number(s);
    });
  }

  btn.addEventListener("click", async () => {
    ensureInlineStyles();
    hideMessage();

    if (logsDiv) logsDiv.innerHTML = "";
    if (solDiv) solDiv.style.display = "none";

    const check = validateMatrixAndVector();
    if (!check.valid) {
      showMessage(check.message, "danger");
      return;
    }

    let A, b;
    try {
      A = getMatrixValues("matrixA");
      b = getVectorValues("matrixB");

      for (let i = 0; i < A.length; i++) {
        for (let j = 0; j < A[i].length; j++) {
          if (A[i][j] === null || !Number.isFinite(A[i][j])) {
            showMessage(`Entry A[${i + 1}][${j + 1}] is empty or invalid.`, "danger");
            return;
          }
        }
      }
      for (let i = 0; i < b.length; i++) {
        if (b[i] === null || !Number.isFinite(b[i])) {
          showMessage(`Entry b[${i + 1}] is empty or invalid.`, "danger");
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
      const resp = await fetch("/eval/crout", {
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
      showMessage("Crout decomposition completed successfully.", "success");

      if (Array.isArray(data.logs) && logsDiv) {
        logsDiv.innerHTML = "";
        data.logs.forEach((log, idx) => {
          const card = document.createElement("div");
          card.className = "card mb-3 shadow-sm";

          let matrixL = "";
          let matrixU = "";

          if (log.L_html) {
            matrixL = ensureGaussTableClass(String(log.L_html));
            matrixU = ensureGaussTableClass(String(log.U_html));
            card.innerHTML = `
              <div class="card-header bg-light"><b>${escapeHtml(log.step || `Step ${idx + 1}`)}</b> - ${escapeHtml(log.message || "")}</div>
                <div class="card-body">
                  <div class="row">
                    <div class="col-6">
                      <div class="h5">L</div>
                      <div class="gauss-table-wrapper">${matrixL}</div>
                    </div>
                    <div class="col-6">
                      <div class="h5">U</div>
                      <div class="gauss-table-wrapper">${matrixU}</div>
                    </div>
                  </div>
                </div>
            `;
          } else if (log.L_json) {
            matrixL = ensureGaussTableClass(String(log.L_json));
            matrixU = ensureGaussTableClass(String(log.U_json));
            card.innerHTML = `
              <div class="card-header bg-light"><b>${escapeHtml(log.step || `Step ${idx + 1}`)}</b> - ${escapeHtml(log.message || "")}</div>
                <div class="card-body">
                  <div class="row">
                    <div class="col-6">
                      <div class="h5">L</div>
                      <div class="gauss-table-wrapper">${matrixL}</div>
                    </div>
                    <div class="col-6">
                      <div class="h5">U</div>
                      <div class="gauss-table-wrapper">${matrixU}</div>
                    </div>
                  </div>
                </div>
            `;
          } else if(log.matrix){
              card.innerHTML = `
              <div class="card-header bg-light"><b>${escapeHtml(log.step || `Step ${idx + 1}`)}</b> - ${escapeHtml(log.message || "")}</div>
            `;
          }

          logsDiv.appendChild(card);
        });
      }

      if (Array.isArray(data.solution) && solDiv) {
        const values = data.solution.map(v => {
          const num = Number(v);
          return Number.isFinite(num) ? num.toFixed(decimals) : String(v);
        });

        let html = '<div class="solution-grid">';
        values.forEach((val, idx) => {
          html += `
            <div class="sol-box">
              <div class="sol-label">x${idx + 1}</div>
              <div class="sol-value">${escapeHtml(val)}</div>
            </div>
          `;
        });
        html += "</div>";

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
