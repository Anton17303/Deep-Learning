"""Escribe datos/validacion/preguntas.jsonl (40 preguntas, 2 esquemas ajenos al
entrenamiento) y comprueba que cada SQL de referencia se ejecuta y no es vacío.
Borrador generado con ayuda de IA: revisar y ajustar antes de reportar (ver README)."""
import json
from pathlib import Path

from .bd import conectar

RAIZ = Path(__file__).resolve().parent.parent
PESO = {1: 1, 2: 2, 3: 3}

H = "hotel_full"
F = "futbol_full"
# (esquema, nivel, ordenado, pregunta, sql)
V = [
 # ------------------------------------------------------------------ hotel
 (H,1,False,"Devuelve nombre y ciudad de los hoteles con 4 o más estrellas.",
  "SELECT nombre, ciudad FROM hoteles WHERE estrellas >= 4"),
 (H,1,False,"¿Cuántas reservaciones tienen estado 'cancelada'? Devuelve una sola columna con el total.",
  "SELECT COUNT(*) AS total FROM reservaciones WHERE estado = 'cancelada'"),
 (H,1,True,"Devuelve nombre y tarifa por noche de los tipos de habitación, ordenados de mayor a menor tarifa.",
  "SELECT nombre, tarifa_noche FROM tipos_habitacion ORDER BY tarifa_noche DESC"),
 (H,1,False,"¿Cuál es el precio promedio de los servicios? Devuelve una sola columna.",
  "SELECT AVG(precio) AS promedio FROM servicios"),
 (H,1,False,"Devuelve nombre y correo de los huéspedes cuyo país es 'Guatemala'.",
  "SELECT nombre, correo FROM huespedes WHERE pais = 'Guatemala'"),
 (H,1,False,"Devuelve el número de habitación y el piso de las habitaciones ubicadas en el piso 5.",
  "SELECT numero, piso FROM habitaciones WHERE piso = 5"),
 (H,2,False,"Devuelve el nombre de los hoteles con habitaciones registradas y cuántas habitaciones tiene cada uno (columna total).",
  "SELECT h.nombre, COUNT(*) AS total FROM hoteles h JOIN habitaciones x ON x.id_hotel = h.id_hotel GROUP BY h.id_hotel, h.nombre"),
 (H,2,False,"Devuelve el nombre de los huéspedes que suman más de 15 noches reservadas, junto con ese total (columna total_noches).",
  "SELECT g.nombre, SUM(r.noches) AS total_noches FROM huespedes g JOIN reservaciones r ON r.id_huesped = g.id_huesped GROUP BY g.id_huesped, g.nombre HAVING SUM(r.noches) > 15"),
 (H,2,True,"Para cada canal de reservación devuelve el canal y el número de reservaciones (columna total), ordenado de mayor a menor total y, en caso de empate, por canal alfabéticamente.",
  "SELECT canal, COUNT(*) AS total FROM reservaciones GROUP BY canal ORDER BY total DESC, canal"),
 (H,2,False,"Para cada tipo de habitación que tenga habitaciones físicas registradas, devuelve su nombre y la cantidad de habitaciones de ese tipo (columna total).",
  "SELECT t.nombre, COUNT(*) AS total FROM tipos_habitacion t JOIN habitaciones h ON h.id_tipo = t.id_tipo GROUP BY t.id_tipo, t.nombre"),
 (H,2,False,"Devuelve el nombre de los servicios con consumos registrados y el total de unidades consumidas de cada servicio (columna unidades).",
  "SELECT s.nombre, SUM(c.cantidad) AS unidades FROM servicios s JOIN consumos c ON c.id_servicio = s.id_servicio GROUP BY s.id_servicio, s.nombre"),
 (H,2,False,"Devuelve el nombre del huésped y el nombre del hotel de las reservaciones con estado 'completada' y más de 7 noches.",
  "SELECT g.nombre, h.nombre FROM reservaciones r JOIN huespedes g ON g.id_huesped = r.id_huesped JOIN habitaciones a ON a.id_habitacion = r.id_habitacion JOIN hoteles h ON h.id_hotel = a.id_hotel WHERE r.estado = 'completada' AND r.noches > 7"),
 (H,2,False,"Devuelve el nombre de los hoteles cuya tarifa por noche promedio de sus habitaciones supera 1300, junto con ese promedio (columna promedio).",
  "SELECT h.nombre, AVG(t.tarifa_noche) AS promedio FROM hoteles h JOIN habitaciones a ON a.id_hotel = h.id_hotel JOIN tipos_habitacion t ON t.id_tipo = a.id_tipo GROUP BY h.id_hotel, h.nombre HAVING AVG(t.tarifa_noche) > 1300"),
 (H,3,False,"Devuelve el nombre de los huéspedes que nunca han hecho una reservación.",
  "SELECT g.nombre FROM huespedes g WHERE NOT EXISTS (SELECT 1 FROM reservaciones r WHERE r.id_huesped = g.id_huesped)"),
 (H,3,False,"Devuelve id de la reservación, canal y noches de las reservaciones cuyas noches superan el promedio de noches de su mismo canal.",
  "SELECT a.id_reservacion, a.canal, a.noches FROM reservaciones a WHERE a.noches > (SELECT AVG(b.noches) FROM reservaciones b WHERE b.canal = a.canal)"),
 (H,3,True,"¿Qué servicio genera el mayor ingreso por consumos (precio del servicio por cantidad consumida)? Devuelve el nombre del servicio y el ingreso (columna ingreso).",
  "SELECT s.nombre, SUM(s.precio * c.cantidad) AS ingreso FROM servicios s JOIN consumos c ON c.id_servicio = s.id_servicio GROUP BY s.id_servicio, s.nombre ORDER BY ingreso DESC LIMIT 1"),
 (H,3,False,"Para cada hotel con reservaciones registradas, devuelve la reservación con más noches (en caso de empate, la de menor id de reservación): nombre del hotel, id de la reservación y noches.",
  "WITH r AS (SELECT h.nombre AS hotel, v.id_reservacion, v.noches, ROW_NUMBER() OVER (PARTITION BY h.id_hotel ORDER BY v.noches DESC, v.id_reservacion) AS rn FROM reservaciones v JOIN habitaciones a ON a.id_habitacion = v.id_habitacion JOIN hoteles h ON h.id_hotel = a.id_hotel) SELECT hotel, id_reservacion, noches FROM r WHERE rn = 1"),
 (H,3,True,"¿En qué mes (formato AAAA-MM) según la fecha de entrada hay más reservaciones? Devuelve el mes (columna mes) y el total de reservaciones (columna total). En caso de empate, devuelve el mes cronológicamente menor.",
  "SELECT DATE_FORMAT(fecha_entrada, '%Y-%m') AS mes, COUNT(*) AS total FROM reservaciones GROUP BY DATE_FORMAT(fecha_entrada, '%Y-%m') ORDER BY total DESC, mes LIMIT 1"),
 (H,3,True,"Toma las primeras 10 reservaciones ordenadas por fecha de entrada (y por id de reservación en empate) y devuelve id, fecha de entrada, noches y las noches acumuladas (columna acumulado).",
  "SELECT id_reservacion, fecha_entrada, noches, SUM(noches) OVER (ORDER BY fecha_entrada, id_reservacion) AS acumulado FROM reservaciones ORDER BY fecha_entrada, id_reservacion LIMIT 10"),
 (H,3,False,"¿Qué porcentaje del total de reservaciones representa cada estado? Devuelve el estado y el porcentaje con 2 decimales (columna porcentaje).",
  "SELECT estado, ROUND(100 * COUNT(*) / (SELECT COUNT(*) FROM reservaciones), 2) AS porcentaje FROM reservaciones GROUP BY estado"),
 # ----------------------------------------------------------------- futbol
 (F,1,False,"Devuelve nombre y capacidad de los estadios con capacidad mayor a 20000.",
  "SELECT nom, cap FROM est WHERE cap > 20000"),
 (F,1,False,"¿Cuántos jugadores juegan en la posición 'DEL'? Devuelve una sola columna con el total.",
  "SELECT COUNT(*) AS total FROM jug WHERE pos = 'DEL'"),
 (F,1,False,"¿Cuál es el salario promedio de todos los jugadores? Devuelve una sola columna.",
  "SELECT AVG(sal) AS promedio FROM jug"),
 (F,1,True,"Devuelve nombre y salario de los 5 jugadores con mayor salario, de mayor a menor.",
  "SELECT nom, sal FROM jug ORDER BY sal DESC LIMIT 5"),
 (F,1,False,"Devuelve nombre y año de fundación de los equipos fundados antes de 1960.",
  "SELECT nom, fund FROM equ WHERE fund < 1960"),
 (F,1,False,"¿Cuántas tarjetas rojas se han mostrado? Devuelve una sola columna con el total.",
  "SELECT COUNT(*) AS total FROM tar WHERE tipo = 'roja'"),
 (F,2,False,"Para cada equipo con jugadores registrados, devuelve el nombre del equipo y su cantidad de jugadores (columna total).",
  "SELECT e.nom, COUNT(*) AS total FROM equ e JOIN jug j ON j.id_equ = e.id_equ GROUP BY e.id_equ, e.nom"),
 (F,2,False,"Para cada equipo con jugadores registrados, devuelve el nombre del equipo y el salario promedio de sus jugadores (columna promedio).",
  "SELECT e.nom, AVG(j.sal) AS promedio FROM equ e JOIN jug j ON j.id_equ = e.id_equ GROUP BY e.id_equ, e.nom"),
 (F,2,False,"Devuelve el nombre de los jugadores con al menos 2 goles y su número de goles (columna goles).",
  "SELECT j.nom, COUNT(*) AS goles FROM jug j JOIN gol g ON g.id_jug = j.id_jug GROUP BY j.id_jug, j.nom HAVING COUNT(*) >= 2"),
 (F,2,False,"Devuelve el nombre de los equipos que han jugado al menos un partido como local y cuántos partidos han jugado en esa condición (columna total).",
  "SELECT e.nom, COUNT(*) AS total FROM equ e JOIN par p ON p.id_loc = e.id_equ GROUP BY e.id_equ, e.nom"),
 (F,2,False,"Para los estadios con un equipo registrado como local, devuelve el nombre del estadio y el nombre del equipo que juega allí.",
  "SELECT s.nom, e.nom FROM est s JOIN equ e ON e.id_est = s.id_est"),
 (F,2,False,"Devuelve el nombre de los jugadores con 2 o más tarjetas amarillas y cuántas tienen (columna total).",
  "SELECT j.nom, COUNT(*) AS total FROM jug j JOIN tar t ON t.id_jug = j.id_jug WHERE t.tipo = 'amarilla' GROUP BY j.id_jug, j.nom HAVING COUNT(*) >= 2"),
 (F,2,False,"Devuelve cada posición y la edad promedio de los jugadores de esa posición (columna edad_promedio).",
  "SELECT pos, AVG(edad) AS edad_promedio FROM jug GROUP BY pos"),
 (F,3,False,"Devuelve el nombre y la posición de los jugadores que nunca han anotado un gol y juegan como DEF.",
  "SELECT j.nom, j.pos FROM jug j WHERE j.pos = 'DEF' AND j.id_jug NOT IN (SELECT id_jug FROM gol)"),
 (F,3,False,"Para cada equipo con goles registrados, devuelve el nombre del equipo, el nombre de su máximo goleador (en empate, el de menor id de jugador) y sus goles (columna goles).",
  "WITH c AS (SELECT j.id_equ, j.id_jug, j.nom, COUNT(*) AS goles FROM jug j JOIN gol g ON g.id_jug = j.id_jug GROUP BY j.id_equ, j.id_jug, j.nom), r AS (SELECT c.*, ROW_NUMBER() OVER (PARTITION BY id_equ ORDER BY goles DESC, id_jug) AS rn FROM c) SELECT e.nom, r.nom, r.goles FROM r JOIN equ e ON e.id_equ = r.id_equ WHERE r.rn = 1"),
 (F,3,True,"Entre los equipos con goles registrados, calcula los goles anotados por sus jugadores. Devuelve el nombre del equipo, los goles (columna goles) y su posición con RANK de mayor a menor (columna posicion), ordenado por posición y nombre del equipo.",
  "WITH t AS (SELECT e.nom, COUNT(*) AS goles FROM equ e JOIN jug j ON j.id_equ = e.id_equ JOIN gol g ON g.id_jug = j.id_jug GROUP BY e.id_equ, e.nom) SELECT nom, goles, RANK() OVER (ORDER BY goles DESC) AS posicion FROM t ORDER BY posicion, nom"),
 (F,3,False,"Devuelve el nombre y el salario de los jugadores cuyo salario es mayor al promedio de su propio equipo.",
  "SELECT a.nom, a.sal FROM jug a WHERE a.sal > (SELECT AVG(b.sal) FROM jug b WHERE b.id_equ = a.id_equ)"),
 (F,3,False,"Devuelve el id de los partidos en los que se anotaron más de 2 goles en total y ese total (columna total).",
  "SELECT id_par, COUNT(*) AS total FROM gol GROUP BY id_par HAVING COUNT(*) > 2"),
 (F,3,True,"¿En qué jornada se anotaron más goles? Devuelve la jornada y el total de goles (columna total); en empate, la jornada menor.",
  "SELECT p.jor, COUNT(*) AS total FROM par p JOIN gol g ON g.id_par = p.id_par GROUP BY p.jor ORDER BY total DESC, p.jor LIMIT 1"),
 (F,3,False,"Devuelve nombre, posición y edad de los jugadores que son los más jóvenes de su posición (incluye empates).",
  "SELECT a.nom, a.pos, a.edad FROM jug a WHERE a.edad = (SELECT MIN(b.edad) FROM jug b WHERE b.pos = a.pos)"),
]


def main():
    sal = []
    con = {}
    for i, (esq, nivel, ordenado, preg, sql) in enumerate(V, 1):
        base = f"p3_{esq}"
        if base not in con:
            con[base] = conectar(base)
        cur = con[base].cursor()
        cur.execute(sql)
        n = len(cur.fetchall())
        assert n > 0, f"v{i:02d} vacío: {preg}"
        sal.append(dict(id=f"v{i:02d}", esquema_id=esq, nivel=nivel, peso=PESO[nivel],
                        pregunta=preg, sql_ref=sql, ordenado=ordenado, n_filas_ref=n))
    out = RAIZ / "datos/validacion/preguntas.jsonl"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in sal) + "\n", encoding="utf-8")
    por = {k: sum(1 for r in sal if r["nivel"] == k) for k in (1, 2, 3)}
    print(len(sal), "preguntas; por nivel", por, "; filas ref:", [r["n_filas_ref"] for r in sal])


if __name__ == "__main__":
    main()
