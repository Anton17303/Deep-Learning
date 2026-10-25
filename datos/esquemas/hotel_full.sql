CREATE TABLE `hoteles` (
  `id_hotel` int NOT NULL AUTO_INCREMENT COMMENT 'Identificador del hotel',
  `nombre` varchar(100) NOT NULL COMMENT 'Nombre del hotel',
  `ciudad` varchar(100) NOT NULL COMMENT 'Ciudad donde se ubica',
  `estrellas` int NOT NULL COMMENT 'Categoría en estrellas',
  PRIMARY KEY (`id_hotel`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Hoteles de la cadena';

CREATE TABLE `tipos_habitacion` (
  `id_tipo` int NOT NULL AUTO_INCREMENT COMMENT 'Identificador del tipo',
  `nombre` varchar(30) NOT NULL COMMENT 'Nombre del tipo',
  `capacidad` int NOT NULL COMMENT 'Personas que admite',
  `tarifa_noche` decimal(10,2) NOT NULL COMMENT 'Tarifa por noche en quetzales',
  PRIMARY KEY (`id_tipo`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Tipos de habitación';

CREATE TABLE `habitaciones` (
  `id_habitacion` int NOT NULL AUTO_INCREMENT COMMENT 'Identificador de la habitación',
  `id_hotel` int NOT NULL COMMENT 'Hotel al que pertenece',
  `id_tipo` int NOT NULL COMMENT 'Tipo de habitación',
  `numero` int NOT NULL COMMENT 'Número visible en la puerta',
  `piso` int NOT NULL COMMENT 'Piso donde se encuentra',
  PRIMARY KEY (`id_habitacion`),
  KEY `fk_habitaciones_id_hotel` (`id_hotel`),
  KEY `fk_habitaciones_id_tipo` (`id_tipo`),
  CONSTRAINT `fk_habitaciones_id_hotel` FOREIGN KEY (`id_hotel`) REFERENCES `hoteles` (`id_hotel`),
  CONSTRAINT `fk_habitaciones_id_tipo` FOREIGN KEY (`id_tipo`) REFERENCES `tipos_habitacion` (`id_tipo`)
) ENGINE=InnoDB AUTO_INCREMENT=61 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Habitaciones físicas';

CREATE TABLE `huespedes` (
  `id_huesped` int NOT NULL AUTO_INCREMENT COMMENT 'Identificador del huésped',
  `nombre` varchar(100) NOT NULL COMMENT 'Nombre del huésped',
  `pais` varchar(100) NOT NULL COMMENT 'País de procedencia',
  `correo` varchar(100) NOT NULL COMMENT 'Correo electrónico',
  PRIMARY KEY (`id_huesped`)
) ENGINE=InnoDB AUTO_INCREMENT=71 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Huéspedes';

CREATE TABLE `reservaciones` (
  `id_reservacion` int NOT NULL AUTO_INCREMENT COMMENT 'Identificador de la reservación',
  `id_huesped` int NOT NULL COMMENT 'Huésped que reserva',
  `id_habitacion` int NOT NULL COMMENT 'Habitación reservada',
  `fecha_entrada` date NOT NULL COMMENT 'Fecha de llegada',
  `noches` int NOT NULL COMMENT 'Noches de estadía',
  `canal` varchar(30) NOT NULL COMMENT 'Canal por el que se reservó',
  `estado` varchar(30) NOT NULL COMMENT 'Estado de la reservación',
  PRIMARY KEY (`id_reservacion`),
  KEY `fk_reservaciones_id_huesped` (`id_huesped`),
  KEY `fk_reservaciones_id_habitacion` (`id_habitacion`),
  CONSTRAINT `fk_reservaciones_id_habitacion` FOREIGN KEY (`id_habitacion`) REFERENCES `habitaciones` (`id_habitacion`),
  CONSTRAINT `fk_reservaciones_id_huesped` FOREIGN KEY (`id_huesped`) REFERENCES `huespedes` (`id_huesped`)
) ENGINE=InnoDB AUTO_INCREMENT=261 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Reservaciones de habitaciones';

CREATE TABLE `servicios` (
  `id_servicio` int NOT NULL AUTO_INCREMENT COMMENT 'Identificador del servicio',
  `nombre` varchar(100) NOT NULL COMMENT 'Nombre del servicio',
  `precio` decimal(10,2) NOT NULL COMMENT 'Precio unitario',
  PRIMARY KEY (`id_servicio`)
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Servicios adicionales';

CREATE TABLE `consumos` (
  `id_consumo` int NOT NULL AUTO_INCREMENT COMMENT 'Identificador del consumo',
  `id_reservacion` int NOT NULL COMMENT 'Reservación a la que se carga',
  `id_servicio` int NOT NULL COMMENT 'Servicio consumido',
  `cantidad` int NOT NULL COMMENT 'Unidades consumidas',
  `fecha` date NOT NULL COMMENT 'Fecha del consumo',
  PRIMARY KEY (`id_consumo`),
  KEY `fk_consumos_id_reservacion` (`id_reservacion`),
  KEY `fk_consumos_id_servicio` (`id_servicio`),
  CONSTRAINT `fk_consumos_id_reservacion` FOREIGN KEY (`id_reservacion`) REFERENCES `reservaciones` (`id_reservacion`),
  CONSTRAINT `fk_consumos_id_servicio` FOREIGN KEY (`id_servicio`) REFERENCES `servicios` (`id_servicio`)
) ENGINE=InnoDB AUTO_INCREMENT=401 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Servicios consumidos durante la estadía';