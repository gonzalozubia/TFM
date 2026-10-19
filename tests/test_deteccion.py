import pytest

from avance_obra.deteccion import interpretar_respuesta, preguntar_a_gemini


class RespuestaGeminiFalsa:
    def __init__(self, texto):
        self.text = texto


class ModelosFalsos:
    """Devuelve las respuestas preparadas en orden. Si una es un error, lo lanza."""

    def __init__(self, resultados):
        self.resultados = list(resultados)
        self.llamadas = 0

    def generate_content(self, model, contents, config):
        self.llamadas += 1
        resultado = self.resultados.pop(0)
        if isinstance(resultado, Exception):
            raise resultado
        return RespuestaGeminiFalsa(resultado)


class ClienteFalso:
    """Imita genai.Client: cliente.models.generate_content(...)"""

    def __init__(self, *resultados):
        self.models = ModelosFalsos(resultados)


# --- interpretar_respuesta: control de calidad de Silver ---

def test_respuesta_correcta():
    r = interpretar_respuesta('{"fase": "paneles_instalados", "pct_paneles": 42}')
    assert r == {"fase": "paneles_instalados", "pct_paneles": 42.0}


def test_respuesta_dentro_de_una_lista():
    # El caso que hizo fallar el notebook de detección la primera vez
    r = interpretar_respuesta('[{"fase": "terreno_sin_tocar", "pct_paneles": 0}]')
    assert r["fase"] == "terreno_sin_tocar"


def test_fase_desconocida_se_rechaza():
    with pytest.raises(ValueError):
        interpretar_respuesta('{"fase": "obra_terminada", "pct_paneles": 10}')


def test_porcentaje_fuera_de_rango_se_rechaza():
    with pytest.raises(ValueError):
        interpretar_respuesta('{"fase": "paneles_instalados", "pct_paneles": 130}')


def test_texto_que_no_es_json_se_rechaza():
    with pytest.raises(ValueError):
        interpretar_respuesta("No puedo analizar esta imagen")


# --- preguntar_a_gemini ---

def test_reintenta_si_el_servidor_esta_saturado():
    cliente = ClienteFalso(Exception("503 UNAVAILABLE"),
                           '{"fase": "paneles_instalados", "pct_paneles": 30}')
    r = preguntar_a_gemini(cliente, "modelo", imagen=None, espera_seg=0)
    assert r["pct_paneles"] == 30.0
    assert cliente.models.llamadas == 2


def test_cuota_agotada_no_se_reintenta():
    cliente = ClienteFalso(Exception("429 RESOURCE_EXHAUSTED"))
    with pytest.raises(Exception):
        preguntar_a_gemini(cliente, "modelo", imagen=None, espera_seg=0)
    assert cliente.models.llamadas == 1