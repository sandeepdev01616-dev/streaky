"""Command-line interface."""

from __future__ import annotations

import argparse
import sys
from datetime import date

from streaky import __version__
from streaky.db import Store
from streaky.streaks import current_streak, last_n_days, longest_streak


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="streaky", description="Track tasks, habits and streaks."
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    parser.add_argument("--db", help="path to the database file (default: $STREAKY_DB)")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("add", help="add a task")
    p.add_argument("title", nargs="+")

    p = sub.add_parser("list", help="list open tasks")
    p.add_argument("-a", "--all", action="store_true", help="include finished tasks")

    p = sub.add_parser("done", help="mark a task as done")
    p.add_argument("id", type=int)

    p = sub.add_parser("rm", help="delete a task")
    p.add_argument("id", type=int)

    habit = sub.add_parser("habit", help="manage habits")
    hsub = habit.add_subparsers(dest="habit_command", required=True)

    p = hsub.add_parser("add", help="start tracking a habit")
    p.add_argument("name")

    p = hsub.add_parser("check", help="check in a habit for today (or --date)")
    p.add_argument("name")
    p.add_argument("--date", type=date.fromisoformat, help="YYYY-MM-DD")

    p = hsub.add_parser("rm", help="stop tracking a habit and delete its history")
    p.add_argument("name")

    hsub.add_parser("list", help="show habits with their streaks")

    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    store = Store(args.db)
    try:
        return _dispatch(store, args)
    except (KeyError, ValueError) as exc:
        message = exc.args[0] if exc.args else str(exc)
        print(f"streaky: {message}", file=sys.stderr)
        return 1
    finally:
        store.close()


def _dispatch(store: Store, args: argparse.Namespace) -> int:
    if args.command == "add":
        task = store.add_task(" ".join(args.title))
        print(f"Added task {task.id}: {task.title}")
    elif args.command == "list":
        tasks = store.list_tasks(include_done=args.all)
        if not tasks:
            print("No tasks.")
        for task in tasks:
            mark = "x" if task.done else " "
            print(f"[{mark}] {task.id:>3}  {task.title}")
    elif args.command == "done":
        task = store.complete_task(args.id)
        print(f"Done: {task.title}")
    elif args.command == "rm":
        store.remove_task(args.id)
        print(f"Removed task {args.id}")
    elif args.command == "habit":
        return _habit(store, args)
    return 0


def _habit(store: Store, args: argparse.Namespace) -> int:
    if args.habit_command == "add":
        habit = store.add_habit(args.name)
        print(f"Tracking habit: {habit.name}")
    elif args.habit_command == "check":
        day = args.date or date.today()
        if store.check_in(args.name, day):
            streak = current_streak(store.checkin_days(args.name))
            print(f"Checked in {args.name} for {day}. Current streak: {streak}")
        else:
            print(f"{args.name} was already checked in for {day}.")
    elif args.habit_command == "rm":
        store.remove_habit(args.name)
        print(f"Removed habit {args.name}")
    elif args.habit_command == "list":
        habits = store.list_habits()
        if not habits:
            print("No habits yet. Add one with: streaky habit add <name>")
        width = max((len(h.name) for h in habits), default=0)
        for habit in habits:
            days = store.checkin_days(habit.name)
            print(
                f"{habit.name:<{width}}  {last_n_days(days)}  "
                f"current {current_streak(days):>3}  best {longest_streak(days):>3}"
            )
    return 0
