import pytest
from avance_obra.teselado import generar_rejilla

# Zona de la planta Núñez de Balboa, la misma que uso en el notebook de ingesta
ZONA = dict(lon_min=-6.252, lon_max=-6.199, lat_min=38.419, lat_max=38.456)


def test_rejilla_nunez_balboa_tiene_14_por_16_teselas():
    teselas = generar_rejilla(**ZONA, lado_m=307, lat_referencia=38.44)
    assert len(teselas) == 14 * 16


def test_la_rejilla_cubre_toda_la_zona():
    teselas = generar_rejilla(**ZONA, lado_m=307, lat_referencia=38.44)
    # La primera tesela empieza justo en la esquina noroeste de la zona
    assert min(t["lon_min"] for t in teselas) == pytest.approx(ZONA["lon_min"])
    assert max(t["lat_max"] for t in teselas) == pytest.approx(ZONA["lat_max"])
    # Las últimas pueden pasarse un poco, pero nunca quedarse cortas
    assert max(t["lon_max"] for t in teselas) >= ZONA["lon_max"]
    assert min(t["lat_min"] for t in teselas) <= ZONA["lat_min"]


def test_teselas_vecinas_no_dejan_huecos():
    teselas = {(t["fila"], t["columna"]): t for t in generar_rejilla(**ZONA, lado_m=307, lat_referencia=38.44)}
    # La tesela de la derecha empieza donde acaba la de la izquierda
    assert teselas[(0, 1)]["lon_min"] == pytest.approx(teselas[(0, 0)]["lon_max"])
    # La tesela de abajo empieza donde acaba la de arriba
    assert teselas[(1, 0)]["lat_max"] == pytest.approx(teselas[(0, 0)]["lat_min"])