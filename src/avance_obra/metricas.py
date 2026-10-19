"""Métricas de validación del modelo y cálculos del avance de obra."""

import numpy as np


def pct_paneles_mascara(mascara):
    """% de píxeles de la máscara marcados como panel (cualquier valor > 0 es panel)."""
    mascara = np.array(mascara)
    return float((mascara > 0).mean() * 100)


def error_medio_absoluto(reales, estimados):
    """Media de |estimado - real|, en puntos porcentuales."""
    errores = [abs(e - r) for r, e in zip(reales, estimados)]
    return sum(errores) / len(errores)


def sesgo_medio(reales, estimados):
    """Media de (estimado - real): positivo si el modelo sobrestima, negativo si se queda corto."""
    diferencias = [e - r for r, e in zip(reales, estimados)]
    return sum(diferencias) / len(diferencias)


def pct_error_menor(reales, estimados, umbral=5):
    """% de imágenes en las que el error es menor que `umbral` puntos."""
    aciertos = [abs(e - r) < umbral for r, e in zip(reales, estimados)]
    return sum(aciertos) / len(aciertos) * 100


def pct_avance(superficie_actual, superficie_final):
    """% de avance respecto a la superficie de paneles de la planta terminada."""
    return superficie_actual / superficie_final * 100


def paneles_estimados(pct_avance_obra, paneles_totales):
    """Paneles instalados estimados = % de avance x paneles del proyecto.

    Descarté contar paneles directamente con Gemini: con la planta terminada
    se quedó un 74 % por debajo del total real.
    """
    return round(pct_avance_obra / 100 * paneles_totales)