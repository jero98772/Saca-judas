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
        /*
        const f = math.parse(pythonPowToJS(mathField.value));
        const fcompiled = f.compile();

        const x0 = parseFloat(x0input.value) || 0;
        const deltaX = parseFloat(deltaXinput.value) || 0.5;

        console.log("x0:", x0, "deltaX:", deltaX);

        // Show the search interval visualization
        const searchPoints = [];
        let currentX = x0;
        
        // Generate some search points for visualization
        for (let i = 0; i < 10; i++) {
            try {
                const y = fcompiled.evaluate({ x: currentX });
                searchPoints.push([currentX, y]);
            } catch (e) {
                break;
            }
            currentX += deltaX;
        }

        const graphData = [
            { fn: pythonPowToJS(mathField.value) },
            {
                points: searchPoints,
                fnType: "points",
                graphType: "scatter",
                color: "red",
                attr: { r: 4 }
            }
        ];

        graficar(graphData);*/

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

        // Display the result message
        if (data.message) {
            const messageType = data.message.includes("No valid interval") ? "warning" : 
                              data.message.includes("satisfied") ? "success" : 
                              data.message.includes("Maximum") ? "warning" : "info";
            displayMessage(data.message, messageType);
        }

        // Clear and populate the table
        const tbody = document.querySelector("#result-table tbody");
        tbody.innerHTML = ""; // Clear table first

        // Handle the new response format
        if (data.history && data.history.search_points && data.history.search_points.length > 0) {
            // Limit rows based on nrows parameter
            const maxRows = Math.min(data.history.search_points.length, formValues.nrows);
            const startIndex = Math.max(0, data.history.search_points.length - maxRows);

            for (let i = startIndex; i < data.history.search_points.length; i++) {
                const iteration = data.history.iterations[i] || (i + 1);
                const searchPoint = data.history.search_points[i];
                
                // Extract x value and calculate error
                const xi = searchPoint.x || searchPoint[0]; // Handle both object and array formats
                const errorAbs = i > 0 ? Math.abs(xi - (data.history.search_points[i-1].x || data.history.search_points[i-1][0])) : 0;

                const row = `
                    <tr>
                        <td>${iteration}</td>
                        <td>${xi.toFixed(8)}</td>
                        <td>${errorAbs.toExponential(6)}</td>
                    </tr>
                `;
                tbody.insertAdjacentHTML("beforeend", row);
            }

            // Visualize search points on the graph
            const searchPointsForGraph = data.history.search_points.map(point => {
                const x = point.x || point[0];
                const fx = point.fx || point[1];
                return [x, fx];
            });

            const graphData = [
                { fn: pythonPowToJS(mathField.value) },
                {
                    points: searchPointsForGraph,
                    fnType: "points",
                    graphType: "scatter",
                    color: "red",
                    attr: { r: 4 }
                }
            ];

            // If an interval was found, highlight it
            if (data.interval && data.interval.length === 2) {
                const [a, b] = data.interval;
                
                // Add vertical lines to show the interval
                graphData.push({
                    points: [
                        [a, -1000],
                        [a, 1000]
                    ],
                    fnType: "points",
                    graphType: "polyline",
                    color: "green",
                    attr: { "stroke-width": 2, "stroke-dasharray": "5,5" }
                });

                graphData.push({
                    points: [
                        [b, -1000],
                        [b, 1000]
                    ],
                    fnType: "points",
                    graphType: "polyline",
                    color: "green",
                    attr: { "stroke-width": 2, "stroke-dasharray": "5,5" }
                });

                // Highlight the interval endpoints
                graphData.push({
                    points: [[a, 0], [b, 0]],
                    fnType: "points",
                    graphType: "scatter",
                    color: "green",
                    attr: { r: 6 }
                });
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