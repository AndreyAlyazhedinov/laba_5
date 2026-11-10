import math
import tkinter as tk
from tkinter import ttk

from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg,
                                               NavigationToolbar2Tk)
from matplotlib.figure import Figure

from lab5.expr import ExprError, compile_function

EXAMPLES = (
    "sin(x)",
    "x^2 - 4",
    "exp(-x^2 / 2)",
    "sin(x) / x",
    "sqrt(x)",
    "abs(sin(x)) * cos(3*x)",
)


def sample(func, x_min, x_max, count=401):
    if x_min >= x_max:
        raise ExprError("Левая граница должна быть меньше правой")
    step = (x_max - x_min) / (count - 1)
    xs = [x_min + i * step for i in range(count)]
    ys = []
    for x in xs:
        try:
            y = float(func(x))
        except ExprError:
            y = math.nan
        ys.append(y if math.isfinite(y) else math.nan)
    if all(math.isnan(y) for y in ys):
        raise ExprError("Функция не определена на этом отрезке")
    return xs, ys


def parse_bound(text):
    try:
        return float(text.replace(",", "."))
    except ValueError:
        raise ExprError(f"Граница «{text}» не является числом") from None


class PlotFrame(tk.Frame):
    def __init__(self, master):
        super().__init__(master, padx=8, pady=8)
        self.curves = []
        controls = tk.Frame(self)
        controls.pack(fill="x")
        tk.Label(controls, text="f(x) =").pack(side="left")
        self.formula = tk.StringVar(value=EXAMPLES[0])
        box = ttk.Combobox(controls, textvariable=self.formula,
                           values=EXAMPLES, width=24)
        box.pack(side="left", padx=(4, 10))
        box.bind("<Return>", lambda event: self.draw())
        box.bind("<<ComboboxSelected>>", lambda event: self.draw())
        tk.Label(controls, text="x от").pack(side="left")
        self.x_min = tk.StringVar(value="-10")
        ttk.Entry(controls, textvariable=self.x_min, width=6).pack(
            side="left", padx=4)
        tk.Label(controls, text="до").pack(side="left")
        self.x_max = tk.StringVar(value="10")
        ttk.Entry(controls, textvariable=self.x_max, width=6).pack(
            side="left", padx=4)
        self.keep = tk.BooleanVar(value=False)
        ttk.Checkbutton(controls, text="Добавить к графику",
                        variable=self.keep).pack(side="left", padx=8)
        ttk.Button(controls, text="Построить", command=self.draw).pack(
            side="left")
        ttk.Button(controls, text="Очистить", command=self.clear).pack(
            side="left", padx=4)
        self.message = tk.Label(self, anchor="w", fg="#c62828")
        self.message.pack(fill="x")

        self.figure = Figure(figsize=(6.4, 4), dpi=100)
        self.figure.subplots_adjust(left=0.09, right=0.97, top=0.95,
                                    bottom=0.12)
        self.axes = self.figure.add_subplot()
        self.canvas = FigureCanvasTkAgg(self.figure, master=self)
        toolbar = NavigationToolbar2Tk(self.canvas, self, pack_toolbar=False)
        toolbar.update()
        toolbar.pack(side="bottom", fill="x")
        self.canvas.get_tk_widget().pack(fill="both", expand=True)
        self.clear()

    def clear(self):
        self.curves = []
        self.axes.clear()
        self.axes.grid(True, alpha=0.3)
        self.axes.axhline(0, color="#999999", linewidth=0.8)
        self.axes.axvline(0, color="#999999", linewidth=0.8)
        self.axes.set_xlabel("x")
        self.axes.set_ylabel("f(x)")
        self.canvas.draw_idle()
        self.message.config(text="")

    def draw(self):
        formula = self.formula.get().strip()
        try:
            func = compile_function(formula)
            bounds = parse_bound(self.x_min.get()), parse_bound(self.x_max.get())
            xs, ys = sample(func, *bounds)
        except ExprError as exc:
            self.message.config(text=str(exc))
            return False
        if not self.keep.get():
            self.clear()
        line, = self.axes.plot(xs, ys, linewidth=1.6,
                               label=f"f(x) = {formula}")
        self.curves.append(line)
        self.axes.set_xlim(*bounds)
        self.axes.legend(loc="upper right")
        self.canvas.draw_idle()
        self.message.config(text="")
        return True


def main():
    root = tk.Tk()
    root.title("График matplotlib в Tkinter")
    frame = PlotFrame(root)
    frame.pack(fill="both", expand=True)
    frame.draw()
    root.protocol("WM_DELETE_WINDOW", root.quit)
    root.mainloop()
    root.destroy()


if __name__ == "__main__":
    main()
