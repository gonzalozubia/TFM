import numpy as np
import pytest

from avance_obra.metricas import (
    error_medio_absoluto,
    paneles_estimados,
    pct_avance,
    pct_error_menor,
    pct_paneles_mascara,
    sesgo_medio,
)


def test_pct_paneles_mascara():
    # Máscara de 10 x 10 píxeles con las 2 primeras filas marcadas como panel (255)
    mascara = np.zeros((10, 10))
    mascara[:2, :] = 255
    # 20 de 100 píxeles son panel -> 20 %
    assert pct_paneles_mascara(mascara) == 20.0


def test_error_medio_y_sesgo():
    reales = [10, 50, 0]
    estimados = [14, 40, 2]
    # Errores: +4, -10, +2
    # Error medio absoluto = (4 + 10 + 2) / 3 = 5,33
    assert error_medio_absoluto(reales, estimados) == pytest.approx(16 / 3)
    # Sesgo = (4 - 10 + 2) / 3 = -1,33 (de media se queda corto)
    assert sesgo_medio(reales, estimados) == pytest.approx(-4 / 3)


def test_pct_error_menor_que_5_puntos():
    reales = [10, 50, 0, 30]
    estimados = [14, 40, 2, 35]
    # Errores: 4, 10, 2, 5 -> solo 4 y 2 son menores que 5 -> 2 de 4 = 50 %
    assert pct_error_menor(reales, estimados, umbral=5) == 50.0


def test_pct_avance_nunez_balboa_2019():
    # Datos reales de la capa Gold: 88,3 ha de paneles en 2019 y 441,7 ha en 2022
    assert pct_avance(88.3, 441.7) == pytest.approx(20.0, abs=0.1)


def test_paneles_estimados_nunez_balboa_2019():
    # 20 % de avance sobre los 1.430.000 paneles del proyecto
    assert paneles_estimados(20.0, 1_430_000) == 286_000