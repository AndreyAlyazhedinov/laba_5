import tkinter as tk

from lab5.expr import ExprError, evaluate, format_number

KEYS = (
    ("C", "⌫", "(", ")"),
    ("7", "8", "9", "/"),
    ("4", "5", "6", "*"),
    ("1", "2", "3", "-"),
    ("0", ".", "=", "+"),
)
SERVICE = {"C", "⌫", "(", ")", "/", "*", "-", "+"}


class Calculator(tk.Frame):
    def __init__(self, master):
        super().__init__(master, padx=12, pady=12)
        self.value = tk.StringVar()
        self.history = tk.StringVar()
        tk.Label(self, textvariable=self.history, anchor="e", fg="#777777",
                 font=("Consolas", 11)).grid(row=0, column=0, columnspan=4,
                                             sticky="ew")
        self.display = tk.Entry(self, textvariable=self.value,
                                justify="right", font=("Consolas", 20),
                                relief="flat", bg="#f4f4f4")
        self.display.grid(row=1, column=0, columnspan=4, sticky="ew",
                          pady=(0, 10), ipady=6)
        self.display.bind("<Return>", lambda event: self.calculate())
        self.display.bind("<KP_Enter>", lambda event: self.calculate())
        self.display.bind("<Escape>", lambda event: self.clear())
        self.buttons = {}
        for row, keys in enumerate(KEYS, start=2):
            for column, key in enumerate(keys):
                button = tk.Button(self, text=key, width=5, height=2,
                                   font=("Segoe UI", 13),
                                   command=lambda k=key: self.press(k))
                if key == "=":
                    button.config(bg="#1565c0", fg="white")
                elif key in SERVICE:
                    button.config(bg="#e0e0e0")
                button.grid(row=row, column=column, padx=2, pady=2,
                            sticky="nsew")
                self.buttons[key] = button
        self.error = tk.Label(self, text="", fg="#c62828", anchor="w")
        self.error.grid(row=len(KEYS) + 2, column=0, columnspan=4,
                        sticky="ew")
        for column in range(4):
            self.columnconfigure(column, weight=1)

    def press(self, key):
        self.error.config(text="")
        if key == "=":
            self.calculate()
        elif key == "C":
            self.clear()
        elif key == "⌫":
            self.value.set(self.value.get()[:-1])
        else:
            self.value.set(self.value.get() + key)
            self.display.icursor("end")

    def clear(self):
        self.value.set("")
        self.history.set("")
        self.error.config(text="")

    def calculate(self):
        expression = self.value.get()
        try:
            result = format_number(evaluate(expression))
        except ExprError as exc:
            self.error.config(text=str(exc))
            return None
        self.history.set(f"{expression} =")
        self.value.set(result)
        self.display.icursor("end")
        return result


def main():
    root = tk.Tk()
    root.title("Калькулятор")
    root.resizable(False, False)
    calc = Calculator(root)
    calc.pack(fill="both", expand=True)
    calc.display.focus_set()
    root.mainloop()


if __name__ == "__main__":
    main()
