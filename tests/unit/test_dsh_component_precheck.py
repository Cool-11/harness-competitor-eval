import subprocess
from pathlib import Path

import pytest

from scripts.dsh_component_precheck import precheck


@pytest.mark.parametrize('unexpected', [False, True])
def test_p2_precheck_requires_unique_config_diff(tmp_path: Path, monkeypatch, unexpected: bool) -> None:
    patch = tmp_path / 'patch.yml'
    patch.write_text('disabled: true')
    before = "- id: tool-pwsh\n  disabled: !!js process.platform !== 'win32'\n"
    after = "# patched source\n- id: tool-pwsh\n  disabled: true\n"
    if unexpected:
        after += 'token: SECRET\n'
    outputs = iter([before, after, 'test-version'])
    monkeypatch.setattr(subprocess, 'run', lambda *a, **kw: subprocess.CompletedProcess(a, 0, next(outputs), ''))
    if unexpected:
        with pytest.raises(ValueError) as error:
            precheck('fake', patch)
        assert 'SECRET' not in str(error.value)
    else:
        result = precheck('fake', patch)
        assert result['version'] == 'test-version'
        assert len(result['unique_field_diff']) == 2
