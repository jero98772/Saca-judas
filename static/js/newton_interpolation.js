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

    fetch('/eval/newton_interpolant', {
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
            // Mostrar forma de Newton
            document.getElementById('newton-form-result').style.display = 'block';
            document.getElementById('newton-form').textContent = data.polynomial_newton;

            // Parsear y graficar el polinomio
            const polyJS = pythonPowToJS(data.symbolic_expression);
            
            const graphData = [
                {
                    fn: polyJS,
                    color: '#007bff'
                },
                {
                    points: points.x.map((xi, i) => [xi, points.y[i]]),
                    fnType: 'points',
                    graphType: 'scatter',
                    color: '#dc3545',
                    attr: { r: 6 }
                }
            ];
            
            graficar(graphData);
        } else {
            // Ocultar resultados si hay error
            document.getElementById('newton-form-result').style.display = 'none';
            
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
        document.getElementById('newton-form-result').style.display = 'none';
    });
});