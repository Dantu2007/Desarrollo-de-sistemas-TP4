import json
import threading
import urllib.error
import urllib.request

import pytest

import api

RUTA = "/api/v1/pedidos"


@pytest.fixture
def url(tmp_path):
    servidor = api.crear_servidor(str(tmp_path / "tienda.db"), 0)
    threading.Thread(target=servidor.serve_forever, kwargs={"poll_interval": 0.05}, daemon=True).start()
    yield f"http://127.0.0.1:{servidor.server_address[1]}"
    servidor.shutdown()
    servidor.server_close()


def pedir(url, metodo, ruta, cuerpo=None, crudo=None):
    datos = crudo if crudo is not None else (json.dumps(cuerpo).encode() if cuerpo is not None else None)
    req = urllib.request.Request(url + ruta, data=datos, method=metodo,
                                 headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=5) as r:
            return r.status, json.loads(r.read() or b"null")
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read() or b"null")


def compra(**cambios):
    cuerpo = {"email": "ana@mail.com", "zona": "CABA",
              "carrito": [{"producto": "buzo", "talle": "M", "cantidad": 1}]}
    cuerpo.update(cambios)
    return cuerpo


def test_una_ruta_inexistente_devuelve_404(url):
    status, cuerpo = pedir(url, "GET", "/api/v1/otra")
    assert status == 404
    assert cuerpo["error"]["code"] == "RUTA_INEXISTENTE"

def test_json_invalido_devuelve_400(url):
    status, cuerpo = pedir(
        url,
        "POST",
        RUTA,
        crudo=b"{json roto",
    )

    assert status == 400
    assert cuerpo["error"]["code"] == "JSON_INVALIDO"


def test_datos_incompletos_devuelve_400(url):
    cuerpo_incompleto = {
        "email": "ana@mail.com",
        "carrito": [
            {
                "producto": "buzo",
                "talle": "M",
                "cantidad": 1,
            }
        ],
    }

    status, cuerpo = pedir(
        url,
        "POST",
        RUTA,
        cuerpo=cuerpo_incompleto,
    )

    assert status == 400
    assert cuerpo["error"]["code"] == "DATOS_INCOMPLETOS"


def test_error_de_checkout_devuelve_422(url):
    cuerpo_invalido = compra(
        carrito=[
            {
                "producto": "buzo",
                "talle": "XXXL",
                "cantidad": 1,
            }
        ]
    )

    status, cuerpo = pedir(
        url,
        "POST",
        RUTA,
        cuerpo=cuerpo_invalido,
    )

    assert status == 422
    assert cuerpo["error"]["code"] == "TALLE_INVALIDO"