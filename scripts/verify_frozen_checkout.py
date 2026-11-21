"""Verify the frozen pilot in real LF/CRLF Git checkouts of a minimal audit snapshot."""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]


def verify() -> dict:
    relative = Path('experiments/autorubric/pilot-2026-10-30')
    frozen = json.loads((REPO / relative / 'sources.json').read_text(encoding='utf-8'))
    with tempfile.TemporaryDirectory(prefix='harness-frozen-checkout-') as temporary:
        root = Path(temporary).resolve()
        origin = root / 'origin'
        origin.mkdir()
        files = [Path('.gitattributes'), Path('scripts/autorubric_export.py'), relative / 'sources.json']
        for entry in frozen['sources']:
            files.extend([Path(entry['source']), relative / 'snapshots-v1' / f"{entry['sha256']}.bin"])
        for name in files:
            target = origin / name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(REPO / name, target)
        def git(*args, cwd=origin):
            return subprocess.run(['git', '-c', f'core.hooksPath={root / "no-hooks"}', *args],
                                  cwd=cwd, capture_output=True, text=True, check=True)
        git('init', '-q')
        git('config', 'core.autocrlf', 'input')
        git('add', '-f', '.')
        git('-c', 'user.name=Local audit', '-c', 'user.email=local-audit@invalid',
            '-c', 'commit.gpgsign=false', 'commit', '-qm', 'Scoped frozen checkout verification')
        results = []
        for autocrlf in ('false', 'true'):
            checkout = root / f'checkout-{autocrlf}'
            git('-c', f'core.autocrlf={autocrlf}', 'clone', '-q', '--no-local', str(origin), str(checkout))
            subprocess.run([sys.executable, str(checkout / 'scripts/autorubric_export.py'),
                            '--repo-root', str(checkout), '--out', str(root / f'export-{autocrlf}')],
                           capture_output=True, text=True, check=True)
            manifest = json.loads((root / f'export-{autocrlf}/manifest.json').read_text(encoding='utf-8'))
            raw = (checkout / frozen['sources'][0]['source']).read_bytes()
            assert (b'\r\n' in raw) == (autocrlf == 'true')
            assert manifest['signed_runs'] == 10 and manifest['cells'] == 40
            results.append({'core.autocrlf': autocrlf, 'grade_newline': 'CRLF' if autocrlf == 'true' else 'LF',
                            'signed_runs': manifest['signed_runs'], 'cells': manifest['cells'], 'passed': True})
    return {'status': 'passed', 'scope': 'minimal_frozen_export_snapshot_not_full_repository_clone',
            'product_runs': 0, 'checkouts': results}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        parser.error('output exists; preserve prior verification')
    result = verify()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(result['status'])


if __name__ == '__main__':
    main()
