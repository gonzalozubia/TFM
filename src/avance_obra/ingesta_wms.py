"""Descarga de teselas desde un servicio WMS (en el TFM, el PNOA histórico del IGN)."""

import time

import requests

WMS_PNOA_HISTORICO = "https://www.ign.es/wms/pnoa-historico"


def parametros_getmap(anio, bbox, tam_px):
    """Parámetros de la petición GetMap para la ortofoto PNOA de un año.

    bbox = (lon_min, lat_min, lon_max, lat_max), que es el orden que pide WMS 1.1.1.
    """
    return {
        "SERVICE": "WMS", "VERSION": "1.1.1", "REQUEST": "GetMap",
        "LAYERS": f"PNOA{anio}", "STYLES": "", "SRS": "EPSG:4326",
        "BBOX": ",".join(f"{v:.6f}" for v in bbox),
        "WIDTH": tam_px, "HEIGHT": tam_px, "FORMAT": "image/jpeg",
    }


def descargar_tesela(params, ruta, reintentos=3, espera_seg=30, sesion=requests):
    """Pide una tesela al WMS y la guarda en `ruta`. Si falla, espera y reintenta.

    `sesion` es quien hace la petición HTTP. Por defecto es `requests`; en los
    tests le paso una sesión falsa para no depender de internet.
    """
    for intento in range(reintentos):
        try:
            r = sesion.get(WMS_PNOA_HISTORICO, params=params, timeout=120)
            r.raise_for_status()
            # Si el WMS da un error, devuelve un XML en vez de una imagen
            if not r.headers.get("Content-Type", "").startswith("image"):
                raise ValueError(r.text[:200])
            with open(ruta, "wb") as f:
                f.write(r.content)
            return
        except Exception as e:
            print(f"  Fallo ({e.__class__.__name__}), intento {intento + 1} de {reintentos}")
            if intento < reintentos - 1:
                time.sleep(espera_seg)
    raise RuntimeError(f"No se pudo descargar {ruta}")