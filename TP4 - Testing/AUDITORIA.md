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