const btn = document.getElementById("calculation-btn");
const resultMessage = document.getElementById("result-message");
const logsDiv = document.getElementById("logs-container");
const solDiv = document.getElementById("solution-container");
const tol = document.getElementById("tol")
const nmax = document.getElementById("nmax")
const normaBtn = document.getElementById("normaBtn")
const opts = document.querySelectorAll(".dropdown-item")
let norma = "inf"

opts.forEach((opt) => {
    opt.addEventListener('click', () => {
        norma = opt.getAttribute("data-value")
        normaBtn.textContent = `Norm (${opt.innerHTML})`
    })
})


let inlineStylesInjected = false;

function ensureInlineStyles() {
    if (inlineStylesInjected) return;
    inlineStylesInjected = true;

    const css = `
      /* Dynamically injected styles for gauss-table */
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
                newAttr = newAttr.replace(/class\s*=\s*["']([^"']*)["']/, (m, cls) => `class="${(cls + " gauss-table").trim()}"`);
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
    return String(unsafe)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

function getMatrixValues(containerId) {
    const container = document.getElementById(containerId);
    if (!container) {
        return [];
    }

    const celdas = Array.from(container.querySelectorAll("input"))
    let row = []
    let matrix = []

    celdas.forEach((input, index) => {
        row.push(input.value)
        if ((index + 1) % Math.sqrt(celdas.length) === 0) {
            matrix.push(row)
            row = []
        }
    })

    return matrix
}

function getVectorValues(containerId) {
    0
    const container = document.getElementById(containerId);
    if (!container) return [];
    return Array.from(container.querySelectorAll("input")).map(input => input.value);
}

btn.addEventListener("click", async () => {
    ensureInlineStyles();
    hideMessage();
    if (logsDiv) logsDiv.innerHTML = "";
    if (solDiv) solDiv.style.display = "none";

    let A, b, x0;

    try {
        A = getMatrixValues("matrixA");
        b = getVectorValues("matrixB");
        x0 = getVectorValues("matrixX");
        console.log(A)
        console.log(b)
        console.log(x0)
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
    const body = {
        A, b, x0,
        tol: parseFloat(tol.value || '1e-7'),
        nmax: parseInt(nmax.value || '100', 10),
        norma: norma || 'inf',
        decimales: decimals
    };

    try {
        const resp = await fetch("/eval/gauss_seidel", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(body),
        });

        let data;
        try { data = await resp.json(); } catch (err) {
            console.error("Invalid server response:", err);
            showMessage("Invalid response from server.", "danger");
            return;
        }

        if (!resp.ok || data.error) {
            const errMsg = data.error || `HTTP ${resp.status} ${resp.statusText}`;
            showMessage(errMsg, "danger");
            return;
        }

        showMessage("Computation completed successfully.", "success");

        console.log(data)


        if (Array.isArray(data.logs) && logsDiv) {
            logsDiv.innerHTML = "";

            data.logs.forEach((log, idx) => {
                const card = document.createElement("div");
                card.className = "card mb-3 shadow-sm";

                let contentHtml = "";

                Object.keys(log).forEach(key => {
                    if (key === "step") return;
                    if (key === "error") return; // Skip error, será mostrado en el título

                    const value = log[key];

                    // Si es vector o matriz → tabla estilizada
                    if (Array.isArray(value)) {
                        // Verificar si es un vector (array de números) o una matriz (array de arrays)
                        const isVector = !Array.isArray(value[0]);
                        
                        const tableHtml = renderAsTable(value);
                        
                        // No mostrar la etiqueta "x:" para el vector x
                        const displayKey = (key === 'x' || isVector) ? '' : escapeHtml(key);
                        const labelHtml = displayKey ? `<b>${displayKey}:</b>` : '';
                        
                        contentHtml += `
                            <div class="mb-3">
                                ${labelHtml}
                                ${tableHtml}
                            </div>
                        `;
                    }

                    // Texto / números / mensajes
                    else {
                        contentHtml += `
                            <p><b>${escapeHtml(key)}:</b> ${escapeHtml(String(value))}</p>
                        `;
                    }
                });

                // Construir el título con error
                let stepTitle = escapeHtml(log.step || `Step ${idx + 1}`);
                if (log.error) {
                    stepTitle += ` - Error: ${escapeHtml(formatScientificError(log.error))}`;
                }

                // Crear botón de copiar para el título
                const copyBtnInHeader = `<button class="btn btn-sm btn-secundary" onclick="copyIterationToClipboard(${idx})" style="margin-right: 10px;">📋 Copiar</button>`;

                card.innerHTML = `
                    <div class="card-header bg-light d-flex align-items-center justify-content-between">
                        <div style="display: flex; align-items: center;">
                            ${copyBtnInHeader}
                            <b>${stepTitle}</b>
                        </div>
                    </div>
                    <div class="card-body iteration-data-${idx}">
                        ${contentHtml}
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
                // Obtener el error si existe
                
                html += `
            <div class="sol-box" role="group" aria-label="Solution x">
              <div class="sol-label">x<sub>${idx + 1}</sub></div>
              <div class="sol-value">${escapeHtml(val)}</div>
            </div>
          `;
            });
            html += '</div>';

            // Agregar botón de copiar
            const copyBtn = `<button class="btn btn-sm btn-primary mt-3" onclick="copySolutionToClipboard()">📋 Copiar Solución</button>`;

            solDiv.style.display = "block";
            solDiv.innerHTML = html + copyBtn;
        } else if (solDiv) {
            solDiv.style.display = "none";
        }

    } catch (err) {
        console.error("Fetch error:", err);
        showMessage("Communication error with server.", "danger");
    }
});

function renderAsTable(arr) {
    if (!Array.isArray(arr)) return "";

    // Si es vector → convertirlo en matriz 1xN
    const matrix = Array.isArray(arr[0]) ? arr : [arr];

    let html = `
    <div class="gauss-table-wrapper">
    <table class="dataframe gauss-table" style="border-spacing:8px; border-collapse:separate;">
        <thead>
            <tr>
    `;

    html += `
            </tr>
        </thead>
        <tbody>
    `;

    matrix.forEach(row => {
        html += `<tr>`;
        row.forEach(cell => {
            html += `<td>${Number(cell).toFixed(6)}</td>`;
        });
        html += `</tr>`;
    });

    html += `
        </tbody>
    </table>
    </div>`;

    return html;
}

function formatScientificError(value) {
    const num = Number(value);
    if (!Number.isFinite(num)) return String(value);
    
    // Convertir a notación científica con 2 decimales
    return num.toExponential(2);
}

function copyTableToClipboard(button) {
    // Encontrar la tabla más cercana
    const table = button.closest('.mb-3').querySelector('table');
    if (!table) return;

    let text = '';
    const rows = table.querySelectorAll('tr');
    rows.forEach(row => {
        const cells = row.querySelectorAll('td, th');
        const rowText = Array.from(cells).map(cell => cell.textContent.trim()).join('\t');
        text += rowText + '\n';
    });

    navigator.clipboard.writeText(text).then(() => {
        // Cambiar el texto del botón temporalmente
        const originalText = button.textContent;
        button.textContent = '✓ Copiado';
        button.classList.add('btn-success');
        button.classList.remove('btn-primary');
        
        setTimeout(() => {
            button.textContent = originalText;
            button.classList.remove('btn-success');
            button.classList.add('btn-primary');
        }, 2000);
    }).catch(() => {
        alert('Error al copiar al portapapeles');
    });
}

function copyIterationToClipboard(iterationIdx) {
    // Obtener el contenido de la iteración
    const iterationBody = document.querySelector(`.iteration-data-${iterationIdx}`);
    if (!iterationBody) return;

    let text = '';
    
    // Obtener todas las tablas de la iteración
    const tables = iterationBody.querySelectorAll('table');
    tables.forEach((table, tableIdx) => {
        if (tableIdx > 0) text += '\n';
        
        // Obtener la etiqueta de la tabla (si existe)
        const label = table.closest('.mb-3').querySelector('b');
        if (label) text += label.textContent + ':\n';
        
        // Copiar contenido de la tabla
        const rows = table.querySelectorAll('tr');
        rows.forEach(row => {
            const cells = row.querySelectorAll('td, th');
            const rowText = Array.from(cells).map(cell => cell.textContent.trim()).join('\t');
            text += rowText + '\n';
        });
    });

    navigator.clipboard.writeText(text).then(() => {
        // Encontrar el botón en el header y cambiar su estado
        const button = iterationBody.closest('.card').querySelector('.card-header button');
        if (button) {
            const originalText = button.textContent;
            button.textContent = '✓ Copiado';
            button.classList.add('btn-success');
            button.classList.remove('btn-primary');
            
            setTimeout(() => {
                button.textContent = originalText;
                button.classList.remove('btn-success');
                button.classList.add('btn-primary');
            }, 2000);
        }
    }).catch(() => {
        alert('Error al copiar al portapapeles');
    });
}

function copySolutionToClipboard() {
    // Obtener todos los valores de la solución
    const solBoxes = document.querySelectorAll('.sol-box');
    let text = ""
    
    solBoxes.forEach((box) => {

        const value = box.querySelector('.sol-value').textContent.trim();

        text += `${value}\n`;
    });

    navigator.clipboard.writeText(text).then(() => {
        // Cambiar el texto del botón temporalmente
        const button = document.querySelector('#solution-container button');
        if (button) {
            const originalText = button.textContent;
            button.textContent = '✓ Copiado';
            button.classList.add('btn-success');
            button.classList.remove('btn-primary');
            
            setTimeout(() => {
                button.textContent = originalText;
                button.classList.remove('btn-success');
                button.classList.add('btn-primary');
            }, 2000);
        }
    }).catch(() => {
        alert('Error al copiar al portapapeles');
    });
}