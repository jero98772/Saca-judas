
//Referencias
const mathField = document.getElementById('function');
const toggle = document.getElementById('toggle-mathfield');
const derivateField = document.getElementById('derivateField');
const derivateInput = document.getElementById('derivateInput');
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

const preview = (derivatedFunction) => {
    const df = math.parse(pythonPowToJS(derivatedFunction))
    const f = math.parse(pythonPowToJS(mathField.value))

    const fCompiled = f.compile();
    const fDerivatedCompiled = df.compile();

    const a = parseFloat(x0input.value) || 0;

    let xIntercept
    if (fDerivatedCompiled.evaluate({ x: a }) != 0) {
        xIntercept = a - fCompiled.evaluate({ x: a }) / fDerivatedCompiled.evaluate({ x: a });
    } else {
        xIntercept = 0
    }



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
        },
        {
            points: [
                [a, fCompiled.evaluate({ x: a })],
                [xIntercept, 0],
            ],
            fnType: 'points',
            graphType: 'scatter',
            attr: { r: 6 }
        }
    ]

    graficar(graphData)
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
                preview(data.result)
            })
            .catch(error => {
                console.error('Error in preview:', error);
            });
    } else {
        preview(derivateInput.value)
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
            x0: formValues.x0,
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