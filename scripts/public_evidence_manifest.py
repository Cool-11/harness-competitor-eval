"""Derive a verifiable public subset without rewriting historical manifests."""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path


def audit(manifest: Path, tracked_paths: set[Path] | None = None) -> dict:
    entries = json.loads(manifest.read_text(encoding="utf-8"))
    root = manifest.parent.resolve()
    verified, missing, mismatched, local_only = [], [], [], []
    seen = set()
    for entry in entries:
        relative = entry["path"]
        path = (root / relative).resolve()
        if not path.is_relative_to(root) or relative in seen:
            raise ValueError(f"unsafe or duplicate manifest path: {relative}")
        seen.add(relative)
        if not path.is_file():
            missing.append(entry)
        else:
            raw = path.read_bytes()
            actual = {"bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest()}
            if actual != {key: entry[key] for key in actual}:
                mismatched.append({"expected": entry, "actual": actual})
            else:
                if tracked_paths is not None and path not in tracked_paths:
                    local_only.append(entry)
                else:
                    verified.append(entry)
    return {
        "source_manifest_sha256": hashlib.sha256(manifest.read_bytes()).hexdigest(),
        "historical_entries": len(entries), "verified": verified,
        "missing": missing, "mismatched": mismatched,
        "local_only": local_only,
        "status": "complete" if not missing and not mismatched and not local_only else "incomplete",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifests", nargs="+", type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    if args.output.exists():
        parser.error("output exists; choose a new public audit identity")
    result = {}
    for path in args.manifests:
        # A local ignored cache is not part of the public repository archive.
        names = subprocess.check_output(
            ["git", "ls-files", "-z", "--", "."], cwd=path.parent
        ).decode("utf-8").split("\0")
        tracked = {(path.parent / name).resolve() for name in names if name}
        result[path.as_posix()] = audit(path, tracked)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: {"total": val["historical_entries"], "verified": len(val["verified"]),
                            "missing": len(val["missing"]), "local_only": len(val["local_only"]),
                            "mismatched": len(val["mismatched"])}
                      for key, val in result.items()}, ensure_ascii=False))
    # Missing files remain disclosed; corruption is a hard error.
    raise SystemExit(1 if any(val["mismatched"] for val in result.values()) else 0)


if __name__ == "__main__":
    main()
