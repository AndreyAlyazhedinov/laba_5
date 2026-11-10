import json
import tempfile
import unittest
from datetime import datetime, timedelta
from pathlib import Path

from lab5.notes_store import NotesStore, format_time, make_title


class FakeClock:
    def __init__(self):
        self.now = datetime(2026, 11, 10, 18, 0)

    def __call__(self):
        self.now += timedelta(minutes=1)
        return self.now


class TestNotesStore(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = Path(self.tmp.name) / "notes.json"
        self.store = NotesStore(self.path, clock=FakeClock())

    def tearDown(self):
        self.tmp.cleanup()

    def test_missing_file_gives_empty_store(self):
        self.assertEqual(self.store.notes, [])
        self.assertFalse(self.path.exists())

    def test_add_saves_to_file(self):
        note = self.store.add("Список покупок\nмолоко, хлеб")
        self.assertEqual(note.id, 1)
        self.assertEqual(note.title, "Список покупок")
        data = json.loads(self.path.read_text(encoding="utf-8"))
        self.assertEqual(data[0]["text"], "Список покупок\nмолоко, хлеб")

    def test_reload_from_file(self):
        self.store.add("первая")
        self.store.add("вторая")
        again = NotesStore(self.path)
        self.assertEqual([n.title for n in again.notes], ["первая", "вторая"])

    def test_update_and_delete(self):
        first = self.store.add("черновик")
        second = self.store.add("другая")
        self.store.update(first.id, "  \nчистовик")
        self.assertEqual(self.store.get(first.id).title, "чистовик")
        self.store.delete(second.id)
        self.assertEqual(len(NotesStore(self.path).notes), 1)
        with self.assertRaises(KeyError):
            self.store.get(second.id)

    def test_ids_are_not_reused(self):
        self.store.add("a")
        second = self.store.add("b")
        self.store.delete(1)
        self.assertEqual(self.store.add("c").id, second.id + 1)

    def test_find_is_case_insensitive_and_newest_first(self):
        self.store.add("Купить хлеб")
        self.store.add("Позвонить маме")
        self.store.add("хлеб и молоко")
        found = self.store.find("ХЛЕБ")
        self.assertEqual([n.text for n in found],
                         ["хлеб и молоко", "Купить хлеб"])
        self.assertEqual(len(self.store.find()), 3)

    def test_make_title(self):
        self.assertEqual(make_title(""), "Без названия")
        self.assertEqual(make_title("\n\n  Заголовок  \nтекст"), "Заголовок")
        self.assertEqual(len(make_title("а" * 100, limit=20)), 20)

    def test_format_time(self):
        self.assertEqual(format_time("2026-11-10T18:05:00"),
                         "10.11.2026 18:05")


if __name__ == "__main__":
    unittest.main()
