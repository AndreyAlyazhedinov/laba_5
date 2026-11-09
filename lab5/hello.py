import tkinter as tk
from datetime import datetime

PARTS = (
    (5, "Доброе утро"),
    (12, "Добрый день"),
    (18, "Добрый вечер"),
    (23, "Доброй ночи"),
)


def part_of_day(hour):
    result = PARTS[-1][1]
    for start, text in PARTS:
        if hour >= start:
            result = text
    return result


class HelloFrame(tk.Frame):
    def __init__(self, master, clock=datetime.now):
        super().__init__(master, padx=40, pady=30)
        self.clock = clock
        self.clicks = 0
        self.title = tk.Label(self, text="Нажмите на кнопку",
                              font=("Segoe UI", 18, "bold"))
        self.title.pack()
        self.info = tk.Label(self, text="", font=("Segoe UI", 11),
                             fg="#555555")
        self.info.pack(pady=(6, 18))
        self.button = tk.Button(
            self, text="Привет", width=16, font=("Segoe UI", 12),
            bg="#2e7d32", fg="white", activebackground="#1b5e20",
            activeforeground="white", command=self.say_hello)
        self.button.pack()

    def say_hello(self):
        self.clicks += 1
        self.title.config(text="Привет!")
        part = part_of_day(self.clock().hour)
        self.info.config(text=f"{part}! Нажатий: {self.clicks}")


def main():
    root = tk.Tk()
    root.title("Окно с кнопкой «Привет»")
    HelloFrame(root).pack(fill="both", expand=True)
    root.mainloop()


if __name__ == "__main__":
    main()
