// Gaussian Elimination with Total Pivoting - Frontend Handler
const matrixInput = document.getElementById("matrix");

function showMessage(msg, type = "danger") {
    // Create or get message container
    let messageBox = document.getElementById("result-message");
    if (!messageBox) {
        messageBox = document.createElement("div");
        messageBox.id = "result-message";
        messageBox.className = "alert mt-3";
        messageBox.style.display = "none";
        
        // Insert after the form
        const form = document.querySelector("form");
        form.parentNode.insertBefore(messageBox, form.nextSibling);
    }
    
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

function parseMatrix(matrixText) {
    if (!matrixText.trim()) {
        throw new Error("Matrix input is empty");
    }
    
    const lines = matrixText.trim().split('\n');
    const matrix = [];
    
    for (let i = 0; i < lines.length; i++) {
        const line = lines[i].trim();
        if (!line) continue;
        
        // Split by comma or whitespace, filter empty strings
        const values = line.split(/[,\s]+/).filter(val => val.trim() !== '');
        const row = [];
        
        for (const val of values) {
            const num = parseFloat(val.trim());
            if (isNaN(num)) {
                throw new Error(`Invalid number "${val}" in row ${i + 1}`);
            }
            row.push(num);
        }
        
        if (row.length === 0) continue;
        matrix.push(row);
    }
    
    if (matrix.length === 0) {
        throw new Error("No valid rows found in matrix");
    }
    
    // Validate matrix dimensions
    const firstRowLength = matrix[0].length;
    for (let i = 1; i < matrix.length; i++) {
        if (matrix[i].length !== firstRowLength) {
            throw new Error(`Row ${i + 1} has ${matrix[i].length} elements, expected ${firstRowLength}`);
        }
    }
    
    // For augmented matrix, we need n rows and n+1 columns
    if (matrix.length + 1 !== firstRowLength) {
        throw new Error(`For a ${matrix.length}×${matrix.length} system, expected ${matrix.length + 1} columns (including augmented column), got ${firstRowLength}`);
    }
    
    return matrix;
}

function getFormValues() {
    try {
        const matrix = parseMatrix(matrixInput.value);
        return { matrix: matrix };
    } catch (e) {
        showMessage(`Error parsing matrix: ${e.message}`, "danger");
        throw e;
    }
}

function displayResults(data) {
    // Clear previous messages
    showMessage("");
    
    // Create or get results container
    let resultsContainer = document.getElementById("results-container");
    if (!resultsContainer) {
        resultsContainer = document.createElement("div");
        resultsContainer.id = "results-container";
        resultsContainer.className = "col-12 col-lg-8";
        
        // Find the right column or create it
        const rightColumn = document.querySelector(".col-12.col-lg-8");
        if (rightColumn) {
            rightColumn.innerHTML = "";
            rightColumn.appendChild(resultsContainer);
        } else {
            const container = document.querySelector(".row.g-4");
            container.appendChild(resultsContainer);
        }
    }
    
    if (!data || data.error) {
        showMessage(data?.error || "An error occurred during calculation", "danger");
        resultsContainer.innerHTML = "";
        return;
    }
    
    showMessage("Calculation completed successfully!", "success");
    
    let html = '<div class="row g-4">';
    
    // Solution section
    if (data.solution) {
        html += `
            <div class="col-12">
                <div class="panel-white p-3">
                    <h5 class="mb-3">Solution</h5>
                    <div class="row">`;
        
        data.solution.forEach((val, index) => {
            html += `
                        <div class="col-6 col-md-3">
                            <strong>x${index}</strong>: ${parseFloat(val).toFixed(6)}
                        </div>`;
        });
        
        html += `
                    </div>`;
        
        if (data.perm_cols || data.perm_rows) {
            html += `
                    <div class="mt-2 text-muted">
                        <span class="mono">perm_cols = ${JSON.stringify(data.perm_cols || [])}</span>
                        <span class="mono ms-3">perm_rows = ${JSON.stringify(data.perm_rows || [])}</span>
                    </div>`;
        }
        
        html += `
                </div>
            </div>`;
    }
    
    // Stages section
    if (data.stages && data.stages.length > 0) {
        html += `
            <div class="col-12">
                <div class="panel-white p-3">
                    <h5 class="mb-3">Stages</h5>`;
        
        data.stages.forEach(stage => {
            html += `
                    <div class="mb-3">
                        <div class="d-flex align-items-center justify-content-between">
                            <div><strong>${stage.note || 'Step'}</strong> (k=${stage.k || 'N/A'})</div>`;
            
            if (stage.swap && (stage.swap.rows || stage.swap.cols)) {
                html += `
                            <span class="badge bg-success-subtle text-success-emphasis swap-badge">`;
                if (stage.swap.rows) {
                    html += ` rows: ${JSON.stringify(stage.swap.rows)} `;
                }
                if (stage.swap.cols) {
                    if (stage.swap.rows) html += '|';
                    html += ` cols: ${JSON.stringify(stage.swap.cols)} `;
                }
                html += `</span>`;
            }
            
            html += `
                        </div>
                        <div class="table-responsive">
                            <table class="table table-sm table-striped align-middle table-slim mono mb-0">
                                <tbody>`;
            
            if (stage.matrix) {
                stage.matrix.forEach(row => {
                    html += '<tr>';
                    row.forEach(val => {
                        html += `<td>${parseFloat(val).toFixed(6)}</td>`;
                    });
                    html += '</tr>';
                });
            }
            
            html += `
                                </tbody>
                            </table>
                        </div>
                    </div>`;
        });
        
        html += `
                </div>
            </div>`;
    }
    
    html += '</div>';
    resultsContainer.innerHTML = html;
}

// Handle form submission with AJAX
document.addEventListener("DOMContentLoaded", function() {
    const form = document.querySelector("form");
    const submitButton = document.querySelector(".btn-newton");
    const originalButtonText = submitButton.textContent;
    
    form.addEventListener("submit", function(event) {
        event.preventDefault(); // Prevent default form submission
        
        try {
            const formValues = getFormValues();
            
            // Show loading state
            submitButton.textContent = "Computing...";
            submitButton.disabled = true;
            showMessage("Processing...", "info");
            
            // Prepare form data
            const formData = new FormData();
            formData.append('matrix', matrixInput.value);
            
            fetch('/eval/gauss_pivote', {
                method: 'POST',
                headers: {
                    'Accept': 'application/json'
                },
                body: formData
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                console.log("Received data:", data);
                displayResults(data);
            })
            .catch(error => {
                console.error('Error in calculation:', error);
                showMessage(`Error during calculation: ${error.message}`, "danger");
            })
            .finally(() => {
                // Restore button state
                submitButton.textContent = originalButtonText;
                submitButton.disabled = false;
            });
            
        } catch (error) {
            // Error already handled in getFormValues
            submitButton.textContent = originalButtonText;
            submitButton.disabled = false;
        }
    });
});

// Add input validation
matrixInput.addEventListener("input", function() {
    // Clear previous error messages when user starts typing
    const messageBox = document.getElementById("result-message");
    if (messageBox && messageBox.classList.contains("alert-danger")) {
        showMessage("");
    }
});

// Helper function to validate matrix format on blur
matrixInput.addEventListener("blur", function() {
    if (this.value.trim()) {
        try {
            parseMatrix(this.value);
            // If parsing succeeds, show success briefly
            showMessage("Matrix format is valid", "success");
            setTimeout(() => showMessage(""), 2000);
        } catch (error) {
            // Don't show error on blur, wait for submission
        }
    }
});