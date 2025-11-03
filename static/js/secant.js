
//Referencias
const mathField = document.getElementById('function');
const x0input = document.getElementById("x0")
const x1input = document.getElementById("x1")
const nmax = document.getElementById("nmax")
const tol = document.getElementById("tol")
const nrows = document.getElementById("nrows")

function pythonPowToJS(expr) {
    return expr.replace(/\*\*/g, "^");
}

function getFormValues() {
    const x0Value = parseFloat(x0input.value) || 1;
    const x1Value = parseFloat(x1input.value) || 2;
    const nmaxValue = parseInt(nmax.value) || 100;
    const tolValue = parseFloat(tol.value) || 0.0001;
    const nrowsValue = parseInt(nrows.value) || 30;

    return {
        function: mathField.value || "exp(-x) + sin(x)",
        x0: x0Value,
        x1: x1Value,
        Nmax: nmaxValue,
        tol: tolValue,
        nrows: nrowsValue
    };
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


graficar()


document.getElementById("previewButton").addEventListener("click", (event) => {

    const f = math.parse(pythonPowToJS(mathField.value));
    const fcompiled = f.compile();

    const x0 = parseFloat(x0input.value) ?? 1;
    const x1 = parseFloat(x1input.value) ?? 2;


    // Evaluar f en los puntos
    const f0 = fcompiled.evaluate({ x: x0 });
    const f1 = fcompiled.evaluate({ x: x1 });

    // Pendiente y recta secante
    const m = (f0 - f1) / (x0 - x1);
    const b = f0 - m * x0;

    const secant_str = `${m}*x+${b}`;
    console.log("Recta secante:", secant_str);

    graphData = [
        { fn: pythonPowToJS(mathField.value) },
        { fn: secant_str },
        {
            points: [
                [x0, f0],
                [x1, f1],
            ],
            fnType: 'points',
            graphType: 'scatter',
            attr: { r: 6 }
        }

    ];

    graficar(graphData);

});



//Logic for get the table and results
document.getElementById("calculation-btn").addEventListener("click", (event) => {


    // Get validated form values

    const formValues = getFormValues();

    console.log("Sending data:", formValues); // Debug log

    fetch('/eval/secant', {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: new URLSearchParams({
            function: formValues.function,
            x0: formValues.x0,
            x1: formValues.x1,
            Nmax: formValues.Nmax,
            tol: formValues.tol,
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

            showMessage(data.message, data.type)

            const tbody = document.querySelector("#result-table tbody");
            tbody.innerHTML = ""; // clear table first

            for (let i = 0; i < data.history.iter.length; i++) {
                const formatError = (num) => {
                    const exp = num.toExponential(2); // ejemplo: "1.23e-8"
                    const [mant, power] = exp.split('e');
                    return `${(parseFloat(mant) * 0.1).toFixed(2)}e${parseInt(power) + 1}`; // "0.12e-8"
                };
                const row = `
                    <tr>
                        <td>${data.history.iter[i]}</td>
                        <td>${data.history.xi[i].toFixed(17)}</td>
                        <td>${formatError(data.history["f(xi)"][i])}</td>
                        <td>${formatError(data.history.E[i])}</td>
                    </tr>
                `;
                tbody.insertAdjacentHTML("beforeend", row);
            }

            // Last approximation
            lastX = data.history.xi[data.history.xi.length - 1]

            graphData = [
                {
                    fn: pythonPowToJS(mathField.value)
                },
                {
                    points: [
                        [lastX, -1000],
                        [lastX, 1000]
                    ],
                    fnType: "points",
                    graphType: "polyline",
                    color: "red"
                }
            ]
            graficar(graphData)
        })

        .catch(error => {
            console.error('Error in calculation:', error);
            showMessage(error,"danger")
        });
})