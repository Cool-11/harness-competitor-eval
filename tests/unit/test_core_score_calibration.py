from scripts.core_score_calibration import calibrate


def test_calibration_exposes_semantic_false_positives_without_rescoring() -> None:
    result = calibrate()
    scores = {(row['task'][:3], row['case']): row['checker_score'] for row in result['results']}
    assert scores['S06', 'golden'] == 7
    assert scores['S06', 'partial'] == 5.5
    assert scores['S06', 'unsupported_addition'] == 7
    assert scores['S06', 'keywords_only'] == 7
    assert scores['S06', 'omission'] < 7
    assert scores['S06', 'equivalent'] == 7
    assert scores['S11', 'golden'] == 7
    assert scores['S11', 'partial'] == scores['S11', 'tampered'] == 6
    assert result['independent_review'] == 'pending'
