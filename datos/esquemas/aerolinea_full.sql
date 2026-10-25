CREATE TABLE `aerolineas` (
  `id_aerolinea` int NOT NULL AUTO_INCREMENT COMMENT 'Identificador de la aerolínea',
  `nombre` varchar(100) NOT NULL COMMENT 'Nombre de la aerolínea',
  `pais` varchar(100) NOT NULL COMMENT 'País sede',
  PRIMARY KEY (`id_aerolinea`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Aerolíneas que operan';

CREATE TABLE `aeropuertos` (
  `id_aeropuerto` int NOT NULL AUTO_INCREMENT COMMENT 'Identificador del aeropuerto',
  `nombre` varchar(100) NOT NULL COMMENT 'Nombre del aeropuerto',
  `ciudad` varchar(100) NOT NULL COMMENT 'Ciudad donde se ubica',
  PRIMARY KEY (`id_aeropuerto`)
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Aeropuertos';

CREATE TABLE `vuelos` (
  `id_vuelo` int NOT NULL AUTO_INCREMENT COMMENT 'Identificador del vuelo',
  `id_aerolinea` int NOT NULL COMMENT 'Aerolínea que opera',
  `id_origen` int NOT NULL COMMENT 'Aeropuerto de origen',
  `id_destino` int NOT NULL COMMENT 'Aeropuerto de destino',
  `fecha_salida` date NOT NULL COMMENT 'Fecha de salida',
  `duracion_min` int NOT NULL COMMENT 'Duración en minutos',
  `precio_base` decimal(10,2) NOT NULL COMMENT 'Precio base del boleto',
  PRIMARY KEY (`id_vuelo`),
  KEY `fk_vuelos_id_aerolinea` (`id_aerolinea`),
  KEY `fk_vuelos_id_origen` (`id_origen`),
  KEY `fk_vuelos_id_destino` (`id_destino`),
  CONSTRAINT `fk_vuelos_id_aerolinea` FOREIGN KEY (`id_aerolinea`) REFERENCES `aerolineas` (`id_aerolinea`),
  CONSTRAINT `fk_vuelos_id_destino` FOREIGN KEY (`id_destino`) REFERENCES `aeropuertos` (`id_aeropuerto`),
  CONSTRAINT `fk_vuelos_id_origen` FOREIGN KEY (`id_origen`) REFERENCES `aeropuertos` (`id_aeropuerto`)
) ENGINE=InnoDB AUTO_INCREMENT=121 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Vuelos programados';

CREATE TABLE `pasajeros` (
  `id_pasajero` int NOT NULL AUTO_INCREMENT COMMENT 'Identificador del pasajero',
  `nombre` varchar(100) NOT NULL COMMENT 'Nombre del pasajero',
  `pais` varchar(100) NOT NULL COMMENT 'País de residencia',
  PRIMARY KEY (`id_pasajero`)
) ENGINE=InnoDB AUTO_INCREMENT=101 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Pasajeros';

CREATE TABLE `reservas` (
  `id_reserva` int NOT NULL AUTO_INCREMENT COMMENT 'Identificador de la reserva',
  `id_vuelo` int NOT NULL COMMENT 'Vuelo reservado',
  `id_pasajero` int NOT NULL COMMENT 'Pasajero',
  `clase` varchar(30) NOT NULL COMMENT 'Clase de servicio',
  `equipaje_kg` int NOT NULL COMMENT 'Kilos de equipaje',
  PRIMARY KEY (`id_reserva`),
  KEY `fk_reservas_id_vuelo` (`id_vuelo`),
  KEY `fk_reservas_id_pasajero` (`id_pasajero`),
  CONSTRAINT `fk_reservas_id_pasajero` FOREIGN KEY (`id_pasajero`) REFERENCES `pasajeros` (`id_pasajero`),
  CONSTRAINT `fk_reservas_id_vuelo` FOREIGN KEY (`id_vuelo`) REFERENCES `vuelos` (`id_vuelo`)
) ENGINE=InnoDB AUTO_INCREMENT=451 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Reservas de asientos';