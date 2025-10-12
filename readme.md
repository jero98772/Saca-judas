# 🎭 Saca Judas

**Saca Judas** is an AI-powered, web-animated numerical methods app that integrates interactive tools with an intelligent computation backend. It uses a modern client-server architecture and allows calculations through both a web interface and backend services (via MCP and LLMStudio).

---



## 🚀 Run Locally

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Start the application:

```bash
uvicorn main:app --reload
```

---

## 🌐 Features

- 🤖 AI Integration: Connection to `llmstudio` via `mcp` to perform calculations with or without user interface.
- 🧠 Numerical Methods: Wide range of root-finding and matrix algorithms.
- 🖥️ Animated Web Interface: Frontend built with HTML, CSS, JavaScript.
- 🌐 MCP Integration: Micro-computation protocol server included.
- 📄 Report generation using LaTeX.
- 🌍 Multi-language ready (Python, JS, LaTeX, etc).

---

## 📚 Implemented Numerical Methods

- **Binary Conversion**
  - `binary2decimal_float`
  - `decimal2binary_float`

- **Root-Finding Methods**
  - `iterative_sqrt`
  - `newton_method`
  - `incremental_search`
  - `biseccion`
  - `fixed_point`
  - `secante`
  - `multiples_roots`

- **Matrix Decomposition**
  - `LU_gaussian_simple`
  - `LU_parcial_pivot`
  - `crout`
  - `cholesky`
  - `doolittle`

- **Iterative Solvers**
  - `jacobi`
  - `gauss_seidel`
  - `SOR`

- **Curve Fitting & Interpolation**
  - `vandermonde`
  - `lagrange`
  - `lineal_tracers`
  - `cuadratic_tracers`
  - `cubic_tracers`
  - `spline_evaluator`

- **Gaussian Elimination**
  - `gaussian_elimination_simple`
  - `gaussian_elimination_with_pivot_partial`
  - `gaussian_elimination_with_pivot_total`

- **Other**
  - `formula` (custom numerical formula)

---

## 🔌 Backend Architecture

- `FastAPI` for API services
- `MCP` (Model context protocol) for remote tool execution
- Connection with `llmstudio` for AI-supported calculations

---

## 📊 Future Enhancements

- Additional plotting tools
- Internationalization (i18n) support

---

## 🛠 Tech Stack

- Python (FastAPI)
- JavaScript (frontend)
- HTML + CSS
- MCP + LLMStudio
- LaTeX

  
## User Manual & Reports
- LaTeX Report (https://es.overleaf.com/read/wxmgvzncvzcy#b5ca60).
- LaTeX User Manual (https://es.overleaf.com/read/gstbxkntfqjd#a5eaaa)
### Jype1 combination

Just compile inside the folder, no make problems pls
