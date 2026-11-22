#!/usr/bin/env python3
"""Filter data.csv according to config.json.

Tolerates configs that are not strict JSON (e.g. dangling or missing commas
left behind by hand-editing): the damage is repaired, the config re-parsed,
and the clean form written back. Repairs are reported on stderr.

Usage: python filter.py [config] [data] [out]
"""
import csv
import json
import re
import sys

CONFIG, DATA, OUT = "config.json", "data.csv", "filtered.csv"

OPS = {
    "gt":  (">",  lambda v, t: v > t),
    "gte": (">=", lambda v, t: v >= t),
    "lt":  ("<",  lambda v, t: v < t),
    "lte": ("<=", lambda v, t: v <= t),
    "eq":  ("==", lambda v, t: v == t),
    "ne":  ("!=", lambda v, t: v != t),
}


def _repair(text):
    """Common hand-editing damage: dangling commas, and missing commas
    between sibling members that sit on separate lines."""
    text = re.sub(r",(\s*[}\]])", r"\1", text)                      # trailing commas
    text = re.sub(r'(?<=[}\]"\d])(?<!,)\s*\n(\s*)(?=")', r",\n\1", text)  # missing commas
    return text


def load_config(path):
    raw = open(path, encoding="utf-8").read()
    try:
        return json.loads(raw), False
    except json.JSONDecodeError as exc:
        text, last = raw, exc
        for _ in range(5):
            text = _repair(text)
            try:
                cfg = json.loads(text)
            except json.JSONDecodeError as again:
                last = again
                continue
            print("note: %s was not valid JSON (%s); recovered" % (path, exc),
                  file=sys.stderr)
            return cfg, True
        raise SystemExit("%s is corrupt and could not be recovered: %s" % (path, last))


def main():
    config_path = sys.argv[1] if len(sys.argv) > 1 else CONFIG
    data_path = sys.argv[2] if len(sys.argv) > 2 else DATA
    out_path = sys.argv[3] if len(sys.argv) > 3 else OUT

    cfg, recovered = load_config(config_path)
    if recovered:
        with open(config_path, "w", encoding="utf-8", newline="\n") as f:
            json.dump(cfg, f, ensure_ascii=False, indent=2)
            f.write("\n")

    threshold = float(cfg["threshold"])
    columns = cfg["columns"]
    mode = cfg.get("mode", "gt")
    if mode not in OPS:
        raise SystemExit("unsupported mode %r (expected one of %s)"
                         % (mode, ", ".join(OPS)))
    symbol, predicate = OPS[mode]
    keep = lambda v, _p=predicate: _p(v, threshold)

    with open(data_path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    missing = [c for c in columns if c not in reader.fieldnames]
    if missing:
        raise SystemExit("columns not found in %s: %s" % (data_path, ", ".join(missing)))

    selected = [r for r in rows if keep(float(r["amount"]))]  # input order kept

    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=columns)
        writer.writeheader()
        writer.writerows({c: r[c] for c in columns} for r in selected)

    print("filter: amount %s %g -> kept %d/%d rows"
          % (symbol, threshold, len(selected), len(rows)), file=sys.stderr)
    for r in selected:
        print(",".join(str(r[c]) for c in columns))


if __name__ == "__main__":
    main()
