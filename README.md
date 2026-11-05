# streaky

A small terminal tool for tracking to-do tasks and daily habits, with streaks.

streaky is for people who live in the terminal and want a quick way to jot down
tasks and keep daily habits (reading, exercise, practice) going, without
opening an app or creating an account. All data stays on your machine in a
single SQLite file.

## Built with

- Python 3.10+, standard library only (`argparse`, `sqlite3`)
- pytest for tests

## Install

```bash
git clone https://github.com/<your-username>/streaky.git
cd streaky
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
```

## Usage

```console
$ streaky add Renew library books
Added task 1: Renew library books

$ streaky list
[ ]   1  Renew library books

$ streaky done 1
Done: Renew library books

$ streaky habit add read
Tracking habit: read

$ streaky habit check read
Checked in read for 2026-11-05. Current streak: 1

$ streaky habit list
read  ......#  current   1  best   1
```

The `......#` strip shows the last 7 days, oldest first (`#` = checked in).
A streak counts as alive until the end of the day after your last check-in, so
you don't lose it just because you haven't checked in yet today.

Backfill a missed day with `streaky habit check read --date 2026-11-04`.

### Commands

| Command | What it does |
|---|---|
| `streaky add <title>` | Add a task |
| `streaky list [-a]` | List open tasks (`-a` includes finished ones) |
| `streaky done <id>` | Mark a task as done |
| `streaky rm <id>` | Delete a task |
| `streaky habit add <name>` | Start tracking a habit |
| `streaky habit check <name> [--date YYYY-MM-DD]` | Check in for today or a given day |
| `streaky habit list` | Show habits, last 7 days, current and best streak |
| `streaky habit rm <name>` | Stop tracking a habit and delete its history |

## Configuration

The database lives at `~/.local/share/streaky/streaky.db` by default (or under
`$XDG_DATA_HOME`). Override it with the `STREAKY_DB` environment variable or
the `--db` flag. See [.env.example](.env.example).

## Development

```bash
pytest
```

## Roadmap

Planned work is tracked in [ROADMAP.md](ROADMAP.md) and the GitHub issues.

## License

[MIT](LICENSE)
