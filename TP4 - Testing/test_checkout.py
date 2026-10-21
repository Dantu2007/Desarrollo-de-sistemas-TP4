from datetime import date
from decimal import Decimal

import pytest

from checkout import (
    CheckoutError,
    calcular_descuento,
    calcular_envio,
    calcular_subtotal,
    calcular_total,
    validar_item,
)

HOY_VIGENTE = date(2026, 10, 1)


def item(producto="buzo", talle="M", cantidad=1, **extra):
    return {"producto": producto, "talle": talle, "cantidad": cantidad, **extra}


def codigo_de_error(funcion, *args):
    with pytest.raises(CheckoutError) as error:
        funcion(*args)
    return error.value.code


def test_cantidad_cero_es_invalida():
    assert codigo_de_error(validar_item, item(cantidad=0)) == "CANTIDAD_INVALIDA"


def test_cantidad_diez_es_valida():
    validar_item(item(cantidad=10))


def test_cinco_prendas_aplican_descuento():
    descuento = calcular_descuento(
        Decimal("10000.00"),
        5,
    )

    assert descuento == Decimal("1000.00")

def test_talle_con_espacios_es_valido():
    validar_item(item(talle="  M "))


def test_validar_item_no_modifica_el_item():
    datos = item(talle="m")
    original = datos.copy()

    validar_item(datos)

    assert datos == original


def test_producto_inexistente_lanza_error():
    carrito = [item(producto="gorra")]

    assert codigo_de_error(
        calcular_subtotal,
        carrito,
    ) == "PRODUCTO_INEXISTENTE"

def test_carrito_vacio_lanza_error():
    assert codigo_de_error(
        calcular_subtotal,
        [],
    ) == "CARRITO_VACIO"

def test_cupon_egresados_aplica_15_por_ciento():
    descuento = calcular_descuento(
        Decimal("10000.00"),
        1,
        "EGRESADOS2026",
        date(2026, 11, 29),
    )

    assert descuento == Decimal("1500.00")

def test_cupon_egresados_valido_en_fecha_de_vencimiento():
    descuento = calcular_descuento(
        Decimal("10000.00"),
        1,
        "EGRESADOS2026",
        date(2026, 11, 30),
    )

    assert descuento == Decimal("1500.00")

def test_cupon_acepta_minusculas_y_espacios():
    descuento = calcular_descuento(
        Decimal("10000.00"),
        1,
        "  egresados2026  ",
        date(2026, 11, 29),
    )

    assert descuento == Decimal("1500.00")

def test_cupon_vacio_no_genera_error():
    descuento = calcular_descuento(
        Decimal("10000.00"),
        1,
        "   ",
        date(2026, 11, 29),
    )

    assert descuento == Decimal("0.00")

def test_cupon_invalido():
    assert codigo_de_error(
        calcular_descuento,
        Decimal("30000.00"),
        1,
        "NOEXISTE",
        date(2026, 10, 21),
    ) == "CUPON_INVALIDO"


def test_cupon_egresados_vencido():
    assert codigo_de_error(
        calcular_descuento,
        Decimal("30000.00"),
        1,
        "EGRESADOS2026",
        date(2026, 12, 1),
    ) == "CUPON_VENCIDO"


def test_cupon_bienvenida_no_alcanza_minimo():
    assert codigo_de_error(
        calcular_descuento,
        Decimal("19999.99"),
        1,
        "BIENVENIDA",
        date(2026, 10, 21),
    ) == "CUPON_MINIMO_NO_ALCANZADO"


def test_envio_caba():
    envio = calcular_envio(
        Decimal("30000.00"),
        "CABA",
    )

    assert envio == Decimal("2500.00")


def test_envio_gratis_desde_60000():
    envio = calcular_envio(
        Decimal("60000.00"),
        "GBA",
    )

    assert envio == Decimal("0.00")


def test_zona_invalida():
    assert codigo_de_error(
        calcular_envio,
        Decimal("30000.00"),
        "MARTE",
    ) == "ZONA_INVALIDA"

def test_cupon_bienvenida_aplica_descuento_fijo():
    descuento = calcular_descuento(
        Decimal("20000.00"),
        1,
        "BIENVENIDA",
        date(2026, 10, 21),
    )

    assert descuento == Decimal("3000.00")


def test_calcular_total_compra_simple():
    carrito = [
        item(
            producto="buzo",
            talle="M",
            cantidad=1,
        )
    ]

    resultado = calcular_total(
        carrito,
        "CABA",
        None,
        date(2026, 10, 21),
    )

    assert resultado["subtotal"] == Decimal("24999.90")
    assert resultado["descuento"] == Decimal("0.00")
    assert resultado["envio"] == Decimal("2500.00")
    assert resultado["total"] == Decimal("27499.90")