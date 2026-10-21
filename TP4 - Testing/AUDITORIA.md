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