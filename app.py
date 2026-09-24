"""SpecPilot IA · Streamlit entrypoint."""
import json
import os
import time
from datetime import datetime, timezone
import streamlit as st
from core import MAX_INPUT, PROMPT_VERSION, SYSTEM_PROMPT, build_prompt, to_markdown, validate_spec
from examples import DEMO, IDEAS
from llm import DEFAULT_MODEL, ModelError, generate_spec

st.set_page_config(page_title="SpecPilot IA", page_icon="🧩", layout="wide")

def setting(name, default=""):
    value = os.environ.get(name)
    if value is not None:
        return value.strip()
    try:
        return str(st.secrets.get(name, default)).strip()
    except (FileNotFoundError, st.errors.StreamlitSecretNotFoundError):
        return default

api_key = setting("GEMINI_API_KEY")
model = setting("GEMINI_MODEL", DEFAULT_MODEL)
configured = bool(api_key and api_key != "REEMPLAZAR_EN_STREAMLIT")
for key, value in {"idea": "", "result": None, "attempts": 0, "last_attempt": 0.0}.items():
    if key not in st.session_state:
        st.session_state[key] = value

def load_example(name):
    st.session_state.idea = IDEAS[name]
    st.session_state.result = None

with st.sidebar:
    st.title("SpecPilot IA")
    st.caption("De una idea a una especificación")
    st.divider()
    mode = st.radio("Modo de trabajo", ["Generar con IA", "Ver ejemplo sin conexión"])
    level = st.selectbox("Nivel de explicación", ["Principiante", "Intermedio", "Avanzado"])
    focus = st.selectbox("Enfoque", ["MVP esencial", "Validaciones y errores", "Experiencia del usuario"])
    st.divider()
    st.caption("CONEXIÓN CON EL MODELO")
    st.write("Clave configurada" if configured else "Falta configurar la clave")
    st.caption("La conexión se verifica al generar una respuesta.")
    st.caption(f"Modelo: {model} · Prompt v{PROMPT_VERSION}")
    st.caption("Proyecto de Lucca Vilas · Coderhouse")

st.title("Convertí tu idea en requisitos claros")
st.write("Describí qué querés construir. Obtené historias de usuario, criterios de aceptación y casos de prueba para revisar antes de programar.")

if mode == "Ver ejemplo sin conexión":
    st.info("Vista previa fija de una peluquería. No usa IA ni procesa una idea nueva. Para probar el modelo, elegí Generar con IA.")
    result = {"data": validate_spec(DEMO), "origin": "Ejemplo fijo sin IA", "model": "No utilizado", "idea": IDEAS["Turnos de una peluquería"], "created": "Ejemplo incluido", "level": "Principiante", "focus": "MVP esencial"}
else:
    if not configured:
        st.warning("La app todavía no tiene una clave de IA configurada. Podés explorar el ejemplo sin conexión desde el menú lateral.")
    with st.expander("Cargar una idea de ejemplo"):
        sample = st.selectbox("Ejemplos disponibles", list(IDEAS))
        st.button("Usar este ejemplo", on_click=load_example, args=(sample,))
    with st.form("spec_form"):
        idea = st.text_area("¿Qué app querés construir?", key="idea", height=180, max_chars=MAX_INPUT,
            placeholder="Contá quién la usa, qué necesita hacer y qué reglas debe respetar...")
        st.caption("Entre 30 y 6000 caracteres. No incluyas contraseñas, claves ni datos personales reales. Al generar, la descripción se envía a Google Gemini.")
        submitted = st.form_submit_button("Generar especificación", type="primary", disabled=not configured)
    if submitted:
        st.session_state.result = None
        try:
            prompt = build_prompt(idea, level, focus)
            now = time.monotonic()
            if st.session_state.attempts >= 20:
                raise ValueError("Se alcanzó el límite de 20 solicitudes de esta sesión.")
            if now - st.session_state.last_attempt < 10:
                raise ValueError("Esperá 10 segundos entre solicitudes.")
            st.session_state.last_attempt = now
            st.session_state.attempts += 1
            with st.spinner("Preparando historias y casos de prueba..."):
                data = generate_spec(prompt, api_key, model)
            st.session_state.result = {"data": data, "origin": "Generado con Gemini", "model": model,
                "idea": idea, "level": level, "focus": focus, "created": datetime.now(timezone.utc).isoformat()}
        except (ValueError, ModelError) as error:
            st.error(str(error))
    result = st.session_state.result

if result:
    data = result["data"]
    st.divider()
    st.subheader(data["titulo"])
    st.write(data["resumen"])
    st.caption(f"{result['origin']} · {result['created']}")
    if data["estado"] == "requiere_aclaracion":
        st.warning("Hace falta aclarar la idea. Respondé las preguntas e incorporá las respuestas a tu descripción.")
    st.caption("Borrador para revisión humana. Los casos de prueba son propuestas, no pruebas ejecutadas.")
    a, b, c = st.columns(3)
    a.metric("Historias", len(data["historias"]))
    b.metric("Casos de prueba", len(data["pruebas"]))
    c.metric("Preguntas pendientes", len(data["preguntas"]))
    tab1, tab2, tab3, tab4 = st.tabs(["Alcance", "Historias", "Pruebas", "Prompt utilizado"])
    with tab1:
        for key, title in [("alcance", "Incluido en la propuesta"), ("supuestos", "Supuestos por confirmar"), ("preguntas", "Preguntas pendientes"), ("riesgos", "Riesgos a revisar")]:
            st.subheader(title)
            for item in data[key]:
                st.text("• " + item)
            if not data[key]:
                st.caption("Sin elementos informados.")
    with tab2:
        for h in data["historias"]:
            with st.container(border=True):
                st.text(f"{h['id']} · Prioridad {h['prioridad']}")
                st.text(h["historia"])
                for criterion in h["criterios"]:
                    st.text("• " + criterion)
    with tab3:
        for t in data["pruebas"]:
            with st.expander(f"{t['id']} · {t['historia_id']} · {t['tipo']}"):
                for i, step in enumerate(t["pasos"], 1):
                    st.text(f"{i}. {step}")
                st.text("Resultado esperado: " + t["resultado_esperado"])
    with tab4:
        st.caption("El prompt separa instrucciones de sistema y datos del usuario. La clave nunca forma parte de estos textos.")
        st.code(SYSTEM_PROMPT, language="text")
        st.code(build_prompt(result["idea"], result["level"], result["focus"]), language="json")
    md = to_markdown(data, result["origin"], result["model"])
    export = {"origen": result["origin"], "modelo": result["model"], "prompt_version": PROMPT_VERSION,
              "fecha": result["created"], "especificacion": data}
    left, right = st.columns(2)
    left.download_button("Descargar informe Markdown", md, "especificacion.md", "text/markdown")
    right.download_button("Descargar JSON", json.dumps(export, ensure_ascii=False, indent=2), "especificacion.json", "application/json")
else:
    st.info("Tu especificación aparecerá acá después de generar. También podés explorar una vista previa sin conexión.")

with st.expander("Cómo funciona y qué límites tiene"):
    st.write("La app combina tu descripción con instrucciones para un analista funcional. Solicita una respuesta JSON y valida campos, identificadores y cobertura antes de mostrarla. Si faltan datos, el modelo debe explicitar supuestos o pedir aclaraciones.")
    st.write("Los resultados pueden contener errores. No se ejecuta código ni se desarrolla la app descripta. La sesión no se guarda en una base de datos; al cerrarla se puede perder el trabajo. Google procesa los datos conforme a sus condiciones. Los límites por sesión son orientativos y no sustituyen las cuotas del proveedor.")
