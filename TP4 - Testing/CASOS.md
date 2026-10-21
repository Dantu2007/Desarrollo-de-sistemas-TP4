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
- Talle `S`.
- Talle `M`.
- Talle `L`.
- Talle `XL`.

### Particiones inválidas
- Cualquier talle que no pertenezca al conjunto permitido.
- Valores en minúscula si la especificación exige coincidencia exacta.
- Valores vacíos o nulos.

### Valores límite
R2 no posee límites numéricos, ya que trabaja con un conjunto cerrado de valores válidos.

### Casos

- Entrada: `{"producto": "buzo", "talle": "S", "cantidad": 1}`
  - Resultado esperado: el ítem es válido respecto del talle.

- Entrada: `{"producto": "buzo", "talle": "XL", "cantidad": 1}`
  - Resultado esperado: el ítem es válido respecto del talle.

- Entrada: `{"producto": "buzo", "talle": "XXL", "cantidad": 1}`
  - Resultado esperado: `CheckoutError` con código `TALLE_INVALIDO`.

- Entrada: `{"producto": "buzo", "talle": "", "cantidad": 1}`
  - Resultado esperado: `CheckoutError` con código `TALLE_INVALIDO`.