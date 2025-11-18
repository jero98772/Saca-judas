// Referencias
let pointCount = 0;

function pythonPowToJS(expr) {
    return expr.replace(/\*\*/g, "^");
}

const graficar = (data) => {
    const graph = document.getElementById('graph');
    graph.innerHTML = "";

    functionPlot({
        target: "#graph",
        grid: true,
        width: document.getElementById('graph').offsetWidth,
        height: document.getElementById('graph').offsetHeight,
        data
    });
}

function showMessage(msg, type = "danger") {
    const messageBox = document.getElementById("result-message");
    if (msg) {
        messageBox.style.display = "block";

        // limpiar clases anteriores
        messageBox.classList.remove("alert-danger", "alert-success", "alert-info");

        // aplicar la clase segun el tipo
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

function addPointRow(x = '', y = '') {
    const container = document.getElementById('points-container');
    const row = document.createElement('div');
    row.className = 'point-row';
    row.id = `point-${pointCount}`;

    row.innerHTML = `
        <input type="number" class="form-control point-input x-input" 
               placeholder="x${pointCount}" value="${x}" step="any">
        <input type="number" class="form-control point-input y-input" 
               placeholder="y${pointCount}" value="${y}" step="any">
        <button class="btn-remove-point" onclick="removePoint('point-${pointCount}')" type="button">Remove</button>
    `;

    container.appendChild(row);
    pointCount++;
}

function removePoint(id) {
    const element = document.getElementById(id);
    if (element) {
        element.remove();
    }
}

function getPoints() {
    const rows = document.querySelectorAll('.point-row');
    const x = [];
    const y = [];

    rows.forEach(row => {
        const xVal = parseFloat(row.querySelector('.x-input').value);
        const yVal = parseFloat(row.querySelector('.y-input').value);

        if (!isNaN(xVal) && !isNaN(yVal)) {
            x.push(xVal);
            y.push(yVal);
        }
    });

    return { x, y };
}

// Initialize with 3 default points
addPointRow(0, 0);
addPointRow(1, 1);
addPointRow(2, 4);

// Graficar inicial vacío
graficar([]);

// Add point button
document.getElementById('add-point-btn').addEventListener('click', () => {
    addPointRow();
});

// Calculate button
document.getElementById('calculation-btn').addEventListener('click', (event) => {
    const points = getPoints();

    if (points.x.length < 2) {
        showMessage('Please enter at least 2 points', 'danger');
        return;
    }

    if (points.x.length !== points.y.length) {
        showMessage('X and Y vectors must have the same length', 'danger');
        return;
    }

    console.log('Sending points:', points);

    fetch('/eval/lagrange', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            x: points.x,
            y: points.y
        })
    })
        .then(response => {
            if (!response.ok) {
                return response.json().then(err => {
                    throw new Error(err.error || `HTTP error! status: ${response.status}`);
                });
            }
            return response.json();
        })
        .then(data => {
            console.log('Received data:', data);

            // Mostrar mensaje
            showMessage(data.message, data.status);

            if (data.status === 'success' && data.symbolic_expression) {
                // Mostrar polinomios Li (es un array)
                document.getElementById('lagrange-polys-result').style.display = 'block';
                const polysText = data.polynomial_lagrange.join('\n');
                document.getElementById('lagrange-polys').textContent = polysText;

                // Mostrar combinación
                document.getElementById('lagrange-combination-result').style.display = 'block';
                document.getElementById('lagrange-combination').textContent = data.polynomial_combination;

                // Parsear y graficar el polinomio
                const polyJS = pythonPowToJS(data.symbolic_expression);
                const points = getPoints()

                drawPlot(polyJS, points.x, points.y)
            } else {
                // Ocultar resultados si hay error
                document.getElementById('lagrange-polys-result').style.display = 'none';
                document.getElementById('lagrange-combination-result').style.display = 'none';

                // Solo graficar los puntos
                const graphData = [{
                    points: points.x.map((xi, i) => [xi, points.y[i]]),
                    fnType: 'points',
                    graphType: 'scatter',
                    color: '#dc3545',
                    attr: { r: 6 }
                }];
                graficar(graphData);
            }
        })
        .catch(error => {
            console.error('Calculation error:', error);
            showMessage('Error: ' + error.message, 'danger');

            // Ocultar resultados
            document.getElementById('lagrange-polys-result').style.display = 'none';
            document.getElementById('lagrange-combination-result').style.display = 'none';
        });
});

function drawPlot(polyExpr, xVals, yVals) {
    const plotCard = document.getElementById('plotCard');
    const plotTarget = '#graph';

    if (!window.functionPlot || (!polyExpr && (!xVals || !xVals.length))) {
        // nothing to draw
        plotCard.classList.add('d-none');
        return;
    }

    // pick a reasonable window around the data points
    let minX = Math.min.apply(null, xVals);
    let maxX = Math.max.apply(null, xVals);
    if (!isFinite(minX) || !isFinite(maxX)) {
        minX = -5; maxX = 5;
    }
    let dx = maxX - minX;
    if (dx === 0) dx = 1;
    const xMargin = dx * 0.5;
    const xDomain = [minX - xMargin, maxX + xMargin];

    let minY = Math.min.apply(null, yVals);
    let maxY = Math.max.apply(null, yVals);
    if (!isFinite(minY) || !isFinite(maxY)) {
        minY = -5; maxY = 5;
    }
    let dy = maxY - minY;
    if (dy === 0) dy = 1;
    const yMargin = dy * 0.5;
    const yDomain = [minY - yMargin, maxY + yMargin];

    const dataSeries = [];

    if (polyExpr) {
        dataSeries.push({
            fn: polyExpr,
            sampler: 'builtIn',
            graphType: 'polyline'
        });
    }

    if (xVals && xVals.length) {
        const pts = xVals.map((x, i) => [x, yVals[i]]);
        dataSeries.push({
            fnType: 'points',
            graphType: 'scatter',
            points: pts
        });
    }

    functionPlot({
        target: plotTarget,
        grid: true,
        width: document.getElementById('graph').offsetWidth,
        height: document.getElementById('graph').offsetHeight,
        xAxis: { domain: xDomain },
        yAxis: { domain: yDomain },
        data: dataSeries
    });

    plotCard.classList.remove('d-none');
}