import tempfile
import tkinter as tk
import unittest
from datetime import datetime
from pathlib import Path
from unittest import mock

from lab5.app import MainWindow
from lab5.calc import Calculator
from lab5.hello import HelloFrame, part_of_day
from lab5.notes import NotesFrame


class TkCase(unittest.TestCase):
    def setUp(self):
        self.root = tk.Tk()
        self.root.withdraw()
        self.tmp = tempfile.TemporaryDirectory()
        self.notes_path = Path(self.tmp.name) / "notes.json"

    def tearDown(self):
        self.root.destroy()
        self.tmp.cleanup()


class TestHello(TkCase):
    def test_part_of_day(self):
        self.assertEqual(part_of_day(8), "Доброе утро")
        self.assertEqual(part_of_day(13), "Добрый день")
        self.assertEqual(part_of_day(19), "Добрый вечер")
        self.assertEqual(part_of_day(23), "Доброй ночи")
        self.assertEqual(part_of_day(3), "Доброй ночи")

    def test_button_click(self):
        frame = HelloFrame(self.root,
                           clock=lambda: datetime(2026, 11, 10, 9, 30))
        frame.button.invoke()
        frame.button.invoke()
        self.assertEqual(frame.title.cget("text"), "Привет!")
        self.assertEqual(frame.info.cget("text"), "Доброе утро! Нажатий: 2")


class TestCalculator(TkCase):
    def setUp(self):
        super().setUp()
        self.calc = Calculator(self.root)

    def press_all(self, keys):
        for key in keys:
            self.calc.buttons[key].invoke()

    def test_buttons_compute_result(self):
        self.press_all("12+3*4=")
        self.assertEqual(self.calc.value.get(), "24")
        self.assertEqual(self.calc.history.get(), "12+3*4 =")

    def test_continue_with_result(self):
        self.press_all("(1+2)*3=")
        self.press_all("/2=")
        self.assertEqual(self.calc.value.get(), "4.5")

    def test_error_keeps_expression(self):
        self.press_all("7/0=")
        self.assertEqual(self.calc.value.get(), "7/0")
        self.assertEqual(self.calc.error.cget("text"), "Деление на ноль")
        self.press_all("⌫")
        self.assertEqual(self.calc.value.get(), "7/")
        self.assertEqual(self.calc.error.cget("text"), "")

    def test_clear(self):
        self.press_all("5+5=C")
        self.assertEqual(self.calc.value.get(), "")
        self.assertEqual(self.calc.history.get(), "")


class TestNotesFrame(TkCase):
    def setUp(self):
        super().setUp()
        self.frame = NotesFrame(self.root, self.notes_path)

    def write(self, text):
        self.frame.text.insert("1.0", text)
        self.frame.dirty = True

    def test_save_new_note(self):
        self.write("Купить молоко\nи хлеб")
        self.assertTrue(self.frame.save_note())
        self.assertEqual(self.frame.listbox.get(0), "Купить молоко")
        self.assertFalse(self.frame.dirty)
        reopened = NotesFrame(self.root, self.notes_path)
        self.assertEqual(reopened.listbox.size(), 1)

    def test_empty_note_is_not_saved(self):
        self.write("   ")
        self.assertFalse(self.frame.save_note())
        self.assertFalse(self.notes_path.exists())

    def test_select_and_edit(self):
        self.frame.store.add("первая")
        self.frame.store.add("вторая")
        self.frame.refresh()
        index = [n.text for n in self.frame.visible].index("первая")
        self.frame.listbox.selection_set(index)
        self.frame.on_select()
        self.assertEqual(self.frame.text_value(), "первая")
        self.write("изменённая ")
        self.frame.save_note()
        self.assertEqual(self.frame.store.get(1).text, "изменённая первая")

    def test_search(self):
        for text in ("Купить хлеб", "Позвонить", "хлеб и сыр"):
            self.frame.store.add(text)
        self.frame.query.set("хлеб")
        self.assertEqual(self.frame.listbox.size(), 2)

    def test_delete_asks_confirmation(self):
        self.write("удалить меня")
        self.frame.save_note()
        with mock.patch("lab5.notes.messagebox.askyesno", return_value=False):
            self.frame.delete_note()
        self.assertEqual(len(self.frame.store.notes), 1)
        with mock.patch("lab5.notes.messagebox.askyesno", return_value=True):
            self.frame.delete_note()
        self.assertEqual(self.frame.store.notes, [])
        self.assertEqual(self.frame.text_value(), "")

    def test_unsaved_changes_on_new_note(self):
        self.write("не сохранено")
        with mock.patch("lab5.notes.messagebox.askyesnocancel",
                        return_value=None):
            self.frame.new_note()
        self.assertEqual(self.frame.text_value(), "не сохранено")
        with mock.patch("lab5.notes.messagebox.askyesnocancel",
                        return_value=True):
            self.frame.new_note()
        self.assertEqual(self.frame.text_value(), "")
        self.assertEqual(len(self.frame.store.notes), 1)


class TestMainWindow(TkCase):
    def test_tabs_and_status(self):
        window = MainWindow(self.root, self.notes_path)
        self.assertEqual(window.notebook.index("end"), 5)
        self.assertEqual(window.status.cget("text"),
                         "Вкладка 1 из 5: Привет")
        window.notebook.select(3)
        window.on_tab_changed()
        self.assertEqual(window.status.cget("text"),
                         "Вкладка 4 из 5: График")
        self.assertEqual(self.root.title(), "ЛР5, вариант 1 — График")
        self.assertEqual(len(window.plot.curves), 1)


if __name__ == "__main__":
    unittest.main()
