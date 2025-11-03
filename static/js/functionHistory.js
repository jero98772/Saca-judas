const input = document.getElementById("function");
const dropdown = document.getElementById("function-history");


const HISTORIAL_KEY = "function_history";
let historial = JSON.parse(localStorage.getItem(HISTORIAL_KEY) || "[]");

function actualizarDropdown() {
    dropdown.innerHTML = "";
    if (historial.length === 0) {
        const li = document.createElement("li");
        li.className = "dropdown-item text-muted";
        li.textContent = "(Sin historial)";
        dropdown.appendChild(li);
        return;
    }
    historial.forEach(valor => {
        const li = document.createElement("li");
        li.className = "dropdown-item";
        li.textContent = valor;
        li.addEventListener("click", () => {
            input.value = valor;
        });
        dropdown.appendChild(li);
    });
}

function actualizarLocalStorage() {
    const valor = input.value.trim();
    if (!valor) return;

    // Evitar duplicados
    historial = historial.filter(item => item !== valor);
    historial.unshift(valor);

    // Mantener solo los 10 más recientes
    if (historial.length > 5) historial.pop();

    localStorage.setItem(HISTORIAL_KEY, JSON.stringify(historial));
    actualizarDropdown();
}

// Guardar cuando el usuario cambia el input
input.addEventListener("change", () => {
    actualizarLocalStorage()
});

document.getElementById("previewButton").addEventListener("click", () => {
    actualizarLocalStorage()
    actualizarDropdown()
})

document.getElementById("calculation-btn").addEventListener("click", () => {
    actualizarLocalStorage()
    actualizarDropdown()
})


// Cargar historial al inicio
actualizarLocalStorage()
actualizarDropdown();