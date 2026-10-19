import pytest

from avance_obra.ingesta_wms import descargar_tesela, parametros_getmap


class RespuestaFalsa:
    """Imita la respuesta de requests: contenido, tipo y código HTTP."""

    def __init__(self, contenido=b"", tipo="image/jpeg", codigo=200):
        self.content = contenido
        self.text = contenido.decode()
        self.headers = {"Content-Type": tipo}
        self.codigo = codigo

    def raise_for_status(self):
        if self.codigo >= 400:
            raise RuntimeError(f"HTTP {self.codigo}")


class SesionFalsa:
    """Imita a requests: devuelve las respuestas preparadas en orden y cuenta las peticiones."""

    def __init__(self, *respuestas):
        self.respuestas = list(respuestas)
        self.peticiones = 0

    def get(self, url, params=None, timeout=None):
        self.peticiones += 1
        return self.respuestas.pop(0)


def test_parametros_getmap():
    p = parametros_getmap(2019, (-6.25, 38.42, -6.24, 38.43), 1024)
    assert p["LAYERS"] == "PNOA2019"
    assert p["BBOX"] == "-6.250000,38.420000,-6.240000,38.430000"
    assert p["WIDTH"] == p["HEIGHT"] == 1024


def test_descarga_correcta_guarda_la_imagen(tmp_path):
    ruta = tmp_path / "tesela.jpg"
    sesion = SesionFalsa(RespuestaFalsa(b"imagen"))
    descargar_tesela({}, ruta, sesion=sesion)
    assert ruta.read_bytes() == b"imagen"
    assert sesion.peticiones == 1


def test_reintenta_si_el_servidor_falla(tmp_path):
    ruta = tmp_path / "tesela.jpg"
    # Primero el IGN da error 504 (como el día que estuvo caído) y luego responde bien
    sesion = SesionFalsa(RespuestaFalsa(codigo=504), RespuestaFalsa(b"imagen"))
    descargar_tesela({}, ruta, espera_seg=0, sesion=sesion)
    assert sesion.peticiones == 2
    assert ruta.read_bytes() == b"imagen"


def test_un_xml_de_error_no_se_guarda_como_imagen(tmp_path):
    ruta = tmp_path / "tesela.jpg"
    xml = RespuestaFalsa(b"<ServiceException/>", tipo="application/vnd.ogc.se_xml")
    sesion = SesionFalsa(xml, xml)
    with pytest.raises(RuntimeError):
        descargar_tesela({}, ruta, reintentos=2, espera_seg=0, sesion=sesion)
    assert not ruta.exists()
    assert sesion.peticiones == 2