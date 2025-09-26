//Referencias
const mathField = document.getElementById('function');
const p0Input = document.getElementById("p0")
const p1Input = document.getElementById("p1")
const p2Input = document.getElementById("p2")
const nmax = document.getElementById("nmax")
const tol = document.getElementById("tol")
const nrows = document.getElementById("nrows")

function pythonPowToJS(expr) {
    return expr.replace(/\*\*/g, "^");
}

function getFormValues() {
    const p0Value = parseFloat(p0Input.value)
    const p1Value = parseFloat(p1Input.value) 
    const p2Value = parseFloat(p2Input.value) 
    const nmaxValue = parseInt(nmax.value) 
    const tolValue = parseFloat(tol.value) 
    const nrowsValue = parseInt(nrows.value) 

    return {
        function: mathField.value || "x**3 - x - 1",
        p0: (isNaN(p0Value) ? 0 : p0Value),
        p1: (isNaN(p1Value) ? 1 : p1Value),
        p2: (isNaN(p2Value) ? 2 : p2Value),
        Nmax: nmaxValue,
        tol: tolValue,
        nrows: nrowsValue
    };
}

function postValidateForm(values) {
    try {
        const f = math.parse(pythonPowToJS(mathField.value))
        const fp0 = f.evaluate({ x: values.p0 });
        const fp1 = f.evaluate({ x: values.p1 });
        const fp2 = f.evaluate({ x: values.p2 });

        // Check if any initial point is already a root
        if (Math.abs(fp0) < 1e-12) {
            return { valid: false, message: `Root found at p0 = ${values.p0}` };
        }

        if (Math.abs(fp1) < 1e-12) {
            return { valid: false, message: `Root found at p1 = ${values.p1}` };
        }

        if (Math.abs(fp2) < 1e-12) {
            return { valid: false, message: `Root found at p2 = ${values.p2}` };
        }

        // Check if all three points are distinct
        if (values.p0 === values.p1 || values.p1 === values.p2 || values.p0 === values.p2) {
            return { valid: false, message: "All three initial points must be distinct" };
        }

        return { valid: true, message: "" };
    } catch (error) {
        return { valid: false, message: "Error evaluating function. Please check your function syntax." };
    }
}

// === VALIDATION FUNCTION ===
function validateForm(values) {
    // Check tolerance positive
    if (values.tol <= 0) {
        return { valid: false, message: "Tolerance must be greater than 0." };
    }

    // Check Nmax positive integer
    if (values.Nmax <= 0 || !Number.isInteger(values.Nmax)) {
        return { valid: false, message: "Maximum iterations (Nmax) must be a positive integer." };
    }

    // Check nrows positive integer
    if (values.nrows <= 0 || !Number.isInteger(values.nrows)) {
        return { valid: false, message: "Last N-rows must be a positive integer." };
    }

    // Check function not empty
    if (!values.function || values.function.trim() === "") {
        return { valid: false, message: "You must provide a valid function." };
    }

    // Check that p0, p1, p2 are valid numbers
    if (isNaN(values.p0) || isNaN(values.p1) || isNaN(values.p2)) {
        return { valid: false, message: "All initial points (p0, p1, p2) must be valid numbers." };
    }

    return { valid: true, message: "" };
}

// === UTILITY: show validation messages ===
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

const graficar = (data, annotations = {}) => {
    functionPlot({
        target: "#graph",
        grid: true,
        width: document.getElementById('graph').offsetWidth,
        height: document.getElementById('graph').offsetHeight,
        data,
        annotations
    });
}

// Initial graph
graficar([
    { fn: "x^3 - x - 1" }
])

document.getElementById("previewButton").addEventListener("click", (event) => {
    const values = getFormValues();
    const validation = validateForm(values);

    if (!validation.valid) {
        showMessage(validation.message);
        return;
    }

    // Clear error message
    showMessage("");

    const graphData = [
        { fn: pythonPowToJS(mathField.value) },
        {
            points: [
                [values.p0, 0],
                [values.p1, 0],
                [values.p2, 0]
            ],
            fnType: "points",
            graphType: "scatter",
            color: "red"
        }
    ];

    const annotations = [
        {
            x: values.p0,
            text: 'p0'
        },
        {
            x: values.p1,
            text: 'p1'
        },
        {
            x: values.p2,
            text: 'p2'
        }
    ]

    graficar(graphData, annotations);

    const postValidation = postValidateForm(values)

    if (!postValidation.valid) {
        showMessage(postValidation.message)
    }
});

// Logic for get the table and results
document.getElementById("calculation-btn").addEventListener("click", (event) => {
    const formValues = getFormValues();
    const validation = validateForm(formValues);

    if (!validation.valid) {
        showMessage(validation.message);
        return;
    }

    const postValidation = postValidateForm(formValues)

    if (!postValidation.valid) {
        showMessage(postValidation.message)
        return;
    }

    // Clear error message
    showMessage("");

    console.log("Sending data:", formValues); // Debug log

    fetch('/eval/muller', {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: new URLSearchParams({
            function: formValues.function,
            p0: formValues.p0,
            p1: formValues.p1,
            p2: formValues.p2,
            nmax: formValues.Nmax,
            tolerance: formValues.tol,
            last_n_rows: formValues.nrows
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

            // Mostrar mensaje que viene del backend
            showMessage(data.message, "success");

            // Limpiar y poblar la tabla
            const tbody = document.querySelector("#result-table tbody");
            tbody.innerHTML = ""; // clear table first

            for (let i = 0; i < data.iterations.length; i++) {
                // Convert root to number if it's a string
                const rootValue = typeof data.roots[i] === 'string' ? parseFloat(data.roots[i]) : data.roots[i];
                
                const row = `
                    <tr>
                        <td>${data.iterations[i]}</td>
                        <td>${rootValue.toFixed(6)}</td>
                        <td>${(math.parse(pythonPowToJS(formValues.function))
                        .compile()
                        .evaluate({ x: rootValue })
                    ).toFixed(6)}</td>
                        <td>${data.errors[i].toExponential(3)}</td>
                    </tr>
                `;
                tbody.insertAdjacentHTML("beforeend", row);
            }
            
            // Última aproximación
            const lastX = typeof data.final_root === 'string' ? parseFloat(data.final_root) : data.final_root;

            const graphData = [
                { fn: pythonPowToJS(mathField.value) },
                {
                    points: [
                        [lastX, -1000],
                        [lastX, 1000]
                    ],
                    fnType: "points",
                    graphType: "polyline",
                    color: "red"
                }
            ];

            graficar(graphData);
        })
        .catch(error => {
            console.error('Error in calculation:', error);
            showMessage("Error in calculation. Please check input values.");
        });
});