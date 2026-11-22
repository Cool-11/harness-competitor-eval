"""Recompute ordered-tier agreement without inventing missing reviews or independence."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import Counter
from pathlib import Path


def metrics(pairs: list[tuple[int, int]]) -> dict:
    n = len(pairs)
    if not n:
        return {"paired_cells": 0, "exact_agreement": None, "one_tier_difference": None,
                "quadratic_weighted_kappa": None, "kappa_status": "no_valid_pairs"}
    left, right = Counter(a for a, _ in pairs), Counter(b for _, b in pairs)
    observed = sum((a - b) ** 2 for a, b in pairs) / n
    expected = sum(left[a] * right[b] * (a - b) ** 2 for a in range(4) for b in range(4)) / n ** 2
    return {"paired_cells": n, "exact_agreement": sum(a == b for a, b in pairs) / n,
            "one_tier_difference": sum(abs(a - b) == 1 for a, b in pairs) / n,
            "quadratic_weighted_kappa": 1 - observed / expected if expected else None,
            "kappa_status": "descriptive_small_clustered_sample" if expected else "degenerate_marginals"}


def read_form(path: Path, expected: set[tuple[str, str]]) -> dict:
    rows = {}
    with path.open(encoding="utf-8-sig", newline="") as handle:
        for row in csv.DictReader(handle):
            key = (row['subject'], row['cell'])
            if key in rows or key not in expected:
                raise ValueError(f"duplicate or unexpected review cell: {key}")
            value = row['judgment'].strip()
            row['judgment'] = value
            if value not in {'', '0', '1', '2', '3', 'abstain'}:
                raise ValueError(f"invalid tier: {key}")
            if value and not row.get('rationale', '').strip():
                raise ValueError(f"judgment requires rationale: {key}")
            if value in {'0', '1', '2', '3'} and not row.get('evidence', '').strip():
                raise ValueError(f"tier requires observable evidence: {key}")
            if value == 'abstain' and not row.get('missing', '').strip():
                raise ValueError(f"abstention requires missing evidence reason: {key}")
            rows[key] = row
    if rows.keys() != expected:
        raise ValueError("review must retain all frozen cells, including abstentions")
    return rows


def compare(reference: Path, review: Path, protocol: dict, declaration: dict | None = None) -> dict:
    expected = {(subject, cell) for subject in protocol['subjects'] for cell in protocol['cells']}
    left, right = read_form(reference, expected), read_form(review, expected)
    result = {
        "status": "pending", "expected_cells": len(expected), "run_subjects": len(protocol['subjects']),
        "source_sha256": {"reference": hashlib.sha256(reference.read_bytes()).hexdigest(),
                          "review": hashlib.sha256(review.read_bytes()).hexdigest()},
        "declaration": declaration or {"relationship": "unknown"},
        "independence_verified": False,
        "pending": {"reference": sum(not r['judgment'].strip() for r in left.values()),
                    "review": sum(not r['judgment'].strip() for r in right.values())},
        "abstain": {"reference": sum(r['judgment'] == 'abstain' for r in left.values()),
                    "review": sum(r['judgment'] == 'abstain' for r in right.values())},
        "overall": None, "by_dimension": {}, "disagreements": [],
    }
    # Do not publish attractive partial agreement while unfilled hard cases remain.
    if any(result['pending'].values()):
        return result
    pairs, by_dimension = [], {}
    for key in sorted(expected):
        a, b = left[key]['judgment'], right[key]['judgment']
        if a != b:
            result['disagreements'].append({"subject": key[0], "cell": key[1],
                                            "reference": left[key], "review": right[key]})
        if a != 'abstain' and b != 'abstain':
            pair = (int(a), int(b))
            pairs.append(pair)
            by_dimension.setdefault(protocol['cells'][key[1]], []).append(pair)
    result['status'] = 'computed_not_adjudicated'
    result['overall'] = metrics(pairs)
    result['by_dimension'] = {dimension: metrics(by_dimension.get(dimension, []))
                              for dimension in sorted(set(protocol['cells'].values()))}
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--reference', type=Path, required=True)
    parser.add_argument('--review', type=Path, required=True)
    parser.add_argument('--protocol', type=Path, required=True)
    parser.add_argument('--declaration', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        parser.error('output exists; preserve prior review results')
    protocol = json.loads(args.protocol.read_text(encoding='utf-8'))
    for entry in protocol.get('frozen_sources', []):
        path = args.protocol.parent / entry['path']
        if hashlib.sha256(path.read_bytes()).hexdigest() != entry['sha256']:
            parser.error(f'frozen review anchor changed: {entry["path"]}')
    declaration = json.loads(args.declaration.read_text(encoding='utf-8')) if args.declaration else None
    result = compare(args.reference, args.review, protocol, declaration)
    result['protocol_sha256'] = hashlib.sha256(args.protocol.read_bytes()).hexdigest()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(result['status'])


if __name__ == '__main__':
    main()
