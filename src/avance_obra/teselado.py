"""Cálculo de la rejilla de teselas que cubre la zona de una planta."""

import math

# Metros que mide un grado. Para la longitud depende de la latitud (ver abajo)
METROS_POR_GRADO_LAT = 111_000
METROS_POR_GRADO_LON_ECUADOR = 111_320


def grados_por_tesela(lado_m, lat_referencia):
    """Devuelve (d_lat, d_lon): lo que mide en grados una tesela de `lado_m` metros.

    Un grado de longitud mide menos cuanto más lejos del ecuador,
    por eso d_lon depende de la latitud de la zona.
    """
    d_lat = lado_m / METROS_POR_GRADO_LAT
    d_lon = lado_m / (METROS_POR_GRADO_LON_ECUADOR * math.cos(math.radians(lat_referencia)))
    return d_lat, d_lon


def generar_rejilla(lon_min, lon_max, lat_min, lat_max, lado_m, lat_referencia):
    """Divide la zona en teselas de `lado_m` metros de lado.

    Empiezo por la esquina noroeste (fila 0 arriba, columna 0 a la izquierda),
    que es como se ve la ortofoto. Devuelve una lista de diccionarios con la
    fila, la columna, el nombre de archivo y el bbox de cada tesela.
    """
    d_lat, d_lon = grados_por_tesela(lado_m, lat_referencia)
    n_filas = math.ceil((lat_max - lat_min) / d_lat)
    n_columnas = math.ceil((lon_max - lon_min) / d_lon)

    teselas = []
    for fila in range(n_filas):
        for columna in range(n_columnas):
            t_lat_max = lat_max - fila * d_lat
            t_lon_min = lon_min + columna * d_lon
            teselas.append({
                "fila": fila,
                "columna": columna,
                "tesela": f"tesela_f{fila:02d}_c{columna:02d}.jpg",
                "lat_min": t_lat_max - d_lat,
                "lat_max": t_lat_max,
                "lon_min": t_lon_min,
                "lon_max": t_lon_min + d_lon,
            })
    return teselas