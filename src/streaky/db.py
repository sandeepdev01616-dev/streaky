"""SQLite storage for tasks and habits."""

from __future__ import annotations

import os
import sqlite3
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path

SCHEMA = """
CREATE TABLE IF NOT EXISTS tasks (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    title       TEXT NOT NULL,
    created_at  TEXT NOT NULL,
    done_at     TEXT
);

CREATE TABLE IF NOT EXISTS habits (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT NOT NULL UNIQUE,
    created_at  TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS checkins (
    habit_id    INTEGER NOT NULL REFERENCES habits(id) ON DELETE CASCADE,
    day         TEXT NOT NULL,
    PRIMARY KEY (habit_id, day)
);
"""


def default_db_path() -> Path:
    """Return the database path, honouring STREAKY_DB and XDG_DATA_HOME."""
    override = os.environ.get("STREAKY_DB")
    if override:
        return Path(override).expanduser()
    data_home = os.environ.get("XDG_DATA_HOME") or Path.home() / ".local" / "share"
    return Path(data_home) / "streaky" / "streaky.db"


@dataclass
class Task:
    id: int
    title: str
    created_at: datetime
    done_at: datetime | None

    @property
    def done(self) -> bool:
        return self.done_at is not None


@dataclass
class Habit:
    id: int
    name: str
    created_at: datetime


class Store:
    def __init__(self, path: Path | str | None = None) -> None:
        self.path = Path(path) if path else default_db_path()
        if str(self.path) != ":memory:":
            self.path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(self.path)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA foreign_keys = ON")
        self.conn.executescript(SCHEMA)

    def close(self) -> None:
        self.conn.close()

    # Tasks

    def add_task(self, title: str) -> Task:
        now = datetime.now().isoformat(timespec="seconds")
        with self.conn:
            cur = self.conn.execute(
                "INSERT INTO tasks (title, created_at) VALUES (?, ?)", (title, now)
            )
        return self.get_task(cur.lastrowid)

    def get_task(self, task_id: int) -> Task:
        row = self.conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
        if row is None:
            raise KeyError(f"no task with id {task_id}")
        return _task(row)

    def list_tasks(self, include_done: bool = False) -> list[Task]:
        sql = "SELECT * FROM tasks"
        if not include_done:
            sql += " WHERE done_at IS NULL"
        sql += " ORDER BY id"
        return [_task(r) for r in self.conn.execute(sql)]

    def complete_task(self, task_id: int) -> Task:
        self.get_task(task_id)
        now = datetime.now().isoformat(timespec="seconds")
        with self.conn:
            self.conn.execute(
                "UPDATE tasks SET done_at = ? WHERE id = ? AND done_at IS NULL",
                (now, task_id),
            )
        return self.get_task(task_id)

    def remove_task(self, task_id: int) -> None:
        self.get_task(task_id)
        with self.conn:
            self.conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))

    # Habits

    def add_habit(self, name: str) -> Habit:
        now = datetime.now().isoformat(timespec="seconds")
        try:
            with self.conn:
                cur = self.conn.execute(
                    "INSERT INTO habits (name, created_at) VALUES (?, ?)", (name, now)
                )
        except sqlite3.IntegrityError:
            raise ValueError(f"habit '{name}' already exists") from None
        return Habit(cur.lastrowid, name, datetime.fromisoformat(now))

    def get_habit(self, name: str) -> Habit:
        row = self.conn.execute("SELECT * FROM habits WHERE name = ?", (name,)).fetchone()
        if row is None:
            raise KeyError(f"no habit named '{name}'")
        return Habit(row["id"], row["name"], datetime.fromisoformat(row["created_at"]))

    def list_habits(self) -> list[Habit]:
        rows = self.conn.execute("SELECT * FROM habits ORDER BY name")
        return [Habit(r["id"], r["name"], datetime.fromisoformat(r["created_at"])) for r in rows]

    def remove_habit(self, name: str) -> None:
        habit = self.get_habit(name)
        with self.conn:
            self.conn.execute("DELETE FROM habits WHERE id = ?", (habit.id,))

    def check_in(self, name: str, day: date | None = None) -> bool:
        """Record a check-in. Returns False if that day was already checked."""
        habit = self.get_habit(name)
        day = day or date.today()
        with self.conn:
            cur = self.conn.execute(
                "INSERT OR IGNORE INTO checkins (habit_id, day) VALUES (?, ?)",
                (habit.id, day.isoformat()),
            )
        return cur.rowcount == 1

    def checkin_days(self, name: str) -> set[date]:
        habit = self.get_habit(name)
        rows = self.conn.execute("SELECT day FROM checkins WHERE habit_id = ?", (habit.id,))
        return {date.fromisoformat(r["day"]) for r in rows}


def _task(row: sqlite3.Row) -> Task:
    return Task(
        id=row["id"],
        title=row["title"],
        created_at=datetime.fromisoformat(row["created_at"]),
        done_at=datetime.fromisoformat(row["done_at"]) if row["done_at"] else None,
    )
