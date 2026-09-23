from fastapi.testclient import TestClient
from pathlib import Path
import sys

for key in list(sys.modules.keys()):
    if key == 'app' or key.startswith('app.'):
        del sys.modules[key]

service_dir = str(Path(__file__).resolve().parent.parent)
sys.path.insert(0, service_dir)

from app.main import app

client = TestClient(app)


def test_required_training_modules_are_available():
    response = client.get('/api/v1/training/modules')
    assert response.status_code == 200
    modules = response.json()
    ids = {m['module_id'] for m in modules}
    assert {'SAFE_START_01', 'PROXIMITY_RESPONSE_01', 'IDLE_EFFICIENCY_01', 'DECISION_AWARENESS_01'} <= ids

    safe = next(m for m in modules if m['module_id'] == 'SAFE_START_01')
    assert 'objective' in safe
    assert 'estimated_minutes' in safe
    assert 'skills' in safe
    assert 'steps' in safe


def test_attempt_scoring_uses_deterministic_fields():
    payload = {
        'operator_id': 'OP1001',
        'module_id': 'SAFE_START_01',
        'score': 82,
        'max_score': 100,
        'mistakes': 2,
        'started_at': '2026-09-23T07:30:00Z',
        'completed_at': '2026-09-23T07:35:00Z'
    }
    response = client.post('/api/v1/training/attempts', json=payload)
    assert response.status_code == 201
    body = response.json()
    assert 'attempt_id' in body
    assert body['module_id'] == 'SAFE_START_01'
    assert body['percentage'] == 82.0
    assert body['passed'] is True
    assert body['status'] == 'COMPLETED'


def test_attempt_scoring_failure_deterministic():
    payload = {
        'operator_id': 'OP1001',
        'module_id': 'SAFE_START_01',
        'score': 65,
        'max_score': 100,
        'mistakes': 3,
        'started_at': '2026-09-23T07:30:00Z',
        'completed_at': '2026-09-23T07:35:00Z'
    }
    response = client.post('/api/v1/training/attempts', json=payload)
    assert response.status_code == 201
    body = response.json()
    assert body['passed'] is False
    assert body['percentage'] == 65.0


def test_all_modules_have_scenario_steps():
    for mod_id in ['SAFE_START_01', 'PROXIMITY_RESPONSE_01', 'IDLE_EFFICIENCY_01', 'DECISION_AWARENESS_01']:
        res = client.get(f'/api/v1/training/modules/{mod_id}')
        assert res.status_code == 200
        data = res.json()
        assert len(data['scenario_steps']) >= 3
        for step in data['scenario_steps']:
            assert 'step_number' in step
            assert 'prompt' in step
            assert len(step['choices']) >= 2
            assert any(c['is_correct'] for c in step['choices'])


def test_recommendations_consume_contextual_signals():
    for sig, expected_mod in [
        ('seatbelt violation', 'SAFE_START_01'),
        ('proximity event', 'PROXIMITY_RESPONSE_01'),
        ('high idle', 'IDLE_EFFICIENCY_01'),
        ('decision-related pattern', 'DECISION_AWARENESS_01'),
    ]:
        res = client.get(f'/api/v1/training/recommendations/OP1001?signal={sig}')
        assert res.status_code == 200
        recs = res.json()
        assert len(recs) >= 1
        assert recs[0]['module_id'] == expected_mod
        assert 'reason' in recs[0]
        assert len(recs[0]['reason']) > 10
