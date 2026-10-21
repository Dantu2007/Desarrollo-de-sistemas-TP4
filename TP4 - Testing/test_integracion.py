from decimal import Decimal

import pytest

from checkout import CheckoutError
from pedidos import conectar, crear_esquema, guardar_pedido, obtener_pedido


def carrito_valido():
    return [
        {
            "producto": "buzo",
            "talle": "M",
            "cantidad": 1,
        }
    ]


def preparar_db(tmp_path):
    db = tmp_path / "pedidos.db"
    con = conectar(str(db))
    crear_esquema(con)
    return db, con


def test_si_checkout_falla_no_queda_pedido_guardado(tmp_path):
    db, con = preparar_db(tmp_path)

    carrito = [
        {
            "producto": "buzo",
            "talle": "M",
            "cantidad": 0,
        }
    ]

    with pytest.raises(CheckoutError):
        guardar_pedido(
            con,
            "ana@mail.com",
            carrito,
            "CABA",
        )

    cantidad = con.execute(
        "SELECT COUNT(*) FROM pedidos"
    ).fetchone()[0]

    assert cantidad == 0


def test_otra_conexion_ve_el_pedido_completo(tmp_path):
    db, con1 = preparar_db(tmp_path)

    pedido_id = guardar_pedido(
        con1,
        "ana@mail.com",
        carrito_valido(),
        "CABA",
    )

    con2 = conectar(str(db))

    pedido = obtener_pedido(
        con2,
        pedido_id,
    )

    assert pedido is not None
    assert len(pedido["items"]) == 1


def test_montos_recuperados_son_decimal(tmp_path):
    db, con = preparar_db(tmp_path)

    pedido_id = guardar_pedido(
        con,
        "ana@mail.com",
        carrito_valido(),
        "CABA",
    )

    pedido = obtener_pedido(
        con,
        pedido_id,
    )

    assert isinstance(pedido["subtotal"], Decimal)
    assert isinstance(pedido["descuento"], Decimal)
    assert isinstance(pedido["envio"], Decimal)
    assert isinstance(pedido["total"], Decimal)


def test_precio_enviado_por_cliente_se_ignora(tmp_path):
    db, con = preparar_db(tmp_path)

    carrito = [
        {
            "producto": "buzo",
            "talle": "M",
            "cantidad": 1,
            "precio": Decimal("1.00"),
        }
    ]

    pedido_id = guardar_pedido(
        con,
        "ana@mail.com",
        carrito,
        "CABA",
    )

    pedido = obtener_pedido(
        con,
        pedido_id,
    )

    assert pedido["items"][0]["precio_unitario"] == Decimal("24999.90")