from datetime import date

import pytest

from streaky.db import Store


@pytest.fixture
def store():
    s = Store(":memory:")
    yield s
    s.close()


def test_task_lifecycle(store):
    task = store.add_task("write README")
    assert [t.title for t in store.list_tasks()] == ["write README"]

    store.complete_task(task.id)
    assert store.list_tasks() == []
    assert store.list_tasks(include_done=True)[0].done

    store.remove_task(task.id)
    assert store.list_tasks(include_done=True) == []


def test_missing_task_raises(store):
    with pytest.raises(KeyError):
        store.complete_task(42)


def test_duplicate_habit_rejected(store):
    store.add_habit("read")
    with pytest.raises(ValueError):
        store.add_habit("read")


def test_check_in_is_idempotent(store):
    store.add_habit("read")
    day = date(2026, 11, 5)
    assert store.check_in("read", day) is True
    assert store.check_in("read", day) is False
    assert store.checkin_days("read") == {day}


def test_removing_habit_deletes_checkins(store):
    store.add_habit("read")
    store.check_in("read", date(2026, 11, 5))
    store.remove_habit("read")
    store.add_habit("read")
    assert store.checkin_days("read") == set()
