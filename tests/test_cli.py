from streaky.cli import main


def run(tmp_path, capsys, *args):
    code = main(["--db", str(tmp_path / "test.db"), *args])
    out, err = capsys.readouterr()
    return code, out, err


def test_add_and_list_tasks(tmp_path, capsys):
    run(tmp_path, capsys, "add", "buy", "milk")
    code, out, _ = run(tmp_path, capsys, "list")
    assert code == 0
    assert "buy milk" in out


def test_done_unknown_task_errors(tmp_path, capsys):
    code, _, err = run(tmp_path, capsys, "done", "99")
    assert code == 1
    assert "no task with id 99" in err


def test_habit_check_and_list(tmp_path, capsys):
    run(tmp_path, capsys, "habit", "add", "stretch")
    code, out, _ = run(tmp_path, capsys, "habit", "check", "stretch")
    assert code == 0
    assert "Current streak: 1" in out

    _, out, _ = run(tmp_path, capsys, "habit", "list")
    assert "stretch" in out
    assert "current   1" in out
