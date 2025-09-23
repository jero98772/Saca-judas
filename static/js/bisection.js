
//Referencias
const mathField = document.getElementById('function');
const aInput = document.getElementById("a")
const bInput = document.getElementById("b")
const nmax = document.getElementById("nmax")
const tol = document.getElementById("tol")
const nrows = document.getElementById("nrows")

function pythonPowToJS(expr) {
    return expr.replace(/\*\*/g, "^");
}

function getFormValues() {
    const aValue = parseFloat(aInput.value)
    const bValue = parseFloat(bInput.value) 
    const nmaxValue = parseInt(nmax.value) 
    const tolValue = parseFloat(tol.value) 
    const nrowsValue = parseInt(nrows.value) 

    return {
        function: mathField.value || "exp(-x) + sin(x)",
        a: (isNaN(aValue) ? 1 : aValue),
        b: (isNaN(bValue) ? 2 : bValue),
        Nmax: nmaxValue,
        tol: tolValue,
        nrows: nrowsValue
    };
}


function postValidateForm(values) {

    const f = math.parse(pythonPowToJS(mathField.value))
    const fa = f.evaluate({ x: values.a });
    const fb = f.evaluate({ x: values.b });


    if (fa == 0) {
        return { valid: false, message: `Root found at a = ${values.a}` };
    }

    if (fb == 0) {
        return { valid: false, message: `Root found at a = ${values.b}` };
    }

    //Check if f(a) * f(b) < 0
    if (fa * fb > 0) {
        return { valid: false, message: "The function must change sign in the interval [a, b]" };
    }

    return { valid: true, message: "" };
}

// === VALIDATION FUNCTION ===
function validateForm(values) {

    // Check if a < b
    if (values.a >= values.b) {
        return { valid: false, message: "Left endpoint (a) must be less than right endpoint (b)." };
    }

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

    if (values.a == values.b) {
        return { valid: false, message: `I don't like this interval` };
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



graficar([
    { fn: "exp(-x) + sin(x)" }
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

    const middle = (values.a + values.b) / 2;

    graphData = [
        { fn: pythonPowToJS(mathField.value) },
        {
            points: [
                [middle, -10],
                [middle, 10]
            ],
            fnType: "points",
            graphType: "polyline",
            color: "red"
        }
    ];

    annotations = [
        {
            x: values.a,
            text: 'a'
        },
        {
            x: values.b,
            text: 'b'
        },
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

    fetch('/eval/bisection', {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: new URLSearchParams({
            function: formValues.function,
            a: formValues.a,
            b: formValues.b,
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
                const row = `
                    <tr>
                        <td>${data.iterations[i]}</td>
                        <td>${data.roots[i].toFixed(6)}</td>
                        <td>${(math.parse(pythonPowToJS(formValues.function))
                        .compile()
                        .evaluate({ x: data.roots[i] })
                    ).toFixed(6)}</td>
                        <td>${data.errors[i].toExponential(3)}</td>
                    </tr>
                `;
                tbody.insertAdjacentHTML("beforeend", row);
            }
            // Última aproximación
            const lastX = data.final_root;

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