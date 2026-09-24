"""Cliente REST Gemini. Solo el servidor conoce la API key."""
import json
import re
import requests
from core import SPEC_SCHEMA, SYSTEM_PROMPT, validate_spec

API_URL = "https://generativelanguage.googleapis.com/v1beta/interactions"
DEFAULT_MODEL = "gemini-3.5-flash-lite"

class ModelError(Exception):
    """Error apto para mostrar, sin respuesta cruda ni credenciales."""

def generate_spec(prompt: str, api_key: str, model: str = DEFAULT_MODEL) -> dict:
    if not api_key or api_key == "REEMPLAZAR_EN_STREAMLIT":
        raise ModelError("Falta configurar GEMINI_API_KEY en los secretos del servidor.")
    if not re.fullmatch(r"gemini-[a-zA-Z0-9.\-]{1,70}", model):
        raise ModelError("El identificador GEMINI_MODEL no es válido.")
    payload = {
        "model": model, "system_instruction": SYSTEM_PROMPT, "input": prompt,
        "store": False,
        "generation_config": {"max_output_tokens": 6000},
        "response_format": {"type": "text", "mime_type": "application/json", "schema": SPEC_SCHEMA},
    }
    try:
        response = requests.post(API_URL, json=payload,
            headers={"x-goog-api-key": api_key, "Content-Type": "application/json"},
            timeout=(10, 60), allow_redirects=False)
    except requests.Timeout:
        raise ModelError("El modelo tardó demasiado. Esperá unos segundos y volvé a intentar.") from None
    except requests.RequestException:
        raise ModelError("No se pudo conectar con el proveedor de IA. Intentá más tarde.") from None
    messages = {
        400: "El proveedor rechazó la solicitud. Revisá la clave, el modelo y su compatibilidad.",
        401: "La clave de IA no es válida. Revisá los secretos de Streamlit.",
        403: "La cuenta no tiene permiso para usar este modelo.",
        404: "El modelo configurado no está disponible. Revisá GEMINI_MODEL.",
        429: "Se alcanzó la cuota del proveedor. Esperá o revisá los límites de tu cuenta.",
    }
    if response.status_code != 200:
        raise ModelError(messages.get(response.status_code, "El proveedor de IA no está disponible en este momento."))
    try:
        envelope = response.json()
        if envelope.get("status") != "completed":
            raise ValueError("incomplete")
        pieces = [item["text"] for step in envelope.get("steps", [])
                  if step.get("type") == "model_output"
                  for item in step.get("content", []) if item.get("type") == "text"]
        raw = "".join(pieces)
        if not raw or len(raw) > 100_000:
            raise ValueError("invalid size")
        return validate_spec(json.loads(raw))
    except (ValueError, TypeError, KeyError, AttributeError):
        raise ModelError("La IA devolvió una respuesta incompleta o inconsistente. Probá con una descripción más concreta.") from None
