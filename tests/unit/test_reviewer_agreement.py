import csv

import pytest

from scripts.reviewer_agreement import compare, metrics


def form(path, values):
    with path.open('w', newline='', encoding='utf-8') as handle:
        writer = csv.DictWriter(handle, fieldnames=['subject', 'cell', 'judgment', 'evidence', 'rationale', 'missing'])
        writer.writeheader()
        for i, value in enumerate(values):
            writer.writerow(dict(subject=str(i), cell='D3-1', judgment=value, evidence='event#1',
                                 rationale='anchor', missing='not visible' if value == 'abstain' else ''))
    return path


def test_ordered_kappa_and_degenerate_marginals():
    assert metrics([(0, 0), (1, 1), (2, 2), (3, 3)])['quadratic_weighted_kappa'] == 1
    result = metrics([(0, 3), (3, 0)])
    assert result['quadratic_weighted_kappa'] == -1
    assert metrics([(3, 3)])['quadratic_weighted_kappa'] is None
    assert metrics([])['exact_agreement'] is None


def test_pending_and_abstention_are_never_zero(tmp_path):
    protocol = {'subjects': ['0', '1', '2'], 'cells': {'D3-1': 'D3'}}
    reference = form(tmp_path / 'reference.csv', ['0', '1', '3'])
    review = form(tmp_path / 'review.csv', ['0', '', 'abstain'])
    pending = compare(reference, review, protocol)
    assert pending['status'] == 'pending' and pending['overall'] is None
    review = form(review, ['0', '2', 'abstain'])
    result = compare(reference, review, protocol)
    assert result['overall']['paired_cells'] == 2
    assert result['overall']['exact_agreement'] == .5
    assert result['abstain']['review'] == 1
    assert len(result['disagreements']) == 2
    assert not result['independence_verified']


def test_cannot_drop_hard_cases(tmp_path):
    protocol = {'subjects': ['0', '1'], 'cells': {'D3-1': 'D3'}}
    reference = form(tmp_path / 'reference.csv', ['0', '1'])
    review = form(tmp_path / 'review.csv', ['0'])
    with pytest.raises(ValueError, match='all frozen cells'):
        compare(reference, review, protocol)
