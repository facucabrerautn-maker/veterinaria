-- C-08: un UPDATE directo en la base que viola el CHECK de la práctica.
--
-- Correr con psql o pgAdmin DESPUÉS de:  python reiniciar.py
--
-- Resultado esperado: la base RECHAZA la sentencia con un error parecido a:
--   ERROR: new row for relation "practica" violates check constraint "ck_practica_precio_positivo"
-- y el precio de la práctica 1 no cambia.

UPDATE practica SET precio = 0 WHERE id = 1;

-- Comprobación: el precio sigue siendo 15000.00
SELECT id, nombre, precio FROM practica WHERE id = 1;
