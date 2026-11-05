-- Consultas de comprobación para los casos C-04 y C-05.
-- Correr con psql o pgAdmin. Los resultados esperados están en los comentarios.

-- C-04: después de los pedidos de turno que fallaron (práctica inexistente,
-- mascota inexistente, práctica repetida) no debe haber quedado ningún turno
-- extra. Tras reiniciar.py y el C-06, la tabla debe tener solo el turno inicial
-- (id 1) y el creado en C-06.
SELECT id, mascota_id, motivo, total FROM turno ORDER BY id;

-- Tampoco deben existir filas de turno_practica huérfanas (sin turno):
-- Esperado: 0 filas
SELECT tp.*
FROM turno_practica tp
LEFT JOIN turno t ON t.id = tp.turno_id
WHERE t.id IS NULL;

-- C-05: después de DELETE /turnos/1, las prácticas de ese turno ya no están.
-- Esperado: 0
SELECT count(*) AS practicas_del_turno_1 FROM turno_practica WHERE turno_id = 1;

-- C-05: el dueño 1 sigue existiendo (el borrado fue rechazado con 409).
-- Esperado: 1 fila
SELECT id, nombre FROM duenio WHERE id = 1;
