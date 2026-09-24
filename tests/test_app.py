from pathlib import Path
from unittest.mock import patch
from streamlit.testing.v1 import AppTest
from examples import DEMO

APP = str(Path(__file__).resolve().parents[1] / "app.py")

def test_missing_key_and_preview(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "")
    at = AppTest.from_file(APP).run(timeout=20)
    assert not at.exception
    assert at.button[-1].disabled
    at.radio[0].set_value("Ver ejemplo sin conexión").run()
    assert not at.exception
    assert at.metric[0].value == "2"
    assert "fija" in at.info[0].value

def test_generation_flow_with_mock(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "test-only-secret")
    with patch("llm.generate_spec", return_value=DEMO) as generate:
        at = AppTest.from_file(APP).run(timeout=20)
        at.text_area[0].set_value("Quiero una app para gestionar los turnos de una peluquería.")
        at.button[-1].click().run(timeout=20)
        assert not at.exception
        assert generate.call_count == 1
        assert at.metric[1].value == "4"
        assert at.session_state["result"]["origin"] == "Generado con Gemini"

def test_empty_input_does_not_call_model(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "test-only-secret")
    with patch("llm.generate_spec") as generate:
        at = AppTest.from_file(APP).run(timeout=20)
        at.button[-1].click().run()
        assert at.error
        generate.assert_not_called()
