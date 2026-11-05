from datetime import date, timedelta

from streaky.streaks import current_streak, last_n_days, longest_streak

TODAY = date(2026, 11, 5)


def days_ago(*offsets):
    return {TODAY - timedelta(days=o) for o in offsets}


def test_current_streak_includes_today():
    assert current_streak(days_ago(0, 1, 2), today=TODAY) == 3


def test_current_streak_survives_until_today_is_checked():
    assert current_streak(days_ago(1, 2), today=TODAY) == 2


def test_current_streak_broken():
    assert current_streak(days_ago(2, 3), today=TODAY) == 0


def test_current_streak_empty():
    assert current_streak(set(), today=TODAY) == 0


def test_longest_streak():
    assert longest_streak(days_ago(0, 1, 5, 6, 7, 8, 20)) == 4
    assert longest_streak(set()) == 0


def test_last_n_days():
    assert last_n_days(days_ago(0, 2, 6), n=7, today=TODAY) == "#...#.#"
