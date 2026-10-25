"""Definición compacta de esquemas.

Cada columna se escribe como "nombre|tipo|comentario". Tipos:
  pk | fk:<tabla> | nom:<pool> | cat:a/b/c | int:lo:hi | dec:lo:hi | fec:y0:y1 | mail
La primera columna de cada tabla es la clave primaria.

Variantes de nombres:
  full -> identificadores tal como se escriben aquí.
  abr  -> identificadores abreviados (cli, ped, fech_ped...). Los COMMENT siguen
          en español completo, como en una base real con nombres cortos.
"""
import random
from dataclasses import dataclass, field

RESERVADAS = {
    "desc", "asc", "order", "group", "key", "rank", "row", "rows", "from", "to", "in", "is",
    "by", "as", "int", "date", "time", "year", "month", "day", "range", "read", "show", "use",
    "set", "all", "any", "and", "or", "not", "null", "like", "join", "left", "right", "inner",
    "case", "when", "then", "else", "end", "for", "if", "into", "on", "out", "dec", "real",
    "float", "char", "text", "blob", "long", "lock", "load", "keys", "index", "match", "mod",
    "over", "part", "with", "where", "while", "xor", "zerofill", "usage", "unique", "table",
    "fec", "lag", "lead", "cume_dist", "groups", "system", "window", "rol", "ref",
}

POOLS = {
    "persona": [f"{n} {a}" for n in ["Ana", "Luis", "María", "Carlos", "Sofía", "Pedro", "Lucía",
                                      "Diego", "Valeria", "Andrés", "Camila", "Jorge", "Paola",
                                      "Mateo", "Daniela", "Rafael", "Elena", "Samuel"]
                for a in ["López", "Pérez", "García", "Morales", "Ramírez", "Castillo", "Méndez"]],
    "ciudad": ["Guatemala", "Quetzaltenango", "Antigua", "Cobán", "Escuintla", "Huehuetenango",
               "Puerto Barrios", "Flores", "Chiquimula", "Zacapa", "Mazatenango", "Retalhuleu"],
    "pais": ["Guatemala", "México", "Costa Rica", "Colombia", "España", "Chile", "Argentina",
             "Estados Unidos", "Panamá", "Perú"],
    "producto": ["Laptop", "Mouse inalámbrico", "Teclado mecánico", "Monitor 24 pulgadas",
                 "Auriculares", "Cámara web", "Disco duro 1TB", "Impresora", "Silla ergonómica",
                 "Escritorio", "Lámpara LED", "Mochila", "Termo", "Libreta", "Cargador USB",
                 "Parlante", "Tableta", "Router", "Memoria USB", "Soporte para laptop"],
    "categoria": ["Electrónica", "Oficina", "Hogar", "Accesorios", "Papelería", "Audio", "Redes",
                  "Muebles"],
    "carrera": ["Ingeniería en Sistemas", "Ingeniería Civil", "Psicología", "Economía",
                "Biología", "Diseño Gráfico", "Química", "Matemática Aplicada"],
    "curso": ["Cálculo I", "Álgebra Lineal", "Programación", "Estadística", "Física I",
              "Bases de Datos", "Redes", "Ética", "Microeconomía", "Química General",
              "Algoritmos", "Inglés Técnico"],
    "especialidad": ["Pediatría", "Cardiología", "Dermatología", "Ortopedia", "Neurología",
                     "Medicina General", "Ginecología", "Oftalmología"],
    "medicamento": ["Paracetamol", "Ibuprofeno", "Amoxicilina", "Loratadina", "Omeprazol",
                    "Metformina", "Salbutamol", "Diclofenaco"],
    "libro": ["El viento y la sombra", "Cartas del volcán", "Mar de cenizas", "La ciudad quieta",
              "Los días del maíz", "Ruta al norte", "Memorias de un río", "Noche en Atitlán",
              "El mapa inconcluso", "Árboles de niebla", "Lluvia de abril", "El cartero lejano"],
    "editorial": ["Ediciones Maya", "Voces del Sur", "Tinta Nueva", "Océano Gris"],
    "aerolinea": ["Aerosur", "Vuelo Maya", "CentroAir", "Pacífico Jet", "Cielo Azul"],
    "aeropuerto": ["La Aurora", "Mundo Maya", "Tocumen", "Juan Santamaría", "Benito Juárez",
                   "El Dorado", "Barajas", "Jorge Chávez"],
    "sucursal": ["Zona 1", "Zona 4", "Zona 10", "Mixco", "Villa Nueva", "Xela Centro", "Cobán Norte"],
    "platillo": ["Pepián", "Jocon", "Kak'ik", "Tamales", "Hilachas", "Ceviche", "Churrasco",
                 "Ensalada Caesar", "Sopa de tortilla", "Flan", "Rellenitos", "Limonada",
                 "Café", "Horchata", "Pasta alfredo"],
    "depto": ["Ventas", "Finanzas", "Tecnología", "Recursos Humanos", "Operaciones", "Mercadeo",
              "Legal"],
    "puesto": ["Analista", "Gerente", "Asistente", "Desarrollador", "Contador", "Diseñador",
               "Supervisor", "Coordinador"],
    "pelicula": ["La última frontera", "Ecos del mañana", "Selva de acero", "Cartas a Marte",
                 "El faro", "Tormenta roja", "Domingo de lluvia", "Nube negra", "Código Aurora",
                 "Isla perdida"],
    "sala": ["Sala 1", "Sala 2", "Sala 3", "Sala VIP", "Sala IMAX", "Sala 5"],
    "almacen": ["Central", "Norte", "Sur", "Occidente", "Puerto", "Oriente"],
    "hotel": ["Hotel Quetzal", "Casa del Lago", "Hotel Volcán", "Posada del Sol", "Gran Maya",
              "Hotel Ceiba"],
    "servicio": ["Desayuno", "Spa", "Lavandería", "Minibar", "Transporte aeropuerto",
                 "Tour guiado", "Cena", "Estacionamiento"],
    "equipo": ["Leones", "Halcones", "Titanes", "Águilas", "Jaguares", "Tiburones", "Cóndores",
               "Pumas"],
    "estadio": ["Estadio Central", "Coloso Norte", "Estadio del Valle", "Arena Sur",
                "Campo Mayor"],
    "generico": ["Alfa", "Beta", "Gamma", "Delta", "Épsilon", "Zeta", "Eta", "Theta"],
}

# ---------------------------------------------------------------- esquemas ---
ESQUEMAS = {
    "tienda": ("train", [
        ("categorias", "Categorías de productos", 8, [
            "id_categoria|pk|Identificador de la categoría",
            "nombre|nom:categoria|Nombre de la categoría"]),
        ("clientes", "Clientes registrados en la tienda", 60, [
            "id_cliente|pk|Identificador del cliente",
            "nombre|nom:persona|Nombre completo del cliente",
            "correo|mail|Correo electrónico",
            "ciudad|nom:ciudad|Ciudad de residencia",
            "fecha_registro|fec:2021:2025|Fecha en que se registró"]),
        ("productos", "Catálogo de productos", 40, [
            "id_producto|pk|Identificador del producto",
            "nombre|nom:producto|Nombre del producto",
            "id_categoria|fk:categorias|Categoría del producto",
            "precio|dec:5:500|Precio de venta en quetzales",
            "stock|int:0:300|Unidades disponibles en inventario"]),
        ("pedidos", "Pedidos realizados por los clientes", 250, [
            "id_pedido|pk|Identificador del pedido",
            "id_cliente|fk:clientes|Cliente que hizo el pedido",
            "fecha_pedido|fec:2023:2025|Fecha del pedido",
            "estado|cat:pendiente/enviado/entregado/cancelado|Estado del pedido",
            "total|dec:10:2000|Monto total del pedido en quetzales"]),
        ("detalle_pedido", "Líneas de cada pedido", 600, [
            "id_detalle|pk|Identificador de la línea",
            "id_pedido|fk:pedidos|Pedido al que pertenece",
            "id_producto|fk:productos|Producto vendido",
            "cantidad|int:1:10|Unidades vendidas",
            "precio_unitario|dec:5:500|Precio unitario aplicado"]),
    ]),
    "universidad": ("train", [
        ("carreras", "Carreras que ofrece la universidad", 8, [
            "id_carrera|pk|Identificador de la carrera",
            "nombre|nom:carrera|Nombre de la carrera",
            "facultad|cat:Ingenieria/Humanidades/Ciencias/Economia|Facultad a la que pertenece"]),
        ("estudiantes", "Estudiantes matriculados", 80, [
            "id_estudiante|pk|Identificador del estudiante",
            "nombre|nom:persona|Nombre del estudiante",
            "id_carrera|fk:carreras|Carrera que cursa",
            "fecha_ingreso|fec:2018:2025|Fecha de ingreso",
            "promedio|dec:60:100|Promedio general acumulado",
            "becado|cat:si/no|Indica si tiene beca"]),
        ("profesores", "Catedráticos", 15, [
            "id_profesor|pk|Identificador del profesor",
            "nombre|nom:persona|Nombre del profesor",
            "departamento|cat:Matematica/Computacion/Fisica/Humanidades|Departamento académico",
            "salario|dec:5000:20000|Salario mensual en quetzales"]),
        ("cursos", "Cursos del catálogo", 12, [
            "id_curso|pk|Identificador del curso",
            "nombre|nom:curso|Nombre del curso",
            "id_profesor|fk:profesores|Profesor titular",
            "creditos|int:2:6|Créditos del curso"]),
        ("inscripciones", "Inscripciones de estudiantes a cursos", 400, [
            "id_inscripcion|pk|Identificador de la inscripción",
            "id_estudiante|fk:estudiantes|Estudiante inscrito",
            "id_curso|fk:cursos|Curso al que se inscribió",
            "semestre|cat:2024-1/2024-2/2025-1/2025-2|Semestre de la inscripción",
            "nota|int:40:100|Nota final obtenida"]),
    ]),
    "clinica": ("train", [
        ("especialidades", "Especialidades médicas", 8, [
            "id_especialidad|pk|Identificador de la especialidad",
            "nombre|nom:especialidad|Nombre de la especialidad"]),
        ("medicos", "Médicos de la clínica", 20, [
            "id_medico|pk|Identificador del médico",
            "nombre|nom:persona|Nombre del médico",
            "id_especialidad|fk:especialidades|Especialidad del médico",
            "anios_experiencia|int:1:35|Años de experiencia"]),
        ("pacientes", "Pacientes registrados", 90, [
            "id_paciente|pk|Identificador del paciente",
            "nombre|nom:persona|Nombre del paciente",
            "fecha_nacimiento|fec:1950:2015|Fecha de nacimiento",
            "ciudad|nom:ciudad|Ciudad de residencia"]),
        ("medicamentos", "Medicamentos disponibles", 8, [
            "id_medicamento|pk|Identificador del medicamento",
            "nombre|nom:medicamento|Nombre del medicamento",
            "precio|dec:5:300|Precio unitario"]),
        ("citas", "Citas médicas", 300, [
            "id_cita|pk|Identificador de la cita",
            "id_paciente|fk:pacientes|Paciente atendido",
            "id_medico|fk:medicos|Médico que atendió",
            "fecha_cita|fec:2024:2025|Fecha de la cita",
            "motivo|cat:control/emergencia/seguimiento/primera_vez|Motivo de la consulta",
            "costo|dec:100:1500|Costo de la consulta"]),
        ("recetas", "Medicamentos recetados en cada cita", 350, [
            "id_receta|pk|Identificador de la receta",
            "id_cita|fk:citas|Cita en que se recetó",
            "id_medicamento|fk:medicamentos|Medicamento recetado",
            "dias_tratamiento|int:3:30|Duración del tratamiento en días"]),
    ]),
    "biblioteca": ("train", [
        ("autores", "Autores de los libros", 15, [
            "id_autor|pk|Identificador del autor",
            "nombre|nom:persona|Nombre del autor",
            "pais|nom:pais|País de origen"]),
        ("libros", "Libros del acervo", 60, [
            "id_libro|pk|Identificador del libro",
            "titulo|nom:libro|Título del libro",
            "id_autor|fk:autores|Autor del libro",
            "anio_publicacion|int:1950:2023|Año de publicación",
            "paginas|int:80:900|Número de páginas",
            "genero|cat:novela/ensayo/poesia/historia/ciencia|Género literario"]),
        ("socios", "Socios de la biblioteca", 70, [
            "id_socio|pk|Identificador del socio",
            "nombre|nom:persona|Nombre del socio",
            "fecha_alta|fec:2019:2025|Fecha de alta como socio"]),
        ("prestamos", "Préstamos de libros", 350, [
            "id_prestamo|pk|Identificador del préstamo",
            "id_libro|fk:libros|Libro prestado",
            "id_socio|fk:socios|Socio que lo solicitó",
            "fecha_prestamo|fec:2024:2025|Fecha del préstamo",
            "dias_prestamo|int:3:30|Días de préstamo concedidos",
            "devuelto|cat:si/no|Indica si ya fue devuelto"]),
    ]),
    "aerolinea": ("train", [
        ("aerolineas", "Aerolíneas que operan", 5, [
            "id_aerolinea|pk|Identificador de la aerolínea",
            "nombre|nom:aerolinea|Nombre de la aerolínea",
            "pais|nom:pais|País sede"]),
        ("aeropuertos", "Aeropuertos", 8, [
            "id_aeropuerto|pk|Identificador del aeropuerto",
            "nombre|nom:aeropuerto|Nombre del aeropuerto",
            "ciudad|nom:ciudad|Ciudad donde se ubica"]),
        ("vuelos", "Vuelos programados", 120, [
            "id_vuelo|pk|Identificador del vuelo",
            "id_aerolinea|fk:aerolineas|Aerolínea que opera",
            "id_origen|fk:aeropuertos|Aeropuerto de origen",
            "id_destino|fk:aeropuertos|Aeropuerto de destino",
            "fecha_salida|fec:2025:2025|Fecha de salida",
            "duracion_min|int:45:600|Duración en minutos",
            "precio_base|dec:50:1500|Precio base del boleto"]),
        ("pasajeros", "Pasajeros", 100, [
            "id_pasajero|pk|Identificador del pasajero",
            "nombre|nom:persona|Nombre del pasajero",
            "pais|nom:pais|País de residencia"]),
        ("reservas", "Reservas de asientos", 450, [
            "id_reserva|pk|Identificador de la reserva",
            "id_vuelo|fk:vuelos|Vuelo reservado",
            "id_pasajero|fk:pasajeros|Pasajero",
            "clase|cat:economica/ejecutiva/primera|Clase de servicio",
            "equipaje_kg|int:0:40|Kilos de equipaje"]),
    ]),
    "banco": ("train", [
        ("sucursales", "Sucursales del banco", 7, [
            "id_sucursal|pk|Identificador de la sucursal",
            "nombre|nom:sucursal|Nombre de la sucursal",
            "ciudad|nom:ciudad|Ciudad"]),
        ("clientes", "Clientes del banco", 80, [
            "id_cliente|pk|Identificador del cliente",
            "nombre|nom:persona|Nombre del cliente",
            "fecha_alta|fec:2015:2025|Fecha de alta"]),
        ("cuentas", "Cuentas bancarias", 120, [
            "id_cuenta|pk|Identificador de la cuenta",
            "id_cliente|fk:clientes|Titular de la cuenta",
            "id_sucursal|fk:sucursales|Sucursal donde se abrió",
            "tipo|cat:ahorro/monetaria/plazo_fijo|Tipo de cuenta",
            "saldo|dec:100:90000|Saldo actual",
            "fecha_apertura|fec:2016:2025|Fecha de apertura"]),
        ("transacciones", "Movimientos de las cuentas", 700, [
            "id_transaccion|pk|Identificador del movimiento",
            "id_cuenta|fk:cuentas|Cuenta afectada",
            "tipo|cat:deposito/retiro/transferencia|Tipo de movimiento",
            "monto|dec:10:5000|Monto del movimiento",
            "fecha|fec:2024:2025|Fecha del movimiento"]),
        ("prestamos", "Préstamos otorgados", 50, [
            "id_prestamo|pk|Identificador del préstamo",
            "id_cliente|fk:clientes|Cliente que recibió el préstamo",
            "monto|dec:1000:80000|Monto otorgado",
            "plazo_meses|int:6:120|Plazo en meses",
            "estado|cat:vigente/pagado/mora|Estado del préstamo"]),
    ]),
    "restaurante": ("train", [
        ("meseros", "Personal de servicio", 12, [
            "id_mesero|pk|Identificador del mesero",
            "nombre|nom:persona|Nombre del mesero",
            "fecha_contratacion|fec:2018:2025|Fecha de contratación"]),
        ("mesas", "Mesas del restaurante", 15, [
            "id_mesa|pk|Identificador de la mesa",
            "capacidad|int:2:10|Personas que caben",
            "zona|cat:terraza/salon/barra|Zona del local"]),
        ("platillos", "Menú", 15, [
            "id_platillo|pk|Identificador del platillo",
            "nombre|nom:platillo|Nombre del platillo",
            "categoria|cat:entrada/fuerte/postre/bebida|Categoría del menú",
            "precio|dec:15:200|Precio en quetzales"]),
        ("ordenes", "Órdenes atendidas", 300, [
            "id_orden|pk|Identificador de la orden",
            "id_mesa|fk:mesas|Mesa atendida",
            "id_mesero|fk:meseros|Mesero responsable",
            "fecha|fec:2024:2025|Fecha de la orden",
            "propina|dec:0:60|Propina recibida"]),
        ("detalle_orden", "Platillos de cada orden", 800, [
            "id_detalle|pk|Identificador de la línea",
            "id_orden|fk:ordenes|Orden",
            "id_platillo|fk:platillos|Platillo pedido",
            "cantidad|int:1:5|Cantidad pedida"]),
    ]),
    "rrhh": ("train", [
        ("departamentos", "Departamentos de la empresa", 7, [
            "id_departamento|pk|Identificador del departamento",
            "nombre|nom:depto|Nombre del departamento",
            "ubicacion|nom:ciudad|Ciudad de la oficina"]),
        ("puestos", "Puestos de trabajo", 8, [
            "id_puesto|pk|Identificador del puesto",
            "titulo|nom:puesto|Título del puesto",
            "salario_base|dec:3000:25000|Salario base mensual"]),
        ("empleados", "Empleados", 100, [
            "id_empleado|pk|Identificador del empleado",
            "nombre|nom:persona|Nombre del empleado",
            "id_departamento|fk:departamentos|Departamento al que pertenece",
            "id_puesto|fk:puestos|Puesto que ocupa",
            "fecha_contratacion|fec:2015:2025|Fecha de contratación",
            "modalidad|cat:presencial/remoto/hibrido|Modalidad de trabajo"]),
        ("asistencias", "Registro diario de asistencia", 700, [
            "id_asistencia|pk|Identificador del registro",
            "id_empleado|fk:empleados|Empleado",
            "fecha|fec:2025:2025|Fecha de asistencia",
            "horas_trabajadas|dec:4:10|Horas trabajadas ese día"]),
        ("vacaciones", "Vacaciones tomadas", 120, [
            "id_vacacion|pk|Identificador de la solicitud",
            "id_empleado|fk:empleados|Empleado",
            "fecha_inicio|fec:2024:2025|Fecha de inicio",
            "dias|int:1:15|Días tomados"]),
    ]),
    "cine": ("train", [
        ("peliculas", "Cartelera de películas", 10, [
            "id_pelicula|pk|Identificador de la película",
            "titulo|nom:pelicula|Título",
            "genero|cat:accion/drama/comedia/terror/animacion|Género",
            "duracion_min|int:80:180|Duración en minutos",
            "anio|int:1995:2025|Año de estreno"]),
        ("salas", "Salas del cine", 6, [
            "id_sala|pk|Identificador de la sala",
            "nombre|nom:sala|Nombre de la sala",
            "capacidad|int:60:250|Número de butacas"]),
        ("funciones", "Funciones programadas", 150, [
            "id_funcion|pk|Identificador de la función",
            "id_pelicula|fk:peliculas|Película proyectada",
            "id_sala|fk:salas|Sala de proyección",
            "fecha|fec:2025:2025|Fecha de la función",
            "precio_boleto|dec:30:90|Precio por boleto"]),
        ("clientes", "Clientes frecuentes", 70, [
            "id_cliente|pk|Identificador del cliente",
            "nombre|nom:persona|Nombre del cliente",
            "correo|mail|Correo electrónico"]),
        ("boletos", "Boletos vendidos", 600, [
            "id_boleto|pk|Identificador de la venta",
            "id_funcion|fk:funciones|Función",
            "id_cliente|fk:clientes|Cliente comprador",
            "cantidad|int:1:6|Boletos comprados"]),
    ]),
    "logistica": ("train", [
        ("almacenes", "Almacenes de la empresa", 6, [
            "id_almacen|pk|Identificador del almacén",
            "nombre|nom:almacen|Nombre del almacén",
            "ciudad|nom:ciudad|Ciudad"]),
        ("conductores", "Conductores", 20, [
            "id_conductor|pk|Identificador del conductor",
            "nombre|nom:persona|Nombre del conductor",
            "anios_licencia|int:1:30|Años con licencia"]),
        ("productos", "Productos transportados", 25, [
            "id_producto|pk|Identificador del producto",
            "nombre|nom:producto|Nombre del producto",
            "peso_kg|dec:0.5:80|Peso por unidad en kilos"]),
        ("envios", "Envíos realizados", 250, [
            "id_envio|pk|Identificador del envío",
            "id_almacen|fk:almacenes|Almacén de salida",
            "id_conductor|fk:conductores|Conductor asignado",
            "fecha_envio|fec:2024:2025|Fecha de salida",
            "distancia_km|int:10:900|Distancia recorrida en km",
            "estado|cat:en_ruta/entregado/retrasado|Estado del envío"]),
        ("detalle_envio", "Productos de cada envío", 600, [
            "id_detalle|pk|Identificador de la línea",
            "id_envio|fk:envios|Envío",
            "id_producto|fk:productos|Producto enviado",
            "unidades|int:1:200|Unidades enviadas"]),
    ]),
    # ---- validación: dominios que NO aparecen en entrenamiento -------------
    "hotel": ("val", [
        ("hoteles", "Hoteles de la cadena", 6, [
            "id_hotel|pk|Identificador del hotel",
            "nombre|nom:hotel|Nombre del hotel",
            "ciudad|nom:ciudad|Ciudad donde se ubica",
            "estrellas|int:2:5|Categoría en estrellas"]),
        ("tipos_habitacion", "Tipos de habitación", 4, [
            "id_tipo|pk|Identificador del tipo",
            "nombre|cat:sencilla/doble/suite/familiar|Nombre del tipo",
            "capacidad|int:1:6|Personas que admite",
            "tarifa_noche|dec:300:2500|Tarifa por noche en quetzales"]),
        ("habitaciones", "Habitaciones físicas", 60, [
            "id_habitacion|pk|Identificador de la habitación",
            "id_hotel|fk:hoteles|Hotel al que pertenece",
            "id_tipo|fk:tipos_habitacion|Tipo de habitación",
            "numero|int:101:520|Número visible en la puerta",
            "piso|int:1:5|Piso donde se encuentra"]),
        ("huespedes", "Huéspedes", 70, [
            "id_huesped|pk|Identificador del huésped",
            "nombre|nom:persona|Nombre del huésped",
            "pais|nom:pais|País de procedencia",
            "correo|mail|Correo electrónico"]),
        ("reservaciones", "Reservaciones de habitaciones", 260, [
            "id_reservacion|pk|Identificador de la reservación",
            "id_huesped|fk:huespedes|Huésped que reserva",
            "id_habitacion|fk:habitaciones|Habitación reservada",
            "fecha_entrada|fec:2025:2025|Fecha de llegada",
            "noches|int:1:10|Noches de estadía",
            "canal|cat:web/telefono/agencia/mostrador|Canal por el que se reservó",
            "estado|cat:confirmada/cancelada/completada|Estado de la reservación"]),
        ("servicios", "Servicios adicionales", 8, [
            "id_servicio|pk|Identificador del servicio",
            "nombre|nom:servicio|Nombre del servicio",
            "precio|dec:20:400|Precio unitario"]),
        ("consumos", "Servicios consumidos durante la estadía", 400, [
            "id_consumo|pk|Identificador del consumo",
            "id_reservacion|fk:reservaciones|Reservación a la que se carga",
            "id_servicio|fk:servicios|Servicio consumido",
            "cantidad|int:1:5|Unidades consumidas",
            "fecha|fec:2025:2025|Fecha del consumo"]),
    ]),
    # nombres abreviados escritos a mano, como en muchas bases reales
    "futbol": ("val", [
        ("est", "Estadios", 5, [
            "id_est|pk|Identificador del estadio",
            "nom|nom:estadio|Nombre del estadio",
            "ciu|nom:ciudad|Ciudad donde se ubica",
            "cap|int:8000:45000|Capacidad de espectadores"]),
        ("equ", "Equipos de la liga", 8, [
            "id_equ|pk|Identificador del equipo",
            "nom|nom:equipo|Nombre del equipo",
            "id_est|fk:est|Estadio donde juega de local",
            "fund|int:1920:2005|Año de fundación"]),
        ("jug", "Jugadores", 120, [
            "id_jug|pk|Identificador del jugador",
            "nom|nom:persona|Nombre del jugador",
            "id_equ|fk:equ|Equipo al que pertenece",
            "pos|cat:POR/DEF/MED/DEL|Posición en el campo",
            "edad|int:17:38|Edad en años",
            "sal|dec:3000:60000|Salario mensual en quetzales"]),
        ("par", "Partidos jugados", 56, [
            "id_par|pk|Identificador del partido",
            "id_loc|fk:equ|Equipo local",
            "id_vis|fk:equ|Equipo visitante",
            "fec_par|fec:2025:2025|Fecha del partido",
            "jor|int:1:14|Número de jornada"]),
        ("gol", "Goles anotados", 150, [
            "id_gol|pk|Identificador del gol",
            "id_par|fk:par|Partido en que se anotó",
            "id_jug|fk:jug|Jugador que anotó",
            "min|int:1:90|Minuto del gol"]),
        ("tar", "Tarjetas mostradas", 120, [
            "id_tar|pk|Identificador de la tarjeta",
            "id_par|fk:par|Partido en que se mostró",
            "id_jug|fk:jug|Jugador sancionado",
            "tipo|cat:amarilla/roja|Tipo de tarjeta"]),
    ]),
}


# ------------------------------------------------------------------ modelo ---
ACENTOS = {"anios": "años", "anio": "año", "ubicacion": "ubicación", "duracion": "duración",
           "categoria": "categoría", "dias": "días", "transaccion": "transacción",
           "habitacion": "habitación", "reservacion": "reservación", "ordenes": "órdenes",
           "orden": "orden", "envio": "envío", "envios": "envíos", "telefono": "teléfono",
           "correo": "correo", "capacidad": "capacidad", "pais": "país", "medico": "médico",
           "medicos": "médicos", "titulo": "título", "genero": "género", "peliculas": "películas",
           "pelicula": "película", "numero": "número", "cuenta": "cuenta", "prestamo": "préstamo",
           "prestamos": "préstamos", "almacen": "almacén", "almacenes": "almacenes",
           "especialidad": "especialidad", "inscripcion": "inscripción",
           "inscripciones": "inscripciones", "catedratico": "catedrático",
           "estadia": "estadía", "tarifa": "tarifa", "psicologia": "psicología"}
ETIQUETAS_TABLA = {"detalle_pedido": "detalle de pedido", "detalle_orden": "detalle de orden",
                   "detalle_envio": "detalle de envío", "tipos_habitacion": "tipos de habitación"}


def bonito(nombre):
    return " ".join(ACENTOS.get(p, p) for p in nombre.split("_"))


@dataclass
class Col:
    orig: str           # nombre completo (sirve para etiquetas en español)
    db: str             # nombre en la base (según variante)
    tipo: str
    arg: list
    comentario: str

    @property
    def etiqueta(self):
        return bonito(self.orig)


@dataclass
class Tabla:
    orig: str
    db: str
    comentario: str
    filas: int
    cols: list = field(default_factory=list)

    @property
    def etiqueta(self):
        return ETIQUETAS_TABLA.get(self.orig, bonito(self.orig))

    @property
    def pk(self):
        return self.cols[0]

    def de_tipo(self, *tipos):
        return [c for c in self.cols if c.tipo in tipos]

    @property
    def fks(self):
        return [(c, c.arg[0]) for c in self.cols if c.tipo == "fk"]

    @property
    def nums(self):
        return self.de_tipo("int", "dec")

    @property
    def cats(self):
        return self.de_tipo("cat")

    @property
    def noms(self):
        return self.de_tipo("nom")

    @property
    def fechas(self):
        return self.de_tipo("fec")


def _abreviar(nombre, usados):
    toks = [t for t in nombre.split("_") if t not in ("de", "del", "la", "el")]
    for largo in (3, 4, 5, 6):
        partes = [t if len(t) <= 3 else t[:largo if len(t) > largo + 1 else len(t)] for t in toks]
        cand = "_".join(partes)
        if cand not in RESERVADAS and cand not in usados:
            return cand
    cand = "_".join(toks)
    i = 2
    while cand in usados or cand in RESERVADAS:
        cand = f"{cand}{i}"
        i += 1
    return cand


class Esquema:
    def __init__(self, nombre, variante="full"):
        self.nombre, self.variante = nombre, variante
        self.rol, spec = ESQUEMAS[nombre]
        self.tablas = {}
        usados_t = set()
        for tn, tcom, filas, cols in spec:
            tdb = _abreviar(tn, usados_t) if variante == "abr" else tn
            usados_t.add(tdb)
            tab = Tabla(tn, tdb, tcom, filas)
            usados_c = set()
            for linea in cols:
                cn, kind, com = linea.split("|")
                partes = kind.split(":")
                cdb = _abreviar(cn, usados_c) if variante == "abr" else cn
                usados_c.add(cdb)
                tab.cols.append(Col(cn, cdb, partes[0], partes[1:], com))
            self.tablas[tn] = tab

    @property
    def id(self):
        return f"{self.nombre}_{self.variante}"

    @property
    def base(self):
        return f"p3_{self.id}"

    def orden_creacion(self):
        hechos, orden = set(), []
        pend = list(self.tablas)
        while pend:
            for n in list(pend):
                deps = {a for _, a in self.tablas[n].fks if a != n}
                if deps <= hechos:
                    orden.append(n)
                    hechos.add(n)
                    pend.remove(n)
        return orden

    def ddl(self):
        sentencias = []
        for n in self.orden_creacion():
            t = self.tablas[n]
            lineas = []
            for c in t.cols:
                com = c.comentario.replace("'", "''")
                if c.tipo == "pk":
                    tipo_sql = "INT NOT NULL AUTO_INCREMENT"
                elif c.tipo == "fk":
                    tipo_sql = "INT NOT NULL"
                elif c.tipo == "nom":
                    tipo_sql = "VARCHAR(100) NOT NULL"
                elif c.tipo == "mail":
                    tipo_sql = "VARCHAR(100) NOT NULL"
                elif c.tipo == "cat":
                    tipo_sql = "VARCHAR(30) NOT NULL"
                elif c.tipo == "int":
                    tipo_sql = "INT NOT NULL"
                elif c.tipo == "dec":
                    tipo_sql = "DECIMAL(10,2) NOT NULL"
                elif c.tipo == "fec":
                    tipo_sql = "DATE NOT NULL"
                lineas.append(f"  `{c.db}` {tipo_sql} COMMENT '{com}'")
            lineas.append(f"  PRIMARY KEY (`{t.pk.db}`)")
            for c, padre in t.fks:
                p = self.tablas[padre]
                lineas.append(f"  CONSTRAINT `fk_{t.db}_{c.db}` FOREIGN KEY (`{c.db}`) "
                              f"REFERENCES `{p.db}` (`{p.pk.db}`)")
            tcom = t.comentario.replace("'", "''")
            sentencias.append(f"CREATE TABLE `{t.db}` (\n" + ",\n".join(lineas) +
                              f"\n) ENGINE=InnoDB COMMENT='{tcom}'")
        return sentencias

    def filas_de(self, tabla, rng, ids):
        """Genera las filas de una tabla; ids = {tabla_orig: [ids existentes]}."""
        t = self.tablas[tabla]
        filas = []
        for i in range(1, t.filas + 1):
            fila, usados_padre = [], {}
            for c in t.cols:
                if c.tipo == "pk":
                    v = i
                elif c.tipo == "fk":
                    usables = ids[c.arg[0]]
                    # ~15 % de los padres quedan sin hijos (sirve para 'sin registros')
                    opciones = usables[: max(1, int(len(usables) * 0.85))]
                    v = rng.choice(opciones)
                    previos = usados_padre.setdefault(c.arg[0], [])
                    for _ in range(10):
                        if v not in previos:
                            break
                        v = rng.choice(opciones)
                    previos.append(v)
                elif c.tipo == "nom":
                    pool = POOLS.get(c.arg[0], POOLS["generico"])
                    v = pool[(i - 1) % len(pool)] if t.filas <= len(pool) else rng.choice(pool)
                elif c.tipo == "mail":
                    v = f"usuario{i}@correo.com"
                elif c.tipo == "cat":
                    v = rng.choice(c.arg[0].split("/"))
                elif c.tipo == "int":
                    v = rng.randint(int(c.arg[0]), int(c.arg[1]))
                elif c.tipo == "dec":
                    v = round(rng.uniform(float(c.arg[0]), float(c.arg[1])), 2)
                elif c.tipo == "fec":
                    y = rng.randint(int(c.arg[0]), int(c.arg[1]))
                    v = f"{y:04d}-{rng.randint(1, 12):02d}-{rng.randint(1, 28):02d}"
                fila.append(v)
            filas.append(fila)
        ids[tabla] = [f[0] for f in filas]
        return filas


def todos(rol=None, variantes=("full", "abr")):
    """Los esquemas de validación solo existen en la variante 'full'
    (futbol ya trae nombres abreviados escritos a mano)."""
    for nombre, (r, _) in ESQUEMAS.items():
        if rol and r != rol:
            continue
        for v in (variantes if r == "train" else ("full",)):
            yield Esquema(nombre, v)
