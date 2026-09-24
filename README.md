# SpecPilot IA

Proyecto final de **Inteligencia Artificial: Prompt Engineering para programadores 3.0**, Coderhouse.

**Autor:** Lucca Vilas.

**Repositorio público:** https://github.com/LuccaVilas/Proyecto-final-de-Inteligencia-Artificial-3.0

**App desplegada:** pendiente de configurar Streamlit y la API key. Reemplazar esta línea por el enlace real después de publicar y probar la app. El proyecto todavía no está listo para la entrega definitiva.

## Qué resuelve

SpecPilot transforma una idea de software en una especificación inicial: alcance, supuestos, preguntas pendientes, historias de usuario con criterios de aceptación y casos de prueba relacionados. Está pensado para estudiantes y programadores que necesitan ordenar una idea antes de implementarla.

La app está desarrollada en Python y Streamlit y llama a Gemini mediante su API REST. La salida se solicita como JSON y se valida antes de mostrarla. No desarrolla ni ejecuta el software descripto; genera un borrador para revisión humana.

## Uso

1. Seleccionar **Generar con IA**.
2. Escribir una idea de entre 30 y 6000 caracteres o cargar un ejemplo.
3. Elegir nivel de explicación y enfoque.
4. Pulsar **Generar especificación**.
5. Revisar alcance, supuestos, historias y pruebas. Si falta información, responder las preguntas dentro de la descripción y generar nuevamente.
6. Descargar el resultado en Markdown o JSON.

**Ver ejemplo sin conexión** muestra una respuesta fija de una peluquería. No usa IA ni procesa entradas nuevas y no reemplaza la prueba de integración real requerida para la entrega.

## Prompt engineering aplicado

| Práctica | Implementación |
| --- | --- |
| Rol y objetivo explícitos | Analista funcional y QA especializado en requisitos de software. |
| Contexto y restricciones | Descripción, nivel y enfoque separados de las instrucciones del sistema. |
| Ejemplo orientativo | Un ejemplo breve de biblioteca muestra un criterio observable y una prueba negativa. |
| Formato estructurado | JSON Schema con campos obligatorios y límites de tamaño. |
| Gestión de incertidumbre | Supuestos explícitos y preguntas; estado de aclaración para entradas fuera de alcance. |
| Verificación | Validación de esquema, IDs únicos, referencias válidas y cobertura de historias. |
| Resistencia a instrucciones maliciosas | El prompt trata la entrada como datos; no hay ejecución de código ni herramientas del modelo. No garantiza inmunidad a prompt injection. |
| Iteración | El usuario puede incorporar aclaraciones y volver a generar. No existe memoria de conversación entre solicitudes. |

El prompt completo está en `core.py` y puede verse en la pestaña **Prompt utilizado**. La aplicación no solicita ni muestra razonamiento interno.

## Instalación local

Recomendado: Python **3.12**.

```bash
python -m venv .venv
# Windows PowerShell
.venv\Scripts\Activate.ps1
# macOS o Linux: source .venv/bin/activate
python -m pip install -r requirements.txt
```

Copiar `.streamlit/secrets.toml.example` a `.streamlit/secrets.toml` y colocar la clave únicamente en ese archivo local ignorado por Git:

```toml
GEMINI_API_KEY = "TU_CLAVE_SOLO_EN_SECRETOS"
GEMINI_MODEL = "gemini-3.5-flash-lite"
```

También se aceptan variables de entorno con esos nombres. Las variables de entorno tienen prioridad. No se carga `.env` automáticamente.

```bash
python -m streamlit run app.py
```

## Publicación en Streamlit

1. Crear una cuenta o iniciar sesión en [Streamlit Community Cloud](https://share.streamlit.io/).
2. Vincular GitHub y seleccionar este repositorio público, rama `main`, archivo `app.py`.
3. Elegir Python 3.12 en las opciones avanzadas.
4. En **Secrets**, colocar `GEMINI_API_KEY` y `GEMINI_MODEL` como en el ejemplo anterior. La clave se obtiene en [Google AI Studio](https://aistudio.google.com/apikey). No colocar la clave en GitHub.
5. Publicar y ejecutar los casos de aceptación de `docs/PRUEBAS.md` con el modelo real.
6. Pegar la URL definitiva de la app al principio de este README y en el documento de entrega.
7. Comprobar el acceso público desde una ventana privada. La persona que evalúa debe poder generar sin aportar una clave propia.

El acceso a modelos, las cuotas y cualquier costo dependen de la cuenta del proveedor. Confirmar disponibilidad antes de elegir un plan. Si el identificador del modelo deja de estar disponible, actualizar `GEMINI_MODEL` con uno compatible con Interactions y salida estructurada y repetir las pruebas.

## Seguridad y límites

- Clave en el servidor, enviada al proveedor mediante encabezado HTTPS; no forma parte del prompt, descargas ni repositorio.
- `.gitignore` excluye archivos de secretos y entornos locales.
- No se imprimen respuestas crudas de error, credenciales ni prompts en logs propios.
- La descripción se envía a Google. No usar datos sensibles reales.
- Se solicita `store=false`; esto no sustituye las condiciones de tratamiento de datos de Google.
- Máximo 6000 caracteres de entrada, 6000 tokens de salida y timeout de conexión/lectura de 10/60 segundos.
- Límite de 20 intentos por sesión y 10 segundos entre intentos. Es una ayuda de uso, no una defensa global: nuevas sesiones pueden eludirlo. Configurar cuotas y monitorear uso en el proveedor.
- El resultado se mantiene en la sesión y no se guarda en una base de datos. No hay historial persistente.
- La IA puede inventar requisitos o interpretar mal una idea. El esquema valida estructura y relaciones, no la verdad ni la calidad de cada requisito.

## Pruebas

```bash
python -m pip install -r requirements-dev.txt
python -m pytest -q
```

**Resultado local registrado:** 36 pruebas aprobadas en Python 3.12 sobre validaciones, cliente HTTP simulado y flujo de Streamlit. La integración con Gemini real y la app pública permanecen pendientes. No confundir pruebas simuladas con una verificación del proveedor.

El workflow de GitHub Actions ejecuta la suite sin secretos. Casos manuales, criterios de evaluación y resultados pendientes: [docs/PRUEBAS.md](docs/PRUEBAS.md).

## Ejemplos para evaluar

**Peluquería:** “Quiero una app para reservar turnos de peluquería. El cliente elige profesional y horario. No se pueden superponer reservas y el MVP no incluye pagos online.” Esperado: historias de consulta/reserva, prevención de duplicados y casos negativos; sin pagos dentro del alcance confirmado.

**Librería:** “Necesito registrar entradas y ventas de productos. Cada venta descuenta stock. No se permite vender más unidades que las disponibles y debe avisar cuando queden menos de cinco.” Esperado: validación de stock insuficiente y casos de borde alrededor del umbral.

**Ambigüedad:** “Quiero una aplicación para organizar mi negocio y trabajar mejor con mi equipo.” Esperado: supuestos y preguntas concretas, sin inventar integraciones como decisiones confirmadas.

## Estructura

```text
app.py                       Interfaz y estado de sesión
core.py                      Prompt, esquema, validaciones y exportación
llm.py                       Cliente REST de Gemini y errores seguros
examples.py                  Ideas ficticias y vista previa fija
tests/                       Pruebas automatizadas sin consumo de API
docs/PRUEBAS.md               Plan de aceptación y evaluación del modelo
.streamlit/config.toml       Tema y configuración pública
.streamlit/secrets.toml.example  Plantilla sin credenciales
```

## Referencias oficiales

- [Streamlit: desplegar una app](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/deploy)
- [Streamlit: secretos](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/secrets-management)
- [Gemini: API Interactions](https://ai.google.dev/api/interactions-api)
- [Gemini: salida estructurada](https://ai.google.dev/gemini-api/docs/structured-output)
- [Gemini: modelos disponibles](https://ai.google.dev/gemini-api/docs/models)

## Datos para la entrega

Nombre y apellido: **Lucca Vilas**. El correo registrado en Coderhouse se incluye en el documento de entrega, no es necesario publicarlo en este repositorio. Antes de enviar, completar la URL de la app y verificar los casos reales pendientes.