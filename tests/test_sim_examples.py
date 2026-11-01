import runpy
from pathlib import Path

from espresso import is_home

EXAMPLES = Path(__file__).resolve().parent.parent / "sim" / "examples"


def test_basic_run(tmp_path, capsys):
    module = runpy.run_path(str(EXAMPLES / "basic_run.py"))
    sim = module["main"](tmp_path / "trace.jsonl")
    assert is_home(sim.state)
    assert (tmp_path / "trace.jsonl").exists()
    assert "eject_grounds" in capsys.readouterr().out
