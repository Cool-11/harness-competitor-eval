import importlib.util
import json
from pathlib import Path

import pytest


SCRIPT = (Path(__file__).resolve().parents[2] / "experiments"
          / "external-terminal-bench-fix-code-vulnerability"
          / "file-interface-v1" / "prepare_run.py")
spec = importlib.util.spec_from_file_location("external_file_prepare", SCRIPT)
prepare_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(prepare_module)


def test_prepare_freezes_input_and_rejects_reused_run_slot(tmp_path):
    slot = prepare_module.prepare("workbuddy", 1, "test-version", "test-account", tmp_path)
    record = json.loads((slot / "prepare.json").read_text(encoding="utf-8"))
    assert record["status"] == "prepared"
    assert record["inputs_sha256"]["bottle.py"] == prepare_module.sha256(slot / "work" / "bottle.py")
    assert record["prompt_sha256"] == prepare_module.sha256(slot / "prompt.txt")
    assert record["execution_context"]["actual_work_dir"] == "unverified"
    assert record["execution_context"]["requested_work_dir"] == str(slot / "work")
    with pytest.raises(FileExistsError):
        prepare_module.prepare("workbuddy", 1, "test-version", "test-account", tmp_path)


def test_remote_surface_keeps_workdir_unselected(tmp_path):
    slot = prepare_module.prepare("yuanbao", 2, "test-version", "test-account", tmp_path)
    record = json.loads((slot / "prepare.json").read_text(encoding="utf-8"))
    assert record["execution_context"]["actual_work_dir"] == "not_selectable"
    assert not any((slot / "work").iterdir())
