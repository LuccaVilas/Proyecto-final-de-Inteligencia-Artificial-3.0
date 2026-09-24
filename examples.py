"""Entradas de prueba ficticias y una vista previa fija, sin simular una llamada al modelo."""
IDEAS = {
    "Turnos de una peluquería": "Quiero una app web para una peluquería. Los clientes eligen un servicio, una fecha y un horario disponible y reservan un turno. La recepcionista administra horarios. No debe permitir dos reservas para el mismo profesional en el mismo horario. El MVP no tendrá pagos online.",
    "Stock de una librería": "Necesito un sistema para una librería pequeña. El encargado registra productos, entradas y ventas. Cada venta descuenta unidades del stock. No se pueden vender más unidades que las disponibles. Debe avisar cuando un producto tenga menos de cinco unidades. No incluye facturación electrónica.",
    "Préstamos de biblioteca": "Una biblioteca necesita registrar préstamos y devoluciones. Cada socio se identifica con un número. Un libro prestado no puede prestarse otra vez hasta ser devuelto. El bibliotecario consulta préstamos activos. No queremos multas automáticas en esta primera versión.",
}
DEMO = {
    "estado": "borrador", "titulo": "Reservas para una peluquería",
    "resumen": "MVP para consultar horarios y reservar un turno evitando superposiciones.",
    "alcance": ["Consulta de disponibilidad por fecha, servicio y profesional.", "Reserva de un horario disponible sin pago online."],
    "supuestos": ["Los horarios son configurados previamente por recepción.", "Cada servicio utiliza un bloque de tiempo de duración fija; debe confirmarse."],
    "preguntas": ["¿Cuánto dura cada servicio?", "¿Se permite cancelar un turno y hasta cuándo?"],
    "historias": [
        {"id": "HU-01", "historia": "Como cliente quiero consultar horarios disponibles para elegir cuándo atenderme.", "prioridad": "Alta", "criterios": ["Al seleccionar fecha y profesional se muestran solo los horarios disponibles.", "Si no hay horarios se informa sin ofrecer una reserva."]},
        {"id": "HU-02", "historia": "Como cliente quiero reservar un horario para asegurar mi atención.", "prioridad": "Alta", "criterios": ["Al confirmar un horario libre se registra una única reserva y se muestra confirmación.", "Si el horario acaba de ocuparse se rechaza la reserva y se pide elegir otro."]},
    ],
    "pruebas": [
        {"id": "CP-01", "historia_id": "HU-01", "tipo": "Positivo", "pasos": ["Preparar un profesional con un horario libre.", "Seleccionar su fecha y nombre."], "resultado_esperado": "Se muestra el horario libre."},
        {"id": "CP-02", "historia_id": "HU-02", "tipo": "Positivo", "pasos": ["Elegir un horario libre.", "Confirmar la reserva."], "resultado_esperado": "Se registra una reserva y se muestra su confirmación."},
        {"id": "CP-03", "historia_id": "HU-02", "tipo": "Negativo", "pasos": ["Abrir el mismo horario libre en dos sesiones.", "Confirmar la primera reserva y después la segunda."], "resultado_esperado": "Solo una reserva se registra; la segunda recibe un aviso de horario ocupado."},
        {"id": "CP-04", "historia_id": "HU-01", "tipo": "Borde", "pasos": ["Preparar una fecha sin disponibilidad.", "Consultar esa fecha."], "resultado_esperado": "Se muestra un aviso de falta de horarios y no se permite reservar."},
    ],
    "riesgos": ["Las reservas simultáneas requieren una validación atómica en la futura base de datos.", "Los datos de contacto de clientes deben tratarse con acceso restringido."],
}
