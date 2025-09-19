
//Referencias
const mathField = document.getElementById('function');
const toggle = document.getElementById('toggle-mathfield');
const derivateField = document.getElementById('derivateField');
const derivateFieldLabel = document.getElementById('derivateFieldLabel');
const x0input = document.getElementById("x0")
const nmax = document.getElementById("nmax")
const tol = document.getElementById("tol")
const nrows = document.getElementById("nrows")

function pythonPowToJS(expr) {
  return expr.replace(/\*\*/g, "^");
}

const graficar = (data, raiz = NaN) => {
    functionPlot({
        target: "#graph",
        grid: true,
        width: document.getElementById('graph').offsetWidth,
        height: document.getElementById('graph').offsetHeight,
        data
    });
}

defaultData = [
    {
        fn: "exp(-x)+sin(x)"
    },
    {
        fn: "-exp(-x)+cos(x)"
    }
]

graficar(defaultData)

//Logica para ocultar el math field de la derivada
toggle.addEventListener('change', function () {
    derivateField.style.display = this.checked ? 'block' : 'none';
    derivateFieldLabel.style.display = this.checked ? 'block' : 'none';
});

//Logica de la previsualizacion
document.getElementById("previewButton").addEventListener("click", (event) => {
    let tangent_str

    if (!toggle.checked) {
        fetch('/calculations/derivate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
            body: new URLSearchParams({ function: mathField.value })
        })
            .then(response => response.json())
            .then(data => {

                const df = math.parse(data.result)
                const f = math.parse(pythonPowToJS(mathField.value))

                const a = parseFloat(x0input.value) || 0;

                const substituted = f.transform(function (n) {
                    if (n.isSymbolNode && n.name === "x") {
                        return new math.ConstantNode(a);
                    }
                    return n;
                });

                const substitutedDerivate = df.transform(function (n) {
                    if (n.isSymbolNode && n.name === "x") {
                        return new math.ConstantNode(a);
                    }
                    return n;
                });

                tangent_str = `(${substituted}) + ((${substitutedDerivate})*(x-${a}))`
                tangent_str = pythonPowToJS(tangent_str)

                graphData = [
                    {
                        fn: pythonPowToJS(mathField.value)
                    },
                    {
                        fn: tangent_str
                    }
                ]

                graficar(graphData)
            })
            .catch(error => {
                console.error('Error in preview:', error);
            });
    } else {
        tangent_str = derivateField.value
    }
})



//Logic for get the table and results
document.getElementById("calculation-btn").addEventListener("click", (event) => {
    // Get validated form values
    const formValues = getFormValues();

    console.log("Sending data:", formValues); // Debug log

    fetch('/eval/newton_method', {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: new URLSearchParams({
            function: formValues.function,
            x0: formValues.x0.toString(),
            Nmax: formValues.Nmax.toString(),
            tol: formValues.tol.toString(),
            nrows: formValues.nrows.toString()
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

            const tbody = document.querySelector("#result-table tbody");
            tbody.innerHTML = ""; // limpiar por si acaso

            for (let i = 0; i < data.historial.iteraciones.length; i++) {
                const row = `
                        <tr>
                            <td>${data.historial.iteraciones[i]}</td>
                            <td>${data.historial.x[i].toFixed(6)}</td>
                            <td>${data.historial.errorAbs[i].toExponential(3)}</td>
                        </tr>
                    `;
                tbody.insertAdjacentHTML("beforeend", row);
            }

            lastX = data.historial.x[data.historial.x.length - 1]

            graphData = [
                {
                    fn: mathField.value
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