
//Referencias
const mathField = document.getElementById('function');
const toggle = document.getElementById('toggle-mathfield');
const secondToggle = document.getElementById('toggle-second-mathfield');
const derivateField = document.getElementById('derivateField');
const secondDerivateField = document.getElementById('secondDerivateField');
const derivateInput = document.getElementById('derivateInput');
const secondDerivateInput = document.getElementById('secondDerivateInput');
const x0input = document.getElementById("x0")
const nmax = document.getElementById("nmax")
const tol = document.getElementById("tol")
const nrows = document.getElementById("nrows")

function pythonPowToJS(expr) {
    return expr.replace(/\*\*/g, "^");
}

function getFormValues() {
    const x0Value = parseFloat(x0input.value) || 0;
    const nmaxValue = parseInt(nmax.value) || 100;
    const tolValue = parseFloat(tol.value) || 0.0000001;
    const nrowsValue = parseInt(nrows.value) || 30;

    return {
        function: mathField.value || "e^{-x}+\\sin x",
        derivatedFunction: derivateInput.value,
        secondDerivate: secondDerivateInput.value,
        x0: x0Value,
        Nmax: nmaxValue,
        tol: tolValue,
        nrows: nrowsValue
    };
}

const graficar = (data, raiz = NaN) => {

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

defaultData = [
    {
        fn: "exp(-x)+sin(x)"
    },
    {
        fn: "-exp(-x)+cos(x)"
    },
    {
        fn: "exp(-x)-sin(x)",
        title: 'f(x) = x^2'
    },
]

graficar(defaultData)

//Logica para ocultar el math field de la derivada
toggle.addEventListener('change', function () {
    derivateField.style.display = this.checked ? 'block' : 'none';
});

//Logica para ocultar el math field de la derivada
secondToggle.addEventListener('change', function () {
    secondDerivateField.style.display = this.checked ? 'block' : 'none';
});

//Logic for get the table and results
document.getElementById("calculation-btn").addEventListener("click", (event) => {

    // Get validated form values

    const formValues = getFormValues();

    console.log("Sending data:", formValues); // Debug log

    fetch('/eval/modified_newton', {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: new URLSearchParams({
            function: formValues.function,
            x0: formValues.x0,
            Nmax: formValues.Nmax,
            tol: formValues.tol,
            nrows: formValues.nrows,
            ...(formValues.derivatedFunction ? { df: formValues.derivatedFunction } : {}),
            ...(formValues.secondDerivate ? { d2f: formValues.secondDerivate } : {}),
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
        tbody.innerHTML = "";

        for (let i = 0; i < data.historial.iteraciones.length; i++) {
            const row = `
                        <tr>
                            <td>${data.historial.iteraciones[i]}</td>
                            <td>${data.historial.x[i].toFixed(6)}</td>
                            <td>${data.historial.denominadores[i].toExponential(2)}</td>
                            <td>${data.historial.errorAbs[i].toExponential(2)}</td>
                        </tr>
                    `;
            tbody.insertAdjacentHTML("beforeend", row);
        }

        if (data.historial.x[data.historial.x.length - 1]) {
            lastX = data.historial.x[data.historial.x.length - 1]
        } else {
            lastX = 100000000000000
        }


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
        alert('Error en el cálculo. Revisa los valores ingresados.');
    });
})