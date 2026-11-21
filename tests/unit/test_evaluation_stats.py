import pytest

from scripts.evaluation_stats import paired_task_effect, wilson


def test_wilson_fixed_ten_case_acceptance_is_wide():
    assert wilson(7, 10) == pytest.approx([0.3967781475, 0.8922087326])
    assert wilson(0, 0) is None
    assert wilson(0, 10)[0] == pytest.approx(0)
    assert wilson(10, 10)[1] == pytest.approx(1)


def test_paired_effect_retains_task_weights_and_refuses_unknown():
    rows = [{'task': 'A', 'pair_id': str(i), 'baseline': 0, 'intervention': 1} for i in range(9)]
    rows += [{'task': 'B', 'pair_id': 'b', 'baseline': 1, 'intervention': 0},
             {'task': 'C', 'pair_id': 'c', 'baseline': 0, 'intervention': 0}]
    result = paired_task_effect(rows, seed=42, draws=1000)
    assert result['effect'] == 0  # Per-task weights, not 8/11 from unequal run counts.
    assert result == paired_task_effect(rows, seed=42, draws=1000)
    assert paired_task_effect(rows[:2], seed=42)['confidence_interval'] is None
    with pytest.raises(ValueError, match='binary'):
        paired_task_effect([dict(rows[0], intervention=None)], seed=42)
    with pytest.raises(ValueError, match='duplicate'):
        paired_task_effect([rows[0], rows[0]], seed=42)
