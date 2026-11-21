import copy

import pytest

from scripts.mechanism_contract import FIELDS, validate_contract, verify_observed


def contract():
    value = {key: 'unit-frozen' for key in FIELDS}
    value.update(component='tool-pwsh', arm='C1', skills='disabled', memory='disabled',
                 sampling='provider_default', primary_endpoint='task_success',
                 baseline_config_id='baseline', intervention_config_id='intervention',
                 baseline_tools=['pwsh', 'read', 'write'], intervention_tools=['read', 'write'],
                 configuration_sha256={'C0': 'a' * 64, 'C1': 'b' * 64},
                 budget={'max_runs': 3, 'timeout_seconds': 600, 'max_tokens': 1000, 'max_cost': 1})
    return value


def test_single_tool_change_and_runtime_effectiveness():
    value = contract()
    assert validate_contract(value) == []
    observed = {key: value[key] for key in ('model', 'provider', 'reasoning', 'sampling', 'permissions')}
    observed.update(tools=['read', 'write'], source='native session event#1')
    assert verify_observed(value, observed) == []
    assert verify_observed(value, dict(observed, tools=['read', 'write', 'pwsh']))
    assert verify_observed(value, dict(observed, model='different-model'))
    restored = dict(value, arm='C0-restored')
    assert verify_observed(restored, dict(observed, tools=value['baseline_tools'])) == []


@pytest.mark.parametrize('field,value', [('memory', 'unknown'), ('component', 'telemetry'),
                                      ('arm', 'B'), ('intervention_tools', ['read'])])
def test_rejects_uncontrolled_or_inactive_interventions(field, value):
    target = copy.deepcopy(contract())
    target[field] = value
    assert validate_contract(target)
