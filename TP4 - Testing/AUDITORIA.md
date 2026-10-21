## Auditoría de los tests provistos por la IA

## Sección 1 — Tests de la IA

Se ejecutó mutation testing sobre `test_checkout_ia.py` mediante el comando:

`python mutar.py --tests test_checkout_ia.py`

El resultado obtenido fue:

- Mutantes generados: 29
- Mutantes muertos: 17
- Mutantes sobrevivientes: 12
- Puntaje de mutación: 58,6%

El puntaje obtenido indica que la suite de tests provista por la IA presenta una cobertura lógica insuficiente. Doce modificaciones introducidas intencionalmente en `checkout.py` no fueron detectadas por ningún test.

Entre los casos no detectados aparecen cambios relevantes en:

- los límites de cantidad de prendas;
- la aplicación del descuento por cantidad;
- la vigencia de cupones;
- el mínimo requerido para cupones;
- el cálculo de descuentos;
- el límite para envío gratuito;
- la suma de cantidades;
- el cálculo final del total.

Esto demuestra que los tests existentes verifican algunos comportamientos generales, pero no cubren correctamente varios valores límite ni operaciones críticas del negocio.


## Evaluación de los tests de la IA

### 1. `test_subtotal`
**Clasificación:** útil.  
Comprueba correctamente que el subtotal de dos buzos se calcula multiplicando el precio del catálogo por la cantidad.

### 2. `test_total_funciona`
**Clasificación:** débil.  
Solo verifica que el resultado no sea `None`, pero no comprueba que subtotal, descuento, envío o total tengan los valores correctos.

### 3. `test_total_positivo`
**Clasificación:** débil.  
Únicamente comprueba que el total sea mayor que cero, por lo que muchos cálculos incorrectos podrían pasar igualmente el test.

### 4. `test_cupon_egresados`
**Clasificación:** útil.  
Comprueba un caso válido del cupón `EGRESADOS2026` y verifica que aplique un descuento del 15%, aunque no prueba sus fechas límite ni casos inválidos.

### 5. `test_cupon_bienvenida`
**Clasificación:** útil.  
Comprueba que el cupón `BIENVENIDA` aplique correctamente el descuento fijo cuando se alcanza el subtotal mínimo requerido.

### 6. `test_envio_caba`
**Clasificación:** débil.  
Verifica un caso simple de envío a CABA, pero no prueba el límite de envío gratis ni otras zonas.

### 7. `test_carrito_vacio`
**Clasificación:** útil.  
Comprueba que un carrito vacío produzca el error esperado y valida una regla de negocio concreta.

### 8. `test_producto_inexistente`
**Clasificación:** útil.  
Comprueba que un producto fuera del catálogo produzca el error correspondiente, aunque no evalúa otros casos relacionados con catálogo y precios.

## Sección 2 — Hallazgos

## Auditoría estática con Ruff

Se ejecutó el comando:

`python -m ruff check checkout.py pedidos.py api.py`

Ruff detectó 5 problemas en `checkout.py`:

- Importación de `json` no utilizada.
- Uso de un `except` genérico sin especificar la excepción.
- Uso de `date.today()` como valor por defecto en un parámetro de función.
- Comparación con `None` utilizando `!=` en lugar de `is not None`.
- Segundo uso de `date.today()` como valor por defecto en otra función.

Estos hallazgos corresponden principalmente a problemas de calidad, estilo y mantenibilidad del código. No reemplazan la revisión funcional, ya que existen errores de lógica que Ruff no puede detectar.

## Auditoría funcional de `checkout.py`

Se comparó la implementación de `checkout.py` con las reglas R1 a R9 de la especificación.

Se detectaron los siguientes problemas:

1. **R1 — Precios**
   Los precios del catálogo están definidos como `float` y no como `Decimal`. Además, si el cliente envía una clave `precio`, el sistema utiliza ese valor en lugar de ignorarlo.

2. **R1 — Producto inexistente**
   No se valida correctamente que el producto exista. En `calcular_subtotal`, un producto inexistente puede ser ignorado mediante un `except` en lugar de generar `PRODUCTO_INEXISTENTE`.

3. **R2 — Talles**
   El talle se convierte a mayúsculas, pero no se eliminan los espacios de los extremos. Por ejemplo, `"  M "` debería ser válido.

4. **R4 — Modificación del carrito**
   `validar_item` modifica directamente `item["talle"]`, por lo que altera el carrito original recibido, incumpliendo la regla que exige no modificarlo.

5. **R3 — Cantidad**
   La condición utiliza `< 10`, por lo que la cantidad `10` es rechazada aunque la especificación establece un rango inclusivo entre 1 y 10.

6. **R4 — Carrito vacío**
   No existe una validación explícita que genere `CARRITO_VACIO` cuando el carrito no contiene ítems.

7. **R5 — Descuento por cantidad**
   El descuento del 10% se aplica únicamente con más de 5 prendas (`> 5`), cuando debería aplicarse desde 5 prendas inclusive (`>= 5`).

8. **R6 — Cupones existentes**
   Existe un cupón adicional llamado `DEBUG100`, aunque la especificación indica que solamente existen `EGRESADOS2026` y `BIENVENIDA`.

9. **R6 — Normalización del cupón**
   El cupón elimina espacios, pero no normaliza mayúsculas y minúsculas. Además, un cupón vacío o compuesto solamente por espacios debería equivaler a no usar cupón, pero actualmente produce `CUPON_INVALIDO`.

10. **R6 — Fecha de vencimiento**
    `EGRESADOS2026` debería ser válido hasta el 30/11/2026 inclusive, pero la implementación considera vencido el cupón ese mismo día.

11. **R6 — Acumulación de descuentos**
    El descuento por cantidad y el descuento por cupón se suman. La especificación indica que deben calcularse ambos y aplicarse únicamente el mayor.

12. **R6 — Límite del descuento**
    No se garantiza que el descuento final nunca supere el subtotal.

13. **R6 — Fecha por defecto**
    Se utiliza `date.today()` como valor por defecto al definir la función. Esto fija la fecha cuando se carga el módulo en lugar de obtener la fecha del día de cada llamada.

14. **R7 — Manejo de dinero**
    Los cálculos utilizan `float`, enteros y `round`, incumpliendo el requisito de utilizar `Decimal` y redondeo comercial.

15. **R8 — Error de zona**
    Al construir el mensaje de `ZONA_INVALIDA` se utiliza incorrectamente `ENVIOS.keys().join(...)`, lo que puede producir otra excepción en lugar de un `CheckoutError`.

16. **R8 — Envío gratis**
    En `calcular_total`, el costo de envío se calcula utilizando el subtotal original. La regla establece que el límite de $60.000 debe evaluarse después de aplicar el descuento.

17. **R7/R8/R9 — Tipos de retorno**
    Subtotal, descuento, envío y total no se devuelven necesariamente como `Decimal`, aunque el contrato exige que todos los importes utilicen ese tipo.

18. **Orden de validación**
    La especificación exige validar primero carrito vacío y luego, para cada ítem, producto, talle y cantidad. La implementación comienza validando el talle y no valida explícitamente el producto en ese orden.



## Auditoría funcional de `pedidos.py`

Se comparó `pedidos.py` con las reglas de persistencia R10.

Se detectaron los siguientes problemas:

1. **Persistencia parcial ante errores**
   El pedido se inserta y se hace `commit()` antes de llamar a `calcular_total`. Si el checkout produce un `CheckoutError`, puede quedar un pedido guardado parcialmente, incumpliendo la regla de atomicidad.

2. **Falta de commit final**
   Después de actualizar los importes e insertar los ítems no se realiza un `commit()`. Por lo tanto, otra conexión puede no ver inmediatamente el pedido completo.

3. **Pérdida de precisión monetaria**
   Los valores `Decimal` calculados por checkout se convierten a `float` antes de almacenarse en SQLite. Esto puede producir pérdida de precisión.

4. **Recuperación incorrecta de montos**
   `obtener_pedido` construye `Decimal` directamente desde valores `float`, lo que puede generar valores distintos a los calculados originalmente por checkout.

5. **Precio unitario manipulable**
   Al guardar los ítems se utiliza `item.get("precio", CATALOGO[...])`. Si el cliente envía un precio propio, ese valor puede terminar almacenado en lugar del precio oficial del catálogo.

6. **Consulta vulnerable en `pedidos_de`**
   El email se inserta directamente dentro de la consulta SQL mediante un f-string. Esto incumple la regla que indica que el email debe tratarse únicamente como dato y abre la posibilidad de modificar la consulta mediante SQL injection.

7. **Falta de transacción única**
   La operación completa de guardar pedido, importes e ítems no está contenida en una única transacción atómica, por lo que pueden quedar datos inconsistentes ante una falla intermedia.


## Auditoría funcional de `api.py`

Se comparó `api.py` con las reglas HTTP definidas en R11.

Se detectaron los siguientes problemas:

1. **Manejo de JSON inválido**
   El servidor no diferencia correctamente un cuerpo que no contiene JSON válido del resto de los errores de entrada, por lo que puede responder con un código o mensaje distinto al requerido por `JSON_INVALIDO`.

2. **Validación incompleta de campos obligatorios**
   No se valida de forma estricta la presencia y el tipo de `email`, `zona` y `carrito` antes de continuar con el procesamiento.

3. **Validación de fecha**
   Una fecha con formato incorrecto puede no transformarse en el error controlado `FECHA_INVALIDA` con status 400 como exige la especificación.

4. **Mapeo de errores de checkout**
   Los `CheckoutError` deben responder con status 422 preservando su código original. La implementación no garantiza correctamente este comportamiento para todos los casos.

5. **Pedido inexistente**
   La consulta de un id inexistente debe devolver status 404 con código `PEDIDO_INEXISTENTE`. La implementación no cumple de forma consistente este contrato.

6. **Ruta inexistente**
   Una ruta que no existe debe responder status 404 con código `RUTA_INEXISTENTE`, en lugar de utilizar una respuesta genérica del servidor.

7. **Formato de los importes**
   La especificación exige que `subtotal`, `descuento`, `envio` y `total` se envíen en el JSON como texto. La implementación puede devolverlos como valores numéricos.

8. **Errores controlados con status 500**
   Los errores contemplados por la especificación nunca deberían provocar un status 500. La implementación actual contiene caminos de ejecución que pueden terminar como errores internos del servidor en vez de respuestas controladas.


## Falla detectada — R3: cantidad máxima

Se agregó un test para verificar que una cantidad de `10` unidades sea aceptada, ya que la especificación establece un rango válido de 1 a 10 inclusive.

Al ejecutar:

`python -m pytest -q test_checkout.py::test_cantidad_diez_es_valida`

el test falló con el error `CANTIDAD_INVALIDA`.

La causa es que la validación actual utiliza la condición:

`1 <= cantidad < 10`

por lo que el valor 10 queda excluido incorrectamente.


## Falla detectada — R5: descuento desde 5 prendas

Se agregó un test para verificar que una compra de exactamente 5 prendas reciba el 10% de descuento por cantidad.

Al ejecutar:

`python -m pytest -q test_checkout.py::test_cinco_prendas_aplican_descuento`

el test falló porque el sistema devolvió un descuento de `0` en lugar de `1000.00`.

La causa es que la implementación utiliza la condición `cantidad_prendas > 5`, por lo que el descuento recién se aplica a partir de 6 prendas. Según la especificación, debe aplicarse desde 5 prendas inclusive.


## Falla detectada — R2: normalización del talle

Se agregó un test para verificar que un talle con espacios alrededor, por ejemplo `"  M "`, sea aceptado como `M`.

Al ejecutar:

`python -m pytest -q test_checkout.py::test_talle_con_espacios_es_valido`

el test falló con `TALLE_INVALIDO`.

La causa es que la implementación convierte el talle a mayúsculas, pero no elimina los espacios al inicio y al final antes de validarlo.


## Falla detectada — R4: modificación del carrito

Se agregó un test para verificar que `validar_item` no modifique el ítem recibido.

Al ejecutar:

`python -m pytest -q test_checkout.py::test_validar_item_no_modifica_el_item`

el test falló porque el valor del talle fue modificado de `"m"` a `"M"` dentro del mismo diccionario.

La causa es que la implementación normaliza el talle mediante una asignación directa sobre `item["talle"]`, alterando el objeto original recibido.


## Falla detectada — R1: producto inexistente

Se agregó un test para verificar que un producto que no pertenece al catálogo genere el error `PRODUCTO_INEXISTENTE`.

Al ejecutar:

`python -m pytest -q test_checkout.py::test_producto_inexistente_lanza_error`

el test falló porque no se lanzó ningún `CheckoutError`.

La causa es que `calcular_subtotal` captura el error al buscar un producto inexistente y continúa con el siguiente ítem, ignorando silenciosamente el producto inválido en lugar de informar el error correspondiente.


## Falla detectada — R4: carrito vacío

Se agregó un test para verificar que un carrito vacío produzca el error `CARRITO_VACIO`.

Al ejecutar:

`python -m pytest -q test_checkout.py::test_carrito_vacio_lanza_error`

el test falló porque `calcular_subtotal([])` no lanzó ningún `CheckoutError`.

La implementación actual devuelve un subtotal de cero para una lista vacía, en lugar de rechazarla según lo indicado por la especificación.


## Falla detectada — R7: cálculo de cupón con Decimal

Se agregó un test para verificar que el cupón `EGRESADOS2026` aplique correctamente un descuento del 15%.

Al ejecutar:

`python -m pytest -q test_checkout.py::test_cupon_egresados_aplica_15_por_ciento`

el test falló con un `TypeError` porque el cálculo intenta multiplicar un valor `Decimal` por un `float`.

La especificación exige que todos los importes monetarios se manejen utilizando `Decimal`, por lo que los porcentajes de los cupones también deben ser compatibles con ese tipo.

## Falla detectada — R6: fecha de vencimiento inclusiva

Se agregó un test para verificar que el cupón `EGRESADOS2026` sea válido el día 30/11/2026, ya que la especificación establece esa fecha como último día de vigencia inclusive.

Al ejecutar:

`python -m pytest -q test_checkout.py::test_cupon_egresados_valido_en_fecha_de_vencimiento`

el test falló con el error `CUPON_VENCIDO`.

La causa es que la implementación utiliza una comparación estricta que exige que la fecha sea anterior al vencimiento, excluyendo incorrectamente el propio día 30/11/2026.

## Falla detectada — R6: normalización del cupón

Se agregó un test para verificar que los códigos de cupón sean aceptados aunque se ingresen con espacios alrededor y en minúsculas.

Al ejecutar:

`python -m pytest -q test_checkout.py::test_cupon_acepta_minusculas_y_espacios`

el test falló con el error `CUPON_INVALIDO`.

La causa es que la implementación elimina los espacios mediante `strip()`, pero no normaliza el código a mayúsculas antes de compararlo con los cupones definidos.

## Falla detectada — R6: cupón vacío

Se agregó un test para verificar que un cupón vacío o compuesto únicamente por espacios sea tratado como ausencia de cupón.

Al ejecutar:

`python -m pytest -q test_checkout.py::test_cupon_vacio_no_genera_error`

el test falló con el error `CUPON_INVALIDO`.

La causa es que, luego de normalizar el valor con `strip()`, el código vacío se intenta validar igualmente contra la tabla de cupones, en lugar de interpretarse como que no se ingresó ningún cupón.

## Fallos detectados en integración — R10

### Persistencia parcial ante error de checkout

El test `test_si_checkout_falla_no_queda_pedido_guardado` verificó que un pedido inválido no deje registros persistidos.

El test falló porque, luego de producirse un `CheckoutError`, quedó un registro en la tabla `pedidos`.

Esto demuestra que la operación no es atómica y que el pedido se persiste parcialmente antes de completar correctamente el checkout.

### Pedido incompleto visto desde otra conexión

El test `test_otra_conexion_ve_el_pedido_completo` verificó que un pedido guardado pueda consultarse completamente desde una segunda conexión a la misma base.

El test encontró el pedido, pero la lista de ítems estaba vacía.

Esto indica que los datos del pedido y sus ítems no quedan confirmados correctamente dentro de una única transacción.

### Precio enviado por el cliente almacenado incorrectamente

El test `test_precio_enviado_por_cliente_se_ignora` verificó que el precio unitario guardado corresponda siempre al catálogo.

El resultado recuperado fue `1` en lugar de `24999.90`.

Esto demuestra que `pedidos.py` permite que un precio enviado por el cliente termine persistido, incumpliendo la regla que exige utilizar siempre el precio oficial del catálogo.

## Fallos detectados en E2E — R11

### JSON inválido devuelve status incorrecto

El test `test_json_invalido_devuelve_400` verificó que un cuerpo que no contiene JSON válido responda con status `400` y código `JSON_INVALIDO`.

El test falló porque la API respondió con status `500`.

Esto demuestra que el error de JSON inválido no está siendo manejado como un error controlado de entrada.

### Datos incompletos devuelven status incorrecto

El test `test_datos_incompletos_devuelve_400` verificó que la ausencia de un campo obligatorio produzca status `400` y código `DATOS_INCOMPLETOS`.

El test falló porque la API respondió con status `500`.

Esto demuestra que la validación de datos obligatorios no está siendo manejada correctamente antes de procesar el pedido.

### CheckoutError devuelve status incorrecto

El test `test_error_de_checkout_devuelve_422` verificó que un error de negocio, en este caso un talle inválido, responda con status `422` preservando el código `TALLE_INVALIDO`.

El test falló porque la API respondió con status `500`.

Esto demuestra que los `CheckoutError` no están siendo traducidos correctamente a respuestas HTTP controladas.

### Ruta inexistente

El test correspondiente a una ruta inexistente pasó correctamente.

Esto confirma que, para este caso, la API responde de acuerdo con el comportamiento esperado por la especificación.


## Tabla final de hallazgos

| Severidad | Archivo / línea original | Categoría | Regla | Hallazgo | Cómo se encontró |
|---|---|---|---|---|---|
| Alta | `pedidos.py:39-50` | efectos laterales | R10 | Se hace commit del pedido antes de calcular el checkout; si falla, queda persistido parcialmente. | Revisión + test de integración |
| Alta | `pedidos.py:63-71` | efectos laterales | R10 | No se hace commit después de guardar los ítems y montos. Otra conexión puede ver el pedido incompleto. | Revisión + test de integración |
| Alta | `pedidos.py:64-68` | seguridad / lógica | R10 | Se acepta y persiste el precio enviado por el cliente en lugar del precio del catálogo. | Revisión + test de integración |
| Alta | `pedidos.py:104-108` | seguridad | R10 | `pedidos_de` concatena el email directamente en SQL mediante un f-string. | Revisión manual |
| Alta | `api.py:30-54` | manejo de errores | R11 | Cualquier excepción durante POST se convierte en HTTP 500. | Revisión + E2E |
| Alta | `api.py:32` | manejo de errores | R11 | JSON inválido devuelve HTTP 500 en lugar de `400 / JSON_INVALIDO`. | Test E2E |
| Alta | `api.py:37-41` | manejo de errores | R11 | Datos obligatorios faltantes terminan como HTTP 500 en lugar de `400 / DATOS_INCOMPLETOS`. | Test E2E |
| Alta | `api.py:35-42,53-54` | manejo de errores | R11 | Un `CheckoutError` se transforma en HTTP 500 en lugar de conservar el código y responder 422. | Test E2E |
| Alta | `checkout.py:49` | lógica / seguridad | R1 | El precio enviado por el cliente puede reemplazar al precio oficial del catálogo. | Revisión manual |
| Alta | `checkout.py:60-61` | lógica y límites | R5 | El descuento se aplica con más de 5 prendas y no desde 5 inclusive. | Mutation testing + TDD |
| Alta | `checkout.py:61,74,82` | numéricos | R7 | Se mezclan `float` y valores monetarios, incumpliendo el uso de `Decimal`. | Revisión + tests |
| Alta | `checkout.py:109-111` | lógica | R6/R9 | Los descuentos por cantidad y cupón pueden acumularse en lugar de elegir únicamente el mayor. | Revisión manual |
| Alta | `checkout.py:110` | lógica y límites | R8 | El envío gratis se calcula usando el subtotal anterior al descuento. | Revisión manual |
| Media | `checkout.py:40` | lógica y límites | R3 | La cantidad 10 era rechazada por utilizar `< 10`. | Mutation testing + TDD |
| Media | `checkout.py:44-54` | lógica | R4 | Un carrito vacío devolvía subtotal 0 en vez de `CARRITO_VACIO`. | TDD |
| Media | `checkout.py:48-51` | manejo de errores | R1 | Un producto inexistente era ignorado mediante `except/continue`. | Revisión + TDD |
| Media | `checkout.py:35` | strings | R2 | No se eliminaban espacios alrededor del talle. | TDD |
| Media | `checkout.py:35` | efectos laterales | R4 | La validación modificaba el talle dentro del objeto original. | TDD |
| Media | `checkout.py:23` | alucinación | R6 | Existe un cupón `DEBUG100` que no figura en la especificación. | Revisión manual |
| Media | `checkout.py:64` | strings | R6 | El cupón no se normalizaba a mayúsculas. | TDD |
| Media | `checkout.py:64-67` | strings / manejo de errores | R6 | Un cupón vacío o con espacios se interpretaba como cupón inválido. | TDD |
| Media | `checkout.py:72` | fechas / límites | R6 | `EGRESADOS2026` se consideraba vencido el mismo 30/11/2026. | Mutation testing + TDD |
| Media | `checkout.py:84` | numéricos | R7 | No se aplicaba de forma consistente el redondeo monetario requerido con `Decimal`. | Revisión manual |
| Media | `checkout.py:90-94` | manejo de errores | R8 | Una zona inválida provocaba `AttributeError` por uso incorrecto de `join`. | Test unitario |
| Media | `checkout.py:12-16,26-30` | tipos | R7 | Catálogo y envíos estaban definidos con `float`/enteros en lugar de `Decimal`. | Revisión + tests |
| Media | `checkout.py:113-118` | tipos | R7/R9 | Los valores devueltos no estaban garantizados como `Decimal`. | Revisión manual |
| Media | `pedidos.py:12-23` | tipos / numéricos | R10 | Los montos de SQLite se almacenan como `REAL`. | Revisión manual |
| Media | `pedidos.py:55-58` | numéricos | R10 | Los `Decimal` se convierten a `float` antes de persistirlos. | Revisión manual |
| Media | `pedidos.py:88-97` | numéricos | R10 | Se construyen `Decimal` directamente desde valores `float` recuperados. | Revisión manual |
| Media | `api.py:18` | tipos | R11 | `json.dumps(..., default=float)` convierte importes a números JSON en vez de texto. | Revisión manual |
| Media | `api.py:62-68` | manejo de errores | R11 | Un pedido inexistente no se transforma explícitamente en `404 / PEDIDO_INEXISTENTE`. | Revisión manual |
| Baja | `checkout.py:57,102` | code smell / fechas | R6 | `date.today()` se evalúa como argumento por defecto al cargar el módulo. | Ruff |
| Baja | `checkout.py:63` | code smell | — | Se compara con `None` mediante `!=` en vez de `is not None`. | Ruff |
| Baja | `checkout.py:50` | code smell / manejo de errores | R1 | Se utilizaba un `except` genérico. | Ruff |
| Baja | `checkout.py:1` | code smell | — | Importación de `json` sin utilizar. | Ruff |
| Baja | `checkout.py:34-41` | lógica | R1-R3 | El orden de validación no seguía producto → talle → cantidad indicado por la especificación. | Revisión manual |

### Resumen de resultados de pruebas

- Suite provista por la IA: mutation score **58,6%**.
- Suite unitaria desarrollada: **19 tests**.
- Cobertura de `checkout.py`: **97%**.
- Mutation score final: **86,7%**.
- Tests de integración: **4**, de los cuales **3 demostraron fallas** del código recibido.
- Tests E2E: **4**, de los cuales **3 demostraron fallas** del código recibido.


### Cobertura alta no implica buenos tests

Que una suite ejecute cerca del 80% del código no significa que compruebe correctamente su comportamiento. La cobertura indica qué líneas o ramas fueron ejecutadas, pero no si las aserciones fueron suficientemente precisas para detectar resultados incorrectos. En este TP, los ocho tests de la IA pasaban, pero el mutation testing obtuvo solamente 58,6%, con 12 mutantes sobrevivientes. Por ejemplo, cambios en el límite de cantidad, el descuento desde cinco prendas y el cálculo del total no eran detectados. Esto demuestra que varios tests recorrían el código, pero realizaban comprobaciones demasiado débiles o no cubrían valores límite relevantes.

