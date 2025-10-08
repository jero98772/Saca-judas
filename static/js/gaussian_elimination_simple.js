const Ainput = document.getElementById("A");
const binput = document.getElementById("b");
const decimalsInput = document.getElementById("decimals");

const mathField = document.getElementById("mathfield");

mathField.addEventListener("input", () => {
    console.log(mathField.value)
})



function showMessage(msg, type = "danger") {
    const messageBox = document.getElementById("result-message");
    if (msg) {
        messageBox.style.display = "block";
        messageBox.classList.remove("alert-danger", "alert-success", "alert-info");

        if (type === "success") {
            messageBox.classList.add("alert-success");
        } else if (type === "info") {
            messageBox.classList.add("alert-info");
        } else {
            messageBox.classList.add("alert-danger");
        }

        messageBox.textContent = msg;
    } else {
        messageBox.style.display = "none";
        messageBox.textContent = "";
    }
}

function getFormValues() {
    let A, b;
    try {
        A = JSON.parse(Ainput.value);
        b = JSON.parse(binput.value);
    } catch (e) {
        alert("Error parsing A or b. Ensure they are valid Python/JSON format.");
        throw e;
    }

    const decimals = parseInt(decimalsInput.value) || 6;

    return {
        A: A,
        b: b,
        decimals: decimals
    };
}

// Function to create a formatted matrix display
function formatMatrix(matrix) {
    if (!Array.isArray(matrix) || matrix.length === 0) return '';
    
    // For 1D arrays (vectors)
    if (!Array.isArray(matrix[0])) {
        return `<div class="matrix-container">
            <span class="matrix-bracket">[</span>
            <div class="matrix-column">
                ${matrix.map(val => `<div class="matrix-cell">${val}</div>`).join('')}
            </div>
            <span class="matrix-bracket">]</span>
        </div>`;
    }
    
    // For 2D arrays (matrices)
    return `<div class="matrix-container">
        <span class="matrix-bracket">[</span>
        <div class="matrix-rows">
            ${matrix.map(row => `
                <div class="matrix-row">
                    <span class="row-bracket">[</span>
                    ${row.map(val => `<span class="matrix-cell">${val}</span>`).join('')}
                    <span class="row-bracket">]</span>
                </div>
            `).join('')}
        </div>
        <span class="matrix-bracket">]</span>
    </div>`;
}

// Function to format the solution vector
function formatSolution(solution) {
    if (!Array.isArray(solution)) return '';
    
    return `<div class="solution-container">
        <span class="solution-bracket">[</span>
        <div class="solution-values">
            ${solution.map(val => `<div class="solution-value">${val}</div>`).join('')}
        </div>
        <span class="solution-bracket">]</span>
    </div>`;
}

// Add CSS for matrix formatting
function addMatrixStyles() {
    if (document.getElementById('matrix-styles')) return;
    
    const style = document.createElement('style');
    style.id = 'matrix-styles';
    style.textContent = `
        .matrix-container {
            display: inline-flex;
            align-items: center;
            margin: 10px 0;
            font-family: monospace;
        }
        
        .matrix-bracket {
            font-size: 1.5em;
            font-weight: bold;
            margin: 0 5px;
        }
        
        .matrix-rows {
            display: flex;
            flex-direction: column;
        }
        
        .matrix-row {
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 2px 0;
        }
        
        .row-bracket {
            font-weight: bold;
            margin: 0 5px;
        }
        
        .matrix-column {
            display: flex;
            flex-direction: column;
            align-items: center;
        }
        
        .matrix-cell, .solution-value {
            padding: 2px 8px;
            text-align: center;
            min-width: 40px;
        }
        
        .solution-container {
            display: inline-flex;
            align-items: center;
            margin: 10px 0;
            font-family: monospace;
            font-size: 1.2em;
        }
        
        .solution-bracket {
            font-size: 1.5em;
            font-weight: bold;
            margin: 0 5px;
        }
        
        .solution-values {
            display: flex;
            flex-direction: column;
            align-items: center;
        }
        
        .step-matrix {
            margin: 10px 0;
            padding: 10px;
            background-color: #f8f9fa;
            border-radius: 5px;
        }
        
        .step-title {
            font-weight: bold;
            margin-bottom: 5px;
            color: #007bff;
        }
        
        .matrix-label {
            font-weight: bold;
            margin-right: 10px;
        }
        
        .matrix-display {
            display: flex;
            align-items: flex-start;
            margin: 5px 0;
        }
    `;
    
    document.head.appendChild(style);
}

document.getElementById("calculation-btn").addEventListener("click", (event) => {
    const formValues = getFormValues();
    
    // Add matrix styles if not already added
    addMatrixStyles();

    console.log("Sending data:", formValues);

    fetch('/eval/gauss_simple', {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: new URLSearchParams({
            A: JSON.stringify(formValues.A),
            b: JSON.stringify(formValues.b),
            decimals: formValues.decimals
        })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    })
    .then((data) => {
        console.log("Received data:", data);

        showMessage(data.message || "Process finished", data.solution ? "success" : "danger");

        const logsDiv = document.getElementById("logs-container");
        logsDiv.innerHTML = "<h5>Steps</h5>";

        if (data.logs) {
            data.logs.forEach(log => {
                const stepDiv = document.createElement('div');
                stepDiv.className = 'card mb-3';
                
                stepDiv.innerHTML = `
                    <div class="card-header">
                        <b>${log.step}</b> - ${log.message || ""}
                    </div>
                    <div class="card-body">
                        <div class="step-matrix">
                            <div class="step-title">Matrix A:</div>
                            <div class="matrix-display">
                                <span class="matrix-label">A =</span>
                                ${formatMatrix(log.A)}
                            </div>
                        </div>
                        <div class="step-matrix">
                            <div class="step-title">Vector b:</div>
                            <div class="matrix-display">
                                <span class="matrix-label">b =</span>
                                ${formatMatrix(log.b)}
                            </div>
                        </div>
                    </div>
                `;
                
                logsDiv.appendChild(stepDiv);
            });
        }

        const solDiv = document.getElementById("solution-container");
        if (data.solution) {
            solDiv.style.display = "block";
            solDiv.innerHTML = `
                <h5>Final Solution</h5>
                <div class="matrix-display">
                    <span class="matrix-label">x =</span>
                    ${formatSolution(data.solution)}
                </div>
            `;
        } else {
            solDiv.style.display = "none";
        }
    })
    .catch(error => {
        console.error('Error in calculation:', error);
        alert('Error en el cálculo. Revisa los valores ingresados.');
    });
});