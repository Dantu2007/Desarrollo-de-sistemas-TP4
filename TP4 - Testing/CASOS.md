# Casos de caja negra

## R1 — Catálogo y precios

### Particiones válidas
- Producto `buzo`.
- Producto `remera`.
- Producto `campera`.
- Ítem con una clave `precio` propia: debe ignorarse y usarse el precio del catálogo.

### Particiones inválidas
- Producto que no existe en el catálogo.
- Producto escrito con mayúsculas o con un nombre diferente al definido.

### Valores límite
R1 no posee límites numéricos, ya que trabaja con un conjunto cerrado de productos válidos.

### Casos

- Entrada: `{"producto": "buzo", "talle": "M", "cantidad": 1}`
  - Resultado esperado: se utiliza el precio del catálogo `$24999.90`.

- Entrada: `{"producto": "remera", "talle": "M", "cantidad": 1, "precio": 1}`
  - Resultado esperado: se ignora el precio `1` y se utiliza `$11999.50`.

- Entrada: `{"producto": "gorra", "talle": "M", "cantidad": 1}`
  - Resultado esperado: `CheckoutError` con código `PRODUCTO_INEXISTENTE`.

- Entrada: `{"producto": "Buzo", "talle": "M", "cantidad": 1}`
  - Resultado esperado: `CheckoutError` con código `PRODUCTO_INEXISTENTE`.


## R2 — Talles válidos

### Particiones válidas
- Talle `XS`.
- Talle `S`.
- Talle `M`.
- Talle `L`.
- Talle `XL`.
- Talle `XXL`.
- Talles escritos en minúscula, por ejemplo `m`.
- Talles con espacios al principio o al final, por ejemplo `"  M "`.

### Particiones inválidas
- Cualquier talle que no pertenezca al conjunto permitido luego de normalizarlo.
- Valores vacíos.
- Valores nulos.

### Valores límite
R2 no posee límites numéricos, ya que trabaja con un conjunto cerrado de talles válidos.

### Casos

- Entrada: `{"producto": "buzo", "talle": "XS", "cantidad": 1}`
  - Resultado esperado: el ítem es válido respecto del talle.

- Entrada: `{"producto": "buzo", "talle": "XXL", "cantidad": 1}`
  - Resultado esperado: el ítem es válido respecto del talle.

- Entrada: `{"producto": "buzo", "talle": "m", "cantidad": 1}`
  - Resultado esperado: el talle se acepta como `M`.

- Entrada: `{"producto": "buzo", "talle": "  M ", "cantidad": 1}`
  - Resultado esperado: el talle se acepta como `M`.

- Entrada: `{"producto": "buzo", "talle": "XXXL", "cantidad": 1}`
  - Resultado esperado: `CheckoutError` con código `TALLE_INVALIDO`.

- Entrada: `{"producto": "buzo", "talle": "", "cantidad": 1}`
  - Resultado esperado: `CheckoutError` con código `TALLE_INVALIDO`.


## R3 — Cantidad

### Particiones válidas
- Números enteros entre 1 y 10 inclusive.

### Particiones inválidas
- 0.
- Números negativos.
- Números mayores a 10.
- Números decimales.
- Texto u otros valores que no sean enteros.

### Valores límite
- Límite inferior válido: 1.
- Límite superior válido: 10.
- Valores inmediatamente fuera de los límites: 0 y 11.

### Casos

- Entrada: `{"producto": "buzo", "talle": "M", "cantidad": 1}`
  - Resultado esperado: el ítem es válido respecto de la cantidad.

- Entrada: `{"producto": "buzo", "talle": "M", "cantidad": 10}`
  - Resultado esperado: el ítem es válido respecto de la cantidad.

- Entrada: `{"producto": "buzo", "talle": "M", "cantidad": 0}`
  - Resultado esperado: `CheckoutError` con código `CANTIDAD_INVALIDA`.

- Entrada: `{"producto": "buzo", "talle": "M", "cantidad": 11}`
  - Resultado esperado: `CheckoutError` con código `CANTIDAD_INVALIDA`.

- Entrada: `{"producto": "buzo", "talle": "M", "cantidad": 2.5}`
  - Resultado esperado: `CheckoutError` con código `CANTIDAD_INVALIDA`.

## R4 — Carrito

### Particiones válidas
- Carrito con un solo ítem válido.
- Carrito con varios ítems válidos.
- El carrito debe conservar exactamente sus datos originales luego de llamar a las funciones.

### Particiones inválidas
- Lista vacía.
- Cualquier situación en la que una función modifique el carrito recibido.

### Valores límite
- Cantidad mínima válida de ítems: 1.
- Valor inmediatamente inferior al mínimo: 0 ítems.

### Casos

- Entrada: carrito con un único ítem válido.
  - Resultado esperado: el carrito es aceptado.

- Entrada: carrito con varios ítems válidos.
  - Resultado esperado: el carrito es aceptado.

- Entrada: `[]`
  - Resultado esperado: `CheckoutError` con código `CARRITO_VACIO`.

- Entrada: un carrito válido que se guarda antes de llamar a una función de checkout.
  - Resultado esperado: luego de ejecutar la función, el carrito debe ser exactamente igual al original, sin claves modificadas, agregadas ni eliminadas.


## R5 — Descuento por cantidad

### Particiones válidas
- Carrito cuya cantidad total de prendas sea menor a 5: no se aplica descuento por cantidad.
- Carrito cuya cantidad total de prendas sea 5 o más: se aplica un 10% de descuento sobre el subtotal.

### Particiones inválidas
R5 no define entradas inválidas propias, ya que depende de cantidades previamente validadas por R3.

### Valores límite
- 4 prendas: no corresponde descuento.
- 5 prendas: comienza a aplicarse el 10% de descuento.

### Casos

- Entrada: carrito con una cantidad total de 4 prendas.
  - Resultado esperado: descuento por cantidad de `$0`.

- Entrada: carrito con una cantidad total de 5 prendas.
  - Resultado esperado: descuento del `10%` sobre el subtotal.

- Entrada: carrito con una cantidad total de 6 prendas.
  - Resultado esperado: descuento del `10%` sobre el subtotal.

- Entrada: dos ítems con cantidades `2` y `3`.
  - Resultado esperado: se suman las cantidades, dando un total de 5 prendas, por lo que corresponde un descuento del `10%`.