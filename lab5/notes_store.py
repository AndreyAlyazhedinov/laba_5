import json
import os
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path


@dataclass
class Note:
    id: int
    title: str
    text: str
    updated: str


def make_title(text, limit=40):
    for line in text.splitlines():
        line = line.strip()
        if line:
            return line if len(line) <= limit else line[:limit - 1] + "…"
    return "Без названия"


def format_time(stamp):
    return datetime.fromisoformat(stamp).strftime("%d.%m.%Y %H:%M")


class NotesStore:
    def __init__(self, path, clock=datetime.now):
        self.path = Path(path)
        self.clock = clock
        self.notes = []
        self.load()

    def load(self):
        if not self.path.exists():
            self.notes = []
            return
        with open(self.path, encoding="utf-8") as file:
            self.notes = [Note(**item) for item in json.load(file)]

    def save(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        tmp = self.path.with_suffix(".tmp")
        with open(tmp, "w", encoding="utf-8") as file:
            json.dump([asdict(note) for note in self.notes], file,
                      ensure_ascii=False, indent=2)
        os.replace(tmp, self.path)

    def _stamp(self):
        return self.clock().isoformat(timespec="seconds")

    def get(self, note_id):
        for note in self.notes:
            if note.id == note_id:
                return note
        raise KeyError(note_id)

    def add(self, text):
        next_id = max((note.id for note in self.notes), default=0) + 1
        note = Note(next_id, make_title(text), text, self._stamp())
        self.notes.append(note)
        self.save()
        return note

    def update(self, note_id, text):
        note = self.get(note_id)
        note.text = text
        note.title = make_title(text)
        note.updated = self._stamp()
        self.save()
        return note

    def delete(self, note_id):
        self.notes.remove(self.get(note_id))
        self.save()

    def find(self, query=""):
        query = query.strip().lower()
        found = [note for note in self.notes if query in note.text.lower()]
        return sorted(found, key=lambda note: (note.updated, note.id),
                      reverse=True)
