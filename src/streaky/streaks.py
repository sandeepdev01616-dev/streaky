"""Streak calculations over a set of check-in days."""

from __future__ import annotations

from datetime import date, timedelta


def current_streak(days: set[date], today: date | None = None) -> int:
    """Consecutive days ending today, or yesterday if today isn't checked yet."""
    today = today or date.today()
    cursor = today if today in days else today - timedelta(days=1)
    streak = 0
    while cursor in days:
        streak += 1
        cursor -= timedelta(days=1)
    return streak


def longest_streak(days: set[date]) -> int:
    longest = run = 0
    prev: date | None = None
    for day in sorted(days):
        run = run + 1 if prev is not None and day - prev == timedelta(days=1) else 1
        longest = max(longest, run)
        prev = day
    return longest


def last_n_days(days: set[date], n: int = 7, today: date | None = None) -> str:
    """A compact strip like '##.#..#' for the last n days, oldest first."""
    today = today or date.today()
    return "".join(
        "#" if today - timedelta(days=offset) in days else "."
        for offset in range(n - 1, -1, -1)
    )
