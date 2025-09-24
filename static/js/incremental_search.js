//References to DOM elements
const mathField = document.getElementById('function');
const x0input = document.getElementById("x0");
const deltaXinput = document.getElementById("delta_x");
const maxIterInput = document.getElementById("max_iter");
const toleranceInput = document.getElementById("tolerance");
const nrowsInput = document.getElementById("nrows");
const resultMessage = document.getElementById("result-message");

function pythonPowToJS(expr) {
    return expr.replace(/\*\*/g, "^");
}

function getFormValues() {
    const x0Value = parseFloat(x0input.value) || 0;
    const deltaXValue = parseFloat(deltaXinput.value) || 0.5;
    const maxIterValue = parseInt(maxIterInput.value) || 100;
    const toleranceValue = parseFloat(toleranceInput.value) || 0.000001;
    const nrowsValue = parseInt(nrowsInput.value) || 30;

    return {
        function: mathField.value || "exp(-x) + sin(x)",
        x0: x0Value,
        delta_x: deltaXValue,
        max_iter: maxIterValue,
        tolerance: toleranceValue,
        nrows: nrowsValue
    };
}

const graficar = (data) => {
    try {
        functionPlot({
            target: "#graph",
            grid: true,
            width: document.getElementById('graph').offsetWidth,
            height: document.getElementById('graph').offsetHeight,
            data: data || [{ fn: pythonPowToJS(mathField.value) }]
        });
    } catch (error) {
        console.error("Error plotting function:", error);
    }
}

// Initial plot
graficar();

// Preview button functionality
document.getElementById("previewButton").addEventListener("click", (event) => {
    try {
        graficar();
    } catch (error) {
        console.error("Error in preview:", error);
        alert("Error in function preview. Check the function syntax.");
    }
});

// Display result message
function displayMessage(message, type = "info") {
    resultMessage.className = `alert alert-${type}`;
    resultMessage.textContent = message;
    resultMessage.style.display = "block";
}

// Hide result message
function hideMessage() {
    resultMessage.style.display = "none";
}

// Main calculation button functionality
document.getElementById("calculation-btn").addEventListener("click", (event) => {
    hideMessage();
    
    // Get validated form values
    const formValues = getFormValues();

    console.log("Sending data:", formValues); // Debug log

    fetch('/eval/incremental_search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: new URLSearchParams({
            function: formValues.function,
            x0: formValues.x0,
            delta_x: formValues.delta_x,
            max_iter: formValues.max_iter,
            tolerance: formValues.tolerance,
            nrows: formValues.nrows
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

        // Display the result message - now handles multiple intervals
        if (data.message) {
            const messageType = data.intervals && data.intervals.length > 0 ? "success" : 
                              data.message.includes("No valid interval") ? "warning" : 
                              data.message.includes("satisfied") ? "success" : 
                              data.message.includes("Maximum") ? "warning" : "info";
            displayMessage(data.message, messageType);
        }

        // Clear and populate the table
        const tbody = document.querySelector("#result-table tbody");
        tbody.innerHTML = ""; // Clear table first

        // Handle the new response format for multiple intervals
        if (data.history && data.history.search_points && data.history.search_points.length > 0) {
            // Limit rows based on nrows parameter
            const searchPoints = data.history.search_points;
            const maxRows = Math.min(searchPoints.length, formValues.nrows);
            const startIndex = Math.max(0, searchPoints.length - maxRows);

            // Populate table with search history showing intervals found
            for (let i = startIndex; i < searchPoints.length; i++) {
                const [a, b, fa, fb] = searchPoints[i];
                const iteration = i + 1;
                
                // Check if this iteration found an interval (sign change)
                const hasSignChange = fa * fb < 0;
                const intervalText = hasSignChange ? `[${a.toFixed(6)}, ${b.toFixed(6)}]` : "No interval";
                const rowClass = hasSignChange ? "table-success" : "";

                const row = `
                    <tr class="${rowClass}">
                        <td>${iteration}</td>
                        <td>${intervalText}</td>
                        <td>${hasSignChange ? "✓" : "✗"}</td>
                    </tr>
                `;
                tbody.insertAdjacentHTML("beforeend", row);
            }

            // Update table headers to show intervals instead of individual points
            const thead = document.querySelector("#result-table thead tr");
            thead.innerHTML = `
                <th>Iteration</th>
                <th>Interval Found</th>
                <th>Sign Change</th>
            `;

            // Visualize all search points and intervals on the graph
            const searchPointsForGraph = searchPoints.map(point => {
                const [a, b, fa, fb] = point;
                return [a, fa]; // Plot the 'a' points
            });

            const graphData = [
                { fn: pythonPowToJS(mathField.value) },
                {
                    points: searchPointsForGraph,
                    fnType: "points",
                    graphType: "scatter",
                    color: "red",
                    attr: { r: 3 }
                }
            ];

            // Highlight ALL intervals found, not just the first one
            if (data.intervals && data.intervals.length > 0) {
                const colors = ["green", "blue", "orange", "purple", "brown", "cyan", "magenta"];
                
                data.intervals.forEach((interval, index) => {
                    const [a, b] = interval;
                    const color = colors[index % colors.length];
                    
                    // Add vertical lines to show interval boundaries
                    graphData.push({
                        points: [[a, -1000], [a, 1000]],
                        fnType: "points",
                        graphType: "polyline",
                        color: color,
                        attr: { "stroke-width": 3, "stroke-dasharray": "8,4" }
                    });

                    graphData.push({
                        points: [[b, -1000], [b, 1000]],
                        fnType: "points",
                        graphType: "polyline", 
                        color: color,
                        attr: { "stroke-width": 3, "stroke-dasharray": "8,4" }
                    });

                    // Highlight the interval endpoints
                    graphData.push({
                        points: [[a, 0], [b, 0]],
                        fnType: "points",
                        graphType: "scatter",
                        color: color,
                        attr: { r: 6 }
                    });
                });

                // Add a legend-like info to the message
                if (data.intervals.length > 1) {
                    const currentMessage = resultMessage.textContent;
                    displayMessage(`${currentMessage} (Each interval shown in different color)`, 
                                 data.intervals.length > 0 ? "success" : "warning");
                }
            }

            graficar(graphData);

        } else {
            displayMessage("No search points data received", "warning");
        }
    })
    .catch(error => {
        console.error('Error in calculation:', error);
        displayMessage('Error in calculation. Check the input values and function syntax.', 'danger');
    });
});