// static/js/gaussian_elimination_simple.js
document.getElementById("calculation-btn").addEventListener("click", async () => {
  const A = getMatrixValues("matrixA");
  const b = getVectorValues("matrixB");
  const decimals = parseInt(document.getElementById("decimals").value) || 6;

  const resultMessage = document.getElementById("result-message");
  resultMessage.style.display = "none";

  try {
    const response = await fetch("/eval/gauss_simple", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ A, b, decimals }),
    });

    const data = await response.json();

    if (data.error) {
      resultMessage.className = "alert alert-danger";
      resultMessage.textContent = data.error;
      resultMessage.style.display = "block";
      return;
    }

    resultMessage.className = "alert alert-success";
    resultMessage.textContent = "Calculation successful!";
    resultMessage.style.display = "block";

    // Render logs
    const logsDiv = document.getElementById("logs-container");
    logsDiv.innerHTML = "";
    data.logs.forEach((log) => {
      const div = document.createElement("div");
      div.className = "card mb-3";
      div.innerHTML = `
        <div class="card-header"><b>${log.step}</b> - ${log.message}</div>
        <div class="card-body">
          <pre>A = ${JSON.stringify(log.A, null, 2)}</pre>
          <pre>b = ${JSON.stringify(log.b, null, 2)}</pre>
        </div>`;
      logsDiv.appendChild(div);
    });

    // Render solution
    const solDiv = document.getElementById("solution-container");
    if (data.solution) {
      solDiv.style.display = "block";
      solDiv.innerHTML = `
        <h5>Solution:</h5>
        <pre>${JSON.stringify(data.solution, null, 2)}</pre>`;
    }

  } catch (err) {
    resultMessage.className = "alert alert-danger";
    resultMessage.textContent = "Error in calculation.";
    resultMessage.style.display = "block";
  }
});
