"""Descriptive uncertainty helpers; never convert unknown outcomes to failures."""
from __future__ import annotations

import math
import random
from collections import defaultdict
from statistics import NormalDist, mean


def wilson(successes: int, total: int, confidence: float = 0.95) -> list[float] | None:
    if (type(successes) is not int or type(total) is not int
            or not 0 <= successes <= total or not 0 < confidence < 1):
        raise ValueError('invalid binomial counts or confidence')
    if total == 0:
        return None
    z = NormalDist().inv_cdf((1 + confidence) / 2)
    p, z2 = successes / total, z * z
    center = (p + z2 / (2 * total)) / (1 + z2 / total)
    half = z * math.sqrt(p * (1 - p) / total + z2 / (4 * total ** 2)) / (1 + z2 / total)
    return [max(0.0, center - half), min(1.0, center + half)]


def paired_task_effect(rows: list[dict], *, seed: int, draws: int = 10000) -> dict:
    """Equal task weights; cluster-bootstrap task means of paired C1-C0 outcomes.

    Only frozen matched pairs of adjudicated 0/1 outcomes belong here. Callers
    must report excluded/unknown/invalid counts separately. No imputation occurs.
    """
    if type(draws) is not int or draws < 1000:
        raise ValueError('at least 1000 bootstrap draws required')
    grouped, seen = defaultdict(list), set()
    for row in rows:
        key = (row['task'], row['pair_id'])
        if key in seen or not all(isinstance(x, str) and x for x in key):
            raise ValueError('duplicate or missing paired identity')
        if any(type(row[k]) is not int or row[k] not in {0, 1} for k in ('baseline', 'intervention')):
            raise ValueError('only adjudicated binary outcomes; unknown/invalid are not zero')
        seen.add(key)
        grouped[row['task']].append(row['intervention'] - row['baseline'])
    means = [mean(values) for _, values in sorted(grouped.items())]
    result = {'tasks': len(means), 'pairs': len(rows), 'analysis_unit': 'task_equal_weight_paired_difference',
              'effect': mean(means) if means else None, 'confidence_interval': None,
              'method': 'task_cluster_percentile_bootstrap', 'seed': seed, 'draws': draws,
              'status': 'insufficient_task_clusters'}
    if len(means) < 3:
        return result
    generator = random.Random(seed)
    samples = sorted(mean(generator.choices(means, k=len(means))) for _ in range(draws))
    # Fixed empirical percentile convention, declared for deterministic reanalysis.
    result.update(confidence_interval=[samples[math.floor(.025 * (draws - 1))],
                                       samples[math.ceil(.975 * (draws - 1))]],
                  confidence=.95, status='descriptive_small_sample_no_causal_certification')
    return result
