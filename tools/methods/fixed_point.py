from __future__ import annotations
from typing import Callable, Tuple, Optional, List, Dict, Any
from dataclasses import dataclass
import math
import re
import io, base64

import numpy as np
import matplotlib
matplotlib.use("Agg")          # headless rendering on server
import matplotlib.pyplot as plt

# === Turn expression strings into safe f(x) callables ===
_ALLOWED = {
    "pi": math.pi, "e": math.e, "E": math.e,
    "sin": math.sin, "cos": math.cos, "tan": math.tan,
    "asin": math.asin, "acos": math.acos, "atan": math.atan,
    "sinh": math.sinh, "cosh": math.cosh, "tanh": math.tanh,
    "exp": math.exp, "log": math.log, "log10": math.log10,
    "sqrt": math.sqrt, "abs": abs, "floor": math.floor, "ceil": math.ceil,
    "pow": pow
}
_VAR_PATTERN = re.compile(r"\bx\b")

def _sanitize(expr: str) -> str:
    """Light normalization (e.g., ^ → **)."""
    expr = expr.strip()
    expr = expr.replace("^", "**")
    return expr

def compile_expr(expr_str: str) -> Tuple[Callable[[float], float], str]:
    """
    Given e.g. 'cos(x)+x**2', returns:
      (callable f(x), normalized_expression)
    Raises ValueError if the expression fails to compile.
    """
    s = _sanitize(expr_str)
    try:
        code = compile(s, "<expr>", "eval")
    except Exception as e:
        raise ValueError(f"Invalid expression: {expr_str!r} -> {e}")

    def f(x: float) -> float:
        env = dict(_ALLOWED)
        env["x"] = x
        return float(eval(code, {"__builtins__": {}}, env))

    return f, s


def d_numeric(f: Callable[[float], float], h: float = 1e-6) -> Callable[[float], float]:
    """Simple and robust numerical derivative (central difference)."""
    def df(x: float) -> float:
        return (f(x + h) - f(x - h)) / (2.0 * h)
    return df


def make_newton_g_from_f(f: Callable[[float], float], h: float = 1e-6) -> Callable[[float], float]:
    """
    If user provides f(x) but not g(x), generate:
      g(x) = x - f(x)/f'(x)
    using a numerical derivative. This enables fixed-point iteration
    “Newton-style” without asking for a symbolic derivative.
    """
    df = d_numeric(f, h=h)
    def g(x: float) -> float:
        dfx = df(x)
        if abs(dfx) < 1e-14:
            raise ZeroDivisionError("f'(x) ≈ 0 in make_newton_g_from_f; cannot build g(x).")
        return x - f(x) / dfx
    return g

# === Core fixed-point iteration (logic unchanged) ===
def fixed_point_full(
    g: Callable[[float], float],
    x0: float,
    tol: float = 1e-6,
    nmax: int = 100,
    f: Optional[Callable[[float], float]] = None,
    use_relative_error: bool = False
) -> Tuple[List[Tuple[int, float, float, Optional[float], float]], float]:
    """
    Iterate x_{i+1} = g(x_i) until tolerance is met or nmax is reached.

    Returns:
      - rows: list of (i, x_i, g(x_i), f(x_i) or None, error_i)
      - x_last: last value (final approximation)
    """
    rows: List[Tuple[int, float, float, Optional[float], float]] = []
    xi = float(x0)

    for i in range(nmax):
        gxi = float(g(xi))
        fxi = float(f(xi)) if f is not None else None

        if use_relative_error:
            denom = max(1.0, abs(gxi))
            Ei = abs(gxi - xi) / denom
        else:
            Ei = abs(gxi - xi)

        rows.append((i, xi, gxi, fxi, Ei))

        if Ei <= tol:
            xi = gxi
            break
        xi = gxi

    return rows, xi

@dataclass
class PFStep:
    """Lightweight container per iteration to feed the view."""
    i: int
    x: float
    gx: float
    fx: Optional[float]
    err: float

def _cobweb_lines(steps: List[PFStep]) -> List[tuple]:
    """
    Produce “cobweb” line segments to visualize the iteration:
      - vertical:   (x_i, x_i) → (x_i, g(x_i))
      - horizontal: (x_i, g(x_i)) → (g(x_i), g(x_i))
    Purely visual; does not affect computation.
    """
    segs = []
    if not steps:
        return segs
    for s in steps:
        segs.append((s.x, s.x, s.x, s.gx))   # vertical
        segs.append((s.x, s.gx, s.gx, s.gx)) # horizontal
    return segs

def _plot_base64(
    f_str: Optional[str],
    g_str: str,
    x_star: float,
    span: float = 5.0,
    steps: Optional[List[PFStep]] = None
) -> str:
    """
    Draw g(x), y=x, and (optionally) f(x) with a clean style:
      - dotted grid
      - vertical line at final approximation
      - cobweb lines to illustrate the iteration path
    Returns a data URL (base64) ready for <img src="...">.
    """
    xmin, xmax = x_star - span, x_star + span
    xs = np.linspace(xmin, xmax, 500)

    g_fun, _ = compile_expr(g_str)
    f_fun = None
    if f_str:
        f_fun, _ = compile_expr(f_str)

    g_vals = np.array([g_fun(v) for v in xs])
    y_eq_x = xs.copy()

    fig, ax = plt.subplots(figsize=(6.6, 4.2), dpi=160)
    ax.set_facecolor("#fafafa")

    # Main curves
    ax.plot(xs, g_vals, linewidth=2.4, label="g(x)")
    ax.plot(xs, y_eq_x, linestyle="--", linewidth=1.6, label="y = x")
    if f_fun is not None:
        f_vals = np.array([f_fun(v) for v in xs])
        ax.plot(xs, f_vals, linestyle=":", linewidth=1.8, label="f(x)")

    # Cobweb (if steps provided)
    if steps:
        for (x0, y0, x1, y1) in _cobweb_lines(steps):
            ax.plot([x0, x1], [y0, y1], linewidth=1.1)

    # Marker at the final approximation
    ax.axvline(x_star, linestyle="--", linewidth=1.1)

    # Styling
    ax.grid(True, linewidth=0.4, linestyle=":")
    ax.set_title("Fixed-Point — g(x) vs y=x", fontweight="bold")
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    leg = ax.legend(frameon=True)
    leg.get_frame().set_alpha(0.9)

    fig.tight_layout()
    buf = io.BytesIO()
    fig.savefig(buf, format="png")
    plt.close(fig)
    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode("ascii")

def run_fixed_point_web(
    g_text: Optional[str],
    f_text: Optional[str],
    x0: float,
    tol: float = 1e-6,
    max_iter: int = 100,
    use_relative_error: bool = False,
    plot_span: float = 5.0
) -> Dict[str, Any]:
    """
    Entry point for the view. Inputs:
      g_text, f_text, x0, tol, max_iter, use_relative_error, plot_span
    Output dict (same keys as before):
      plot_data_url, steps, converged, reason, x_final, form_echo
    """
    g_fun = None
    f_fun = None
    g_str = (g_text or "").strip()
    f_str = (f_text or "").strip()

    if g_str:
        g_fun, g_str = compile_expr(g_str)
    if f_str:
        f_fun, f_str = compile_expr(f_str)

    # If no g(x) but an f(x) is given, build g(x) using one Newton step.
    if g_fun is None and f_fun is not None:
        g_fun = make_newton_g_from_f(f_fun)

    if g_fun is None:
        raise ValueError("You must provide g(x) or f(x).")

    rows, x_last = fixed_point_full(
        g_fun, x0, tol=tol, nmax=max_iter, f=f_fun, use_relative_error=use_relative_error
    )

    steps: List[PFStep] = [
        PFStep(i=i, x=xi, gx=gxi, fx=fxi, err=Ei) for (i, xi, gxi, fxi, Ei) in rows
    ]

    plot_url = _plot_base64(
        f_str if f_str else None,
        g_str if g_str else "x",
        x_last,
        span=plot_span,
        steps=steps
    )

    converged = bool(rows) and (rows[-1][4] <= tol)
    reason = (
        "Converged by tolerance (|x_{n+1} - x_n| ≤ tol)."
        if converged else
        "Reached max_iter without meeting tolerance."
    )

    return {
        "plot_data_url": plot_url,
        "steps": [s.__dict__ for s in steps],
        "converged": converged,
        "reason": reason,
        "x_final": float(x_last),
        "form_echo": {
            "g": g_str,
            "f": f_str,
            "x0": x0, "tol": tol, "max_iter": max_iter,
            "use_relative_error": use_relative_error
        }
    }
