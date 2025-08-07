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
- `MCP` (Micro Computation Protocol) for remote tool execution
- Connection with `llmstudio` for AI-supported calculations

---

## 📊 Future Enhancements

- Additional plotting tools
- More LaTeX-based PDF report exports
- Internationalization (i18n) support

---

## 🛠 Tech Stack

- Python (FastAPI)
- JavaScript (frontend)
- HTML + CSS
- MCP + LLMStudio
- LaTeX
```

---

## 📄 `README.tex` (for LaTeX Reports)

```latex
\documentclass[11pt]{article}
\usepackage{geometry}
\usepackage{amsmath}
\usepackage{graphicx}
\usepackage{hyperref}
\geometry{margin=1in}

\title{Saca Judas}
\author{AI-Powered Numerical Methods Platform}
\date{}

\begin{document}
\maketitle

\section*{Overview}
\textbf{Saca Judas} is an animated, web-based application for performing numerical calculations. It uses artificial intelligence via \texttt{llmstudio} and communicates with a Micro Computation Protocol (\texttt{MCP}) server to handle backend processing.

\section*{Key Features}
\begin{itemize}
  \item Web interface built with HTML, CSS, and JavaScript.
  \item Backend powered by FastAPI and Python.
  \item Connection to LLMStudio for AI-enhanced calculations.
  \item Export of reports using \LaTeX.
  \item Binary-decimal conversions.
  \item Support for advanced matrix decompositions.
\end{itemize}

\section*{Numerical Methods}
Implemented methods include:

\begin{itemize}
  \item \textbf{Root-finding}: Iterative sqrt, Newton's method, bisection, fixed point, secant, multiple roots.
  \item \textbf{LU Decomposition}: Simple, partial pivoting, Crout, Cholesky, Doolittle.
  \item \textbf{Iterative Solvers}: Jacobi, Gauss-Seidel, SOR.
  \item \textbf{Interpolation}: Vandermonde, Lagrange, linear/quadratic/cubic tracers, spline evaluation.
  \item \textbf{Binary Conversion}: Decimal to binary float and vice versa.
  \item \textbf{Gaussian Elimination}: With/without pivoting.
\end{itemize}

\section*{How to Run}
\begin{verbatim}
pip install -r requirements.txt
uvicorn main:app --reload
\end{verbatim}

\section*{Architecture}
\begin{itemize}
  \item FastAPI for RESTful services.
  \item MCP server for modular computation.
  \item Optional LLMStudio connection for enhanced logic.
\end{itemize}

\section*{Future Work}
\begin{itemize}
  \item Add visualization tools.
  \item Improve reporting tools in \LaTeX.
  \item Extend AI functionality.
\end{itemize}

\end{document}
```
