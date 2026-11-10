import tkinter as tk
from tkinter import ttk

from lab5.calc import Calculator
from lab5.hello import HelloFrame
from lab5.notes import DEFAULT_PATH, NotesFrame
from lab5.plot import PlotFrame

ABOUT = (
    "Лабораторная работа №5\n"
    "Визуальное программирование на Python\n\n"
    "Аляжединов Андрей Борисович, вариант 1\n\n"
    "Переключение вкладок: Ctrl+1 … Ctrl+5,\n"
    "Ctrl+Tab — следующая вкладка, Ctrl+Shift+Tab — предыдущая."
)


class MainWindow:
    def __init__(self, root, notes_path=DEFAULT_PATH):
        self.root = root
        root.minsize(780, 540)
        self.status = tk.Label(root, anchor="w", padx=8, bd=1,
                               relief="sunken", fg="#444444")
        self.status.pack(side="bottom", fill="x")
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill="both", expand=True, padx=6, pady=6)
        self.notes = NotesFrame(self.notebook, notes_path)
        self.plot = PlotFrame(self.notebook)
        pages = (
            ("Привет", HelloFrame(self.notebook)),
            ("Калькулятор", Calculator(self.notebook)),
            ("Заметки", self.notes),
            ("График", self.plot),
            ("О программе", self.about_page()),
        )
        for title, page in pages:
            self.notebook.add(page, text=title, padding=4)
        self.notebook.enable_traversal()
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_changed)
        for number in range(1, len(pages) + 1):
            root.bind(f"<Control-Key-{number}>",
                      lambda event, i=number - 1: self.notebook.select(i))
        root.protocol("WM_DELETE_WINDOW", self.close)
        self.plot.draw()
        self.on_tab_changed()

    def about_page(self):
        frame = tk.Frame(self.notebook, padx=24, pady=24)
        tk.Label(frame, text=ABOUT, justify="left",
                 font=("Segoe UI", 11)).pack(anchor="nw")
        return frame

    def on_tab_changed(self, event=None):
        index = self.notebook.index("current")
        title = self.notebook.tab(index, "text")
        total = self.notebook.index("end")
        self.status.config(text=f"Вкладка {index + 1} из {total}: {title}")
        self.root.title(f"ЛР5, вариант 1 — {title}")

    def close(self):
        if self.notes.confirm_discard():
            self.root.quit()


def main():
    root = tk.Tk()
    MainWindow(root)
    root.mainloop()
    root.destroy()


if __name__ == "__main__":
    main()
