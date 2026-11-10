import re
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from lab5.notes_store import NotesStore, format_time, make_title

DEFAULT_PATH = Path(__file__).resolve().parent.parent / "notes.json"
KEY_S = 83


class NotesFrame(tk.Frame):
    def __init__(self, master, path=DEFAULT_PATH):
        super().__init__(master, padx=8, pady=8)
        self.store = NotesStore(path)
        self.current = None
        self.visible = []
        self.dirty = False

        left = tk.Frame(self)
        left.pack(side="left", fill="y")
        tk.Label(left, text="Поиск:", anchor="w").pack(fill="x")
        self.query = tk.StringVar()
        self.query.trace_add("write", lambda *args: self.refresh())
        ttk.Entry(left, textvariable=self.query).pack(fill="x")
        self.listbox = tk.Listbox(left, width=32, activestyle="none",
                                  exportselection=False,
                                  font=("Segoe UI", 10))
        self.listbox.pack(fill="y", expand=True, pady=6)
        self.listbox.bind("<<ListboxSelect>>", self.on_select)
        buttons = tk.Frame(left)
        buttons.pack(fill="x")
        ttk.Button(buttons, text="Новая", command=self.new_note).pack(
            side="left", expand=True, fill="x")
        ttk.Button(buttons, text="Удалить", command=self.delete_note).pack(
            side="left", expand=True, fill="x")

        right = tk.Frame(self, padx=8)
        right.pack(side="left", fill="both", expand=True)
        self.text = tk.Text(right, wrap="word", undo=True, width=48,
                            height=16, font=("Segoe UI", 11))
        self.text.pack(fill="both", expand=True)
        self.text.bind("<<Modified>>", self.on_modified)
        self.text.bind("<Control-KeyPress>", self.on_control_key)
        bottom = tk.Frame(right)
        bottom.pack(fill="x", pady=(6, 0))
        ttk.Button(bottom, text="Сохранить (Ctrl+S)",
                   command=self.save_note).pack(side="left")
        ttk.Button(bottom, text="Экспорт в .txt",
                   command=self.export_note).pack(side="left", padx=6)
        self.status = tk.Label(bottom, anchor="e", fg="#555555")
        self.status.pack(side="right")

        self.refresh()
        self.set_status(f"Файл {self.store.path.name}, "
                        f"заметок: {len(self.store.notes)}")

    def set_status(self, text):
        self.status.config(text=text)

    def text_value(self):
        return self.text.get("1.0", "end-1c")

    def load_text(self, text):
        self.text.delete("1.0", "end")
        self.text.insert("1.0", text)
        self.text.edit_reset()
        self.text.edit_modified(False)
        self.dirty = False

    def on_modified(self, event=None):
        if self.text.edit_modified():
            self.dirty = True

    def on_control_key(self, event):
        if event.keycode == KEY_S:
            self.save_note()
            return "break"
        return None

    def refresh(self):
        self.visible = self.store.find(self.query.get())
        self.listbox.delete(0, "end")
        for note in self.visible:
            self.listbox.insert("end", note.title)
        ids = [note.id for note in self.visible]
        if self.current in ids:
            index = ids.index(self.current)
            self.listbox.selection_set(index)
            self.listbox.see(index)

    def on_select(self, event=None):
        selection = self.listbox.curselection()
        if not selection:
            return
        note = self.visible[selection[0]]
        if note.id == self.current:
            return
        if not self.confirm_discard():
            self.listbox.selection_clear(0, "end")
            self.refresh()
            return
        self.current = note.id
        self.load_text(note.text)
        self.set_status(f"Изменена {format_time(note.updated)}")

    def new_note(self):
        if not self.confirm_discard():
            return
        self.current = None
        self.listbox.selection_clear(0, "end")
        self.load_text("")
        self.text.focus_set()
        self.set_status("Новая заметка")

    def save_note(self):
        text = self.text_value()
        if not text.strip():
            self.set_status("Пустую заметку сохранить нельзя")
            return False
        if self.current is None:
            self.current = self.store.add(text).id
        else:
            self.store.update(self.current, text)
        self.text.edit_modified(False)
        self.dirty = False
        self.refresh()
        self.set_status(f"Сохранено в {self.store.path.name}")
        return True

    def delete_note(self):
        if self.current is None:
            self.set_status("Заметка не выбрана")
            return
        note = self.store.get(self.current)
        if not messagebox.askyesno("Удаление",
                                   f"Удалить заметку «{note.title}»?",
                                   parent=self):
            return
        self.store.delete(self.current)
        self.current = None
        self.load_text("")
        self.refresh()
        self.set_status("Заметка удалена")

    def export_note(self):
        text = self.text_value()
        if not text.strip():
            self.set_status("Нечего экспортировать")
            return
        name = re.sub(r'[\\/:*?"<>|…]', "_", make_title(text, 30))
        path = filedialog.asksaveasfilename(
            parent=self, defaultextension=".txt", initialfile=f"{name}.txt",
            filetypes=[("Текстовые файлы", "*.txt")])
        if path:
            Path(path).write_text(text, encoding="utf-8")
            self.set_status(f"Экспортировано в {Path(path).name}")

    def confirm_discard(self):
        if not self.dirty:
            return True
        answer = messagebox.askyesnocancel(
            "Заметки", "Сохранить изменения в текущей заметке?", parent=self)
        if answer is None:
            return False
        if answer:
            return self.save_note()
        self.dirty = False
        return True


def main():
    root = tk.Tk()
    root.title("Заметки")
    frame = NotesFrame(root)
    frame.pack(fill="both", expand=True)

    def close():
        if frame.confirm_discard():
            root.destroy()

    root.protocol("WM_DELETE_WINDOW", close)
    root.mainloop()


if __name__ == "__main__":
    main()
