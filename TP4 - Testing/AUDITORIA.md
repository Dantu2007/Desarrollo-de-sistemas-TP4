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