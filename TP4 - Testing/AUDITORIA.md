## Auditoría de los tests provistos por la IA

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


## Sección 1 — Evaluación de los tests de la IA

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