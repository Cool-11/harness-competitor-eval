import hashlib
import json
from pathlib import Path

import pytest

from scripts.public_evidence_manifest import audit


def test_public_subset_discloses_missing_and_corrupt_evidence(tmp_path: Path) -> None:
    original = b"evidence\r\n"
    for name in ("good", "corrupt"):
        (tmp_path / name).write_bytes(original)
    entries = [{"path": name, "bytes": len(original), "sha256": hashlib.sha256(original).hexdigest()}
               for name in ("good", "corrupt", "missing")]
    manifest = tmp_path / "manifest.json"
    manifest.write_text(json.dumps(entries))
    before = manifest.read_bytes()
    (tmp_path / "corrupt").write_bytes(b"evidence\n")
    result = audit(manifest)
    assert result['verified'] == entries[:1]
    assert result['missing'] == entries[2:]
    assert result['mismatched'][0]['expected'] == entries[1]
    assert result['status'] == 'incomplete'
    assert manifest.read_bytes() == before
    public = audit(manifest, tracked_paths=set())
    assert public['verified'] == []
    assert public['local_only'] == entries[:1]


@pytest.mark.parametrize("paths", [["../outside"], ["same", "same"]])
def test_public_manifest_rejects_unsafe_or_duplicate_paths(tmp_path: Path, paths: list) -> None:
    manifest = tmp_path / "manifest.json"
    manifest.write_text(json.dumps([{"path": p} for p in paths]))
    with pytest.raises(ValueError, match="unsafe or duplicate"):
        audit(manifest)
