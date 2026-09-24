import json
from unittest.mock import Mock
import pytest
import requests
import llm
from examples import DEMO

def response(data=None, code=200):
    return Mock(status_code=code, json=Mock(return_value=data))

def test_success_and_secret_isolation(monkeypatch):
    envelope = {"status": "completed", "steps": [{"type": "thought", "content": [{"type": "text", "text": "internal"}]},
        {"type": "model_output", "content": [{"type": "text", "text": json.dumps(DEMO)}]}]}
    post = Mock(return_value=response(envelope))
    monkeypatch.setattr(llm.requests, "post", post)
    assert llm.generate_spec("input", "test-only-secret") == DEMO
    args = post.call_args.kwargs
    assert "test-only-secret" not in json.dumps(args["json"])
    assert args["headers"]["x-goog-api-key"] == "test-only-secret"
    assert args["json"]["store"] is False
    assert args["allow_redirects"] is False

@pytest.mark.parametrize("code", [400, 401, 403, 404, 429, 500, 302])
def test_errors_are_sanitized(monkeypatch, code):
    monkeypatch.setattr(llm.requests, "post", Mock(return_value=response({"secret": "NEVER_EXPOSE"}, code)))
    with pytest.raises(llm.ModelError) as error: llm.generate_spec("input", "test-only-secret")
    assert "NEVER_EXPOSE" not in str(error.value)

@pytest.mark.parametrize("exception", [requests.Timeout, requests.ConnectionError])
def test_network_errors(monkeypatch, exception):
    monkeypatch.setattr(llm.requests, "post", Mock(side_effect=exception("NEVER_EXPOSE")))
    with pytest.raises(llm.ModelError): llm.generate_spec("input", "test-only-secret")

@pytest.mark.parametrize("data", [{}, {"status": "failed"}, {"status": "completed", "steps": []},
    {"status": "completed", "steps": [{"type": "model_output", "content": [{"type": "text", "text": "not json"}]}]}])
def test_invalid_response(monkeypatch, data):
    monkeypatch.setattr(llm.requests, "post", Mock(return_value=response(data)))
    with pytest.raises(llm.ModelError): llm.generate_spec("input", "test-only-secret")

def test_missing_key_never_calls_network(monkeypatch):
    post = Mock()
    monkeypatch.setattr(llm.requests, "post", post)
    with pytest.raises(llm.ModelError): llm.generate_spec("input", "")
    post.assert_not_called()
