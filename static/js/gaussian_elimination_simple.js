const Ainput = document.getElementById("A");
const binput = document.getElementById("b");
const decimalsInput = document.getElementById("decimals");


function showMessage(msg, type = "danger") {
    const messageBox = document.getElementById("result-message");
    if (msg) {
        messageBox.style.display = "block";


        messageBox.classList.remove("alert-danger", "alert-success", "alert-info");


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


function getFormValues() {
    let A, b;
    try {
        A = JSON.parse(Ainput.value);
        b = JSON.parse(binput.value);
    } catch (e) {
        alert("Error parsing A or b. Ensure they are valid Python/JSON format.");
        throw e;
    }

    const decimals = parseInt(decimalsInput.value) || 6;

    return {
        A: A,
        b: b,
        decimals: decimals
    };
}


document.getElementById("calculation-btn").addEventListener("click", (event) => {
    const formValues = getFormValues();

    console.log("Sending data:", formValues);

    fetch('/eval/gauss_simple', {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: new URLSearchParams({
            A: JSON.stringify(formValues.A),
            b: JSON.stringify(formValues.b),
            decimals: formValues.decimals
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


            showMessage(data.message || "Process finished", data.solution ? "success" : "danger");


            const logsDiv = document.getElementById("logs-container");
            logsDiv.innerHTML = "<h5>Steps</h5>";

            if (data.logs) {
                data.logs.forEach(log => {
                    logsDiv.innerHTML += `
                        <div class="card mb-2">
                            <div class="card-header"><b>${log.step}</b> - ${log.message || ""}</div>
                            <div class="card-body">
                                <b>Matrix A:</b>
                                <pre>${JSON.stringify(log.A, null, 2)}</pre>
                                <b>Vector b:</b>
                                <pre>${JSON.stringify(log.b, null, 2)}</pre>
                            </div>
                        </div>
                    `;
                });
            }

            const solDiv = document.getElementById("solution-container");
            if (data.solution) {
                solDiv.style.display = "block";
                solDiv.innerHTML = `<pre>${JSON.stringify(data.solution, null, 2)}</pre>`;
            } else {
                solDiv.style.display = "none";
            }
        })
        .catch(error => {
            console.error('Error in calculation:', error);
            alert('Error en el cálculo. Revisa los valores ingresados.');
        });
});
