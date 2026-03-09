import pytest

try:
    from app.ml import predictor
except Exception:
    predictor = None


def sample_input():
    return {
        "case_type": "civil",
        "number_of_hearings": 3,
        "judge_workload": 40,
        "document_count": 5,
        "case_priority": "medium",
        "filing_to_first_hearing_days": 20,
        "court_level": "district",
        "previous_adjournments": 1,
    }


def test_predictor_loaded_and_predicts():
    if predictor is None:
        pytest.skip("Model artifact not present or predictor not initialized")
    # predictor should have a predict method
    assert hasattr(predictor, "predict")
    res = predictor.predict(sample_input())
    assert isinstance(res, dict)
    assert "predicted_duration_days" in res
    assert "confidence" in res
    assert "model_version" in res


def test_predictor_response_structure():
    """Validate all required fields in predictor response."""
    if predictor is None:
        pytest.skip("Model artifact not present")
    res = predictor.predict(sample_input())
    # Check all required response fields
    assert res["predicted_duration_days"] > 0
    assert res["predicted_duration_years"] > 0
    assert res.get("risk_level") in ["Low Delay", "Moderate Delay", "High Delay"]
    assert res["model_version"] == "v1"
    assert 0 <= res["confidence"] <= 1
    assert "generated_at" in res
    assert len(res["generated_at"]) > 0


def test_predictor_determinism():
    """Verify same input produces same output."""
    if predictor is None:
        pytest.skip("Model artifact not present")
    data = sample_input()
    res1 = predictor.predict(data)
    res2 = predictor.predict(data)
    # Should be identical
    assert res1["predicted_duration_days"] == res2["predicted_duration_days"]
    assert res1["confidence"] == res2["confidence"]


def test_predictor_with_different_inputs():
    """Test predictor with varied realistic inputs and risk mapping."""
    if predictor is None:
        pytest.skip("Model artifact not present")
    
    # cases expected to fall in each risk bucket
    cases = [
        # low delay scenario
        {"case_type": "civil", "number_of_hearings": 1, "judge_workload": 20,
         "document_count": 2, "case_priority": "low", "filing_to_first_hearing_days": 10,
         "court_level": "magistrate", "previous_adjournments": 0},
        # moderate delay scenario
        {"case_type": "criminal", "number_of_hearings": 5, "judge_workload": 50,
         "document_count": 20, "case_priority": "medium", "filing_to_first_hearing_days": 20,
         "court_level": "district", "previous_adjournments": 2},
        # high delay scenario
        {"case_type": "tax", "number_of_hearings": 7, "judge_workload": 80,
         "document_count": 40, "case_priority": "high", "filing_to_first_hearing_days": 30,
         "court_level": "supreme", "previous_adjournments": 5},
    ]
    
    risks = []
    for case in cases:
        res = predictor.predict(case)
        risks.append(res.get("risk_level"))
        assert res["predicted_duration_days"] > 0
        assert res.get("risk_level") in ["Low Delay", "Moderate Delay", "High Delay"]
    
    # Should cover all three risk levels
    assert set(risks) == {"Low Delay", "Moderate Delay", "High Delay"}

def test_configurable_thresholds():
    """Ensure thresholds can be overridden via Flask config."""
    if predictor is None:
        pytest.skip("Model artifact not present")
    from flask import Flask
    app = Flask(__name__)
    # set thresholds so that sample_input becomes Low Delay
    app.config["LOW_DELAY_THRESHOLD"] = 1000
    app.config["HIGH_DELAY_THRESHOLD"] = 2000
    with app.app_context():
        res = predictor.predict(sample_input())
        assert res["risk_level"] == "Low Delay"


def test_model_info_endpoint(client):
    """Verify the `/ai/model-info` API returns the expected metadata."""
    # create a test JWT without needing a real user in the database
    from flask_jwt_extended import create_access_token
    # identity can be any dict since authorization checks are not relevant here
    import json
    with client.application.app_context():
        # serialize identity so PyJWT doesn't complain (mirrors auth route behaviour)
        token = create_access_token(identity=json.dumps({'id': 1, 'role': 'admin'}))
    headers = {'Authorization': f'Bearer {token}'}
    resp2 = client.get('/ai/model-info', headers=headers)
    assert resp2.status_code == 200
    resp_json = resp2.get_json()
    assert resp_json.get('success') is True
    info = resp_json.get('data', {})
    # basic metadata assertions
    assert info.get('model_version') == 'v1'
    assert 'algorithm' in info
    assert 'features_used' in info
    assert 'training_samples' in info
