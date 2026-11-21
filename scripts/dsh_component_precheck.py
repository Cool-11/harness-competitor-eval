"""Local P2 seam check: dump merged configuration without calling a model."""
from __future__ import annotations

import argparse
import difflib
import hashlib
import json
import os
import subprocess
from pathlib import Path


def precheck(executable: str, patch: Path) -> dict:
    base = [executable, "--profile", "headless", "--dump-config"]
    outputs = []
    for command in (base, base + ["--patch", str(patch.resolve())]):
        result = subprocess.run(command, capture_output=True, encoding="utf-8", check=True, timeout=60)
        # Source comments vary with patch provenance, not the loaded fields.
        outputs.append([line for line in result.stdout.splitlines() if not line.startswith('#')])
    changed = [line for line in difflib.ndiff(*outputs) if line.startswith(('- ', '+ '))]
    expected = ["-   disabled: !!js process.platform !== 'win32'", "+   disabled: true"]
    if changed != expected:
        # Do not print arbitrary config differences: they may contain credentials.
        raise ValueError("P2 precheck failed: merged config differs beyond the expected tool-pwsh field")
    version = subprocess.run([executable, '--version'], capture_output=True, encoding='utf-8', check=True, timeout=30)
    return {
        "status": "merged_configuration_verified_not_a_product_run",
        "version": version.stdout.strip(), "profile": "headless", "platform": os.name,
        "patch_sha256": hashlib.sha256(patch.read_bytes()).hexdigest(),
        "unique_field_diff": changed,
        "config_fingerprints_lf": [hashlib.sha256('\n'.join(lines).encode()).hexdigest() for lines in outputs],
        "runtime_effect": "requires native request tool list; dump-config retains JS expressions",
        "restoration": "omit patch; reuse baseline configuration with a new run_id",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--executable', default='dsh.cmd' if os.name == 'nt' else 'dsh')
    parser.add_argument('--patch', type=Path, default=Path('scripts/patches/swap-P2-no-pwsh.yml'))
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        parser.error('output exists; choose a new precheck identity')
    result = precheck(args.executable, args.patch)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(result['status'])


if __name__ == '__main__':
    main()
