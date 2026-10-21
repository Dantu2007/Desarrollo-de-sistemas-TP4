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



## R6 — Cupones

### Particiones válidas
- Sin cupón: `None`, `""` o solo espacios.
- Cupón `EGRESADOS2026` dentro de su vigencia.
- Cupón `BIENVENIDA` cuando el subtotal es de $20.000 o más.
- Cupones escritos con distintas mayúsculas/minúsculas o con espacios alrededor.

### Particiones inválidas
- Código de cupón inexistente.
- `EGRESADOS2026` usado después del 30/11/2026.
- `BIENVENIDA` con subtotal menor a $20.000.

### Valores límite
- `EGRESADOS2026`:
  - 30/11/2026: válido.
  - 01/12/2026: vencido.
- `BIENVENIDA`:
  - Subtotal $20.000: válido.
  - Subtotal menor a $20.000: inválido.
- Si existe descuento por cantidad y por cupón, se aplica únicamente el mayor.

### Casos

- Entrada: cupón `None`.
  - Resultado esperado: no se aplica descuento por cupón y no se produce error.

- Entrada: cupón `" egresados2026 "` con fecha `30/11/2026`.
  - Resultado esperado: se aplica un descuento del 15%.

- Entrada: cupón `EGRESADOS2026` con fecha `01/12/2026`.
  - Resultado esperado: `CheckoutError` con código `CUPON_VENCIDO`.

- Entrada: cupón `BIENVENIDA` con subtotal de $20.000.
  - Resultado esperado: se aplica un descuento fijo de $3.000.

- Entrada: cupón `BIENVENIDA` con subtotal menor a $20.000.
  - Resultado esperado: `CheckoutError` con código `CUPON_MINIMO_NO_ALCANZADO`.

- Entrada: cupón `DESCUENTO50`.
  - Resultado esperado: `CheckoutError` con código `CUPON_INVALIDO`.

- Entrada: compra con descuento por cantidad del 10% y cupón que genera un descuento mayor.
  - Resultado esperado: se aplica solamente el descuento mayor, sin acumular ambos.


## R7 — Dinero y redondeo

### Particiones válidas
- Todos los importes deben manejarse utilizando `Decimal`.
- Los descuentos porcentuales deben redondearse a dos decimales mediante redondeo comercial.

### Particiones inválidas
- Uso de valores `float` para representar importes.
- Resultados monetarios que no estén redondeados correctamente al centavo.

### Valores límite
- Los casos en que el cálculo genera medio centavo deben redondearse hacia arriba.

### Casos

- Entrada: 15% de `Decimal("11999.50")`.
  - Resultado esperado: `Decimal("1799.93")`.

- Entrada: cualquier cálculo de subtotal, descuento, envío o total.
  - Resultado esperado: el resultado debe ser de tipo `Decimal` y no `float`.

- Entrada: cálculo porcentual cuyo tercer decimal sea 5.
  - Resultado esperado: el valor se redondea hacia arriba al centavo.


## R8 — Envío

### Particiones válidas
- Zona `CABA`: costo $2.500.
- Zona `GBA`: costo $4.000.
- Zona `INTERIOR`: costo $6.500.
- Zona `RETIRO`: costo $0.
- Zonas escritas en minúscula o con espacios alrededor.
- Compra cuyo subtotal después del descuento sea de $60.000 o más: envío gratis.

### Particiones inválidas
- Cualquier zona que no pertenezca a las cuatro zonas permitidas.

### Valores límite
- Subtotal con descuento de $59.999,99: corresponde cobrar envío.
- Subtotal con descuento de $60.000: envío gratis.

### Casos

- Entrada: zona `CABA` y subtotal con descuento menor a $60.000.
  - Resultado esperado: envío de $2.500.

- Entrada: zona `" gba "` y subtotal con descuento menor a $60.000.
  - Resultado esperado: envío de $4.000.

- Entrada: zona `INTERIOR` y subtotal con descuento menor a $60.000.
  - Resultado esperado: envío de $6.500.

- Entrada: zona `RETIRO`.
  - Resultado esperado: envío de $0.

- Entrada: zona `CABA` y subtotal con descuento exactamente igual a $60.000.
  - Resultado esperado: envío gratis.

- Entrada: zona `CABA` y subtotal con descuento de $59.999,99.
  - Resultado esperado: envío de $2.500.

- Entrada: zona `ROSARIO`.
  - Resultado esperado: `CheckoutError` con código `ZONA_INVALIDA`.

  ## R9 — Total

### Particiones válidas
- Compra sin descuento y con envío.
- Compra con descuento y con envío.
- Compra con envío gratis.
- Compra con retiro, donde el envío es $0.

### Particiones inválidas
R9 no define entradas inválidas propias, porque usa valores ya validados por las reglas anteriores.

### Valores límite
- Casos donde el subtotal con descuento queda justo por debajo de $60.000.
- Casos donde el subtotal con descuento queda exactamente en $60.000 y el envío pasa a ser gratis.

### Casos

- Entrada:
  - subtotal: $49.999,80
  - descuento: $0
  - envío: $2.500
  - Resultado esperado: total = $52.499,80.

- Entrada:
  - subtotal: $100.000
  - descuento: $10.000
  - envío: $0
  - Resultado esperado: total = $90.000.

- Entrada:
  - subtotal: $50.000
  - descuento: $5.000
  - envío: $4.000
  - Resultado esperado: total = $49.000.


## R10 — Persistencia de pedidos

### Particiones válidas
- Guardar un pedido válido.
- Consultar un pedido existente.
- Consultar un pedido inexistente.
- Buscar pedidos por email.
- Guardar datos que requieren normalización.
- Consultar la base desde otra conexión.

### Particiones inválidas
- Intentar guardar un pedido cuyo checkout produce un `CheckoutError`.
- Datos enviados por el usuario que intenten alterar una consulta mediante el campo email.

### Valores límite
R10 no tiene límites numéricos principales, pero sí casos críticos de persistencia y consistencia entre conexiones.

### Casos

- Entrada: guardar un pedido válido.
  - Resultado esperado: se guarda el pedido junto con todos sus ítems y se devuelve su id.

- Entrada: guardar un pedido inválido que produce un `CheckoutError`.
  - Resultado esperado: el error se propaga y no queda guardado ni el pedido ni ninguno de sus ítems.

- Entrada: guardar un pedido y luego consultarlo desde otra conexión a la misma base.
  - Resultado esperado: el pedido completo debe estar disponible.

- Entrada: consultar un pedido con un id inexistente.
  - Resultado esperado: `None`.

- Entrada: guardar email `"  ANA@MAIL.COM  "`.
  - Resultado esperado: se guarda como `"ana@mail.com"`.

- Entrada: guardar zona `" caba "`, talle `" m "` y cupón `" egresados2026 "`.
  - Resultado esperado: se guardan normalizados como `CABA`, `M` y `EGRESADOS2026`.

- Entrada: guardar un ítem que trae un `precio` propio.
  - Resultado esperado: `precio_unitario` se guarda usando el precio del catálogo y no el enviado por el cliente.

- Entrada: consultar `pedidos_de` con el mismo email usando distintas mayúsculas o espacios.
  - Resultado esperado: devuelve los mismos pedidos.

- Entrada: varios pedidos del mismo email.
  - Resultado esperado: se devuelven del más reciente al más antiguo.

- Entrada: email con contenido que pudiera alterar una consulta SQL.
  - Resultado esperado: se interpreta únicamente como un dato y no modifica la consulta.


## R11 — API HTTP

### Particiones válidas
- Crear un pedido válido mediante `POST /api/v1/pedidos`.
- Consultar un pedido existente mediante `GET /api/v1/pedidos/{id}`.
- Crear un pedido sin cupón ni fecha.
- Crear un pedido con cupón y fecha válidos.

### Particiones inválidas
- Cuerpo que no sea JSON válido.
- Falta de `email`, `zona` o `carrito`.
- Campos obligatorios con tipos incorrectos.
- Fecha con formato inválido.
- Datos que produzcan un `CheckoutError`.
- Consultar un pedido inexistente.
- Acceder a una ruta inexistente.

### Valores límite
- Fecha válida con formato exacto `AAAA-MM-DD`.
- Cupón `EGRESADOS2026` usado el 30/11/2026: válido.
- Cupón `EGRESADOS2026` usado el 01/12/2026: error de negocio.

### Casos

- Entrada: `POST /api/v1/pedidos` con un pedido válido.
  - Resultado esperado: status `201 Created` y respuesta con `id`, `subtotal`, `descuento`, `envio` y `total`.

- Entrada: `GET /api/v1/pedidos/{id}` con un id existente.
  - Resultado esperado: status `200` y el pedido completo.

- Entrada: pedido válido.
  - Resultado esperado: todos los montos de la respuesta JSON viajan como texto y no como números JSON.

- Entrada: cuerpo que no sea JSON válido.
  - Resultado esperado: status `400` y código `JSON_INVALIDO`.

- Entrada: falta `email`, `zona` o `carrito`, o alguno tiene un tipo incorrecto.
  - Resultado esperado: status `400` y código `DATOS_INCOMPLETOS`.

- Entrada: fecha con formato distinto de `AAAA-MM-DD`.
  - Resultado esperado: status `400` y código `FECHA_INVALIDA`.

- Entrada: pedido con talle inválido.
  - Resultado esperado: status `422` y código `TALLE_INVALIDO`.

- Entrada: cualquier otro `CheckoutError`.
  - Resultado esperado: status `422` y se conserva el `code` original del error.

- Entrada: `GET` de un pedido inexistente.
  - Resultado esperado: status `404` y código `PEDIDO_INEXISTENTE`.

- Entrada: acceder a una ruta inexistente.
  - Resultado esperado: status `404` y código `RUTA_INEXISTENTE`.

- Entrada: cualquier error controlado por la especificación.
  - Resultado esperado: nunca debe responder con status `500`.