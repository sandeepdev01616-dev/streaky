# Roadmap

Rough plan for streaky. Estimates are approximate.

## v0.2: Better tasks (~8h)
- [ ] Due dates (`streaky add "pay rent" --due 2026-12-01`) and an overdue view
- [ ] Priorities and sorting (`--priority high`)
- [ ] Tags/projects (`+home`, `@work`-style) with filtering in `list`
- [ ] Edit a task's title in place (`streaky edit <id> <new title>`)

## v0.3: Better habits (~8h)
- [ ] Weekly targets (e.g. "gym 3x per week") with streaks counted in weeks
- [ ] Undo a check-in (`streaky habit uncheck`)
- [ ] Monthly calendar heatmap view in the terminal
- [ ] Archive habits instead of deleting history

## v0.4: Data and output (~6h)
- [ ] Export / import as JSON and CSV
- [ ] `--json` output flag for scripting
- [ ] Colored output with `NO_COLOR` support
- [ ] Schema migrations so upgrades never lose data

## v0.5: Daily workflow (~6h)
- [ ] `streaky today` summary: open tasks plus habits not yet checked
- [ ] Shell completions (bash, zsh, fish)
- [ ] Optional desktop reminder via a cron/systemd timer snippet

## Project hygiene (~4h)
- [ ] GitHub Actions CI running tests on Python 3.10–3.13
- [ ] Lint and format with ruff
- [ ] Publish to PyPI so it installs with `pipx install streaky`
- [ ] Man page / `--help` examples
