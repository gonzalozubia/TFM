"""Detección de la fase de obra con Gemini y validación de sus respuestas."""

import json
import time

# Fases de obra que puede devolver el modelo, en el orden en que avanza la obra
FASES = ["terreno_sin_tocar", "movimiento_de_tierras", "estructuras_sin_paneles", "paneles_instalados"]

# Prompt v2: en la v1 el modelo sobrestimaba ~13 puntos porque contaba también
# los pasillos entre filas. Con estas instrucciones el error medio bajó a 6,6 puntos.
PROMPT_V2 = """Esta es una imagen aérea (ortofoto) vista desde arriba, de unos 300 x 300 metros.
1) Clasifica la parcela en una de estas fases de obra:
   terreno_sin_tocar, movimiento_de_tierras, estructuras_sin_paneles, paneles_instalados.
2) Estima qué porcentaje de la imagen ocupa la superficie de los paneles solares.
   Cuenta SOLO la superficie de las placas (los módulos oscuros).
   NO cuentes los pasillos de tierra entre filas, caminos, vallas, edificios
   ni el resto del recinto de la planta.
   Muchas imágenes tienen pocos paneles o ninguno; si no hay, responde 0.
Responde solo con un JSON así: {"fase": "...", "pct_paneles": 0-100}"""


def interpretar_respuesta(texto):
    """Convierte la respuesta de Gemini en {"fase": ..., "pct_paneles": ...}.

    Es el control de calidad de la capa Silver: si la respuesta no es un JSON,
    la fase no es una de las 4 o el % no está entre 0 y 100, lanzo ValueError
    y esa tesela no se guarda (se reintentará en la siguiente ejecución).
    """
    resp = json.loads(texto)  # si no es un JSON válido, json lanza un ValueError

    # A veces Gemini devuelve el JSON dentro de una lista: [{"fase": ..., ...}]
    if isinstance(resp, list):
        resp = resp[0]

    fase = resp["fase"]
    if fase not in FASES:
        raise ValueError(f"Fase desconocida: {fase}")

    pct = float(resp["pct_paneles"])
    if pct < 0 or pct > 100:
        raise ValueError(f"Porcentaje fuera de rango: {pct}")

    return {"fase": fase, "pct_paneles": pct}


def preguntar_a_gemini(cliente, modelo, imagen, reintentos=3, espera_seg=30):
    """Manda una imagen a Gemini y devuelve su respuesta ya validada.

    Si el servidor está saturado (error 503) espero y reintento. Cualquier otro
    error (cuota agotada, respuesta incorrecta...) se lanza para que lo trate el notebook.
    """
    for intento in range(reintentos):
        try:
            r = cliente.models.generate_content(
                model=modelo,
                contents=[imagen, PROMPT_V2],
                config={"response_mime_type": "application/json"},
            )
            return interpretar_respuesta(r.text)
        except Exception as e:
            if "503" in str(e) and intento < reintentos - 1:
                print(f"  Servidor saturado, espero {espera_seg} s...")
                time.sleep(espera_seg)
            else:
                raise