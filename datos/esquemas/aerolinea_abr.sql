CREATE TABLE `aer` (
  `id_aer` int NOT NULL AUTO_INCREMENT COMMENT 'Identificador de la aerolínea',
  `nom` varchar(100) NOT NULL COMMENT 'Nombre de la aerolínea',
  `pais` varchar(100) NOT NULL COMMENT 'País sede',
  PRIMARY KEY (`id_aer`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Aerolíneas que operan';

CREATE TABLE `aero` (
  `id_aer` int NOT NULL AUTO_INCREMENT COMMENT 'Identificador del aeropuerto',
  `nom` varchar(100) NOT NULL COMMENT 'Nombre del aeropuerto',
  `ciu` varchar(100) NOT NULL COMMENT 'Ciudad donde se ubica',
  PRIMARY KEY (`id_aer`)
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Aeropuertos';

CREATE TABLE `vue` (
  `id_vue` int NOT NULL AUTO_INCREMENT COMMENT 'Identificador del vuelo',
  `id_aer` int NOT NULL COMMENT 'Aerolínea que opera',
  `id_ori` int NOT NULL COMMENT 'Aeropuerto de origen',
  `id_des` int NOT NULL COMMENT 'Aeropuerto de destino',
  `fec_sal` date NOT NULL COMMENT 'Fecha de salida',
  `dur_min` int NOT NULL COMMENT 'Duración en minutos',
  `pre_base` decimal(10,2) NOT NULL COMMENT 'Precio base del boleto',
  PRIMARY KEY (`id_vue`),
  KEY `fk_vue_id_aer` (`id_aer`),
  KEY `fk_vue_id_ori` (`id_ori`),
  KEY `fk_vue_id_des` (`id_des`),
  CONSTRAINT `fk_vue_id_aer` FOREIGN KEY (`id_aer`) REFERENCES `aer` (`id_aer`),
  CONSTRAINT `fk_vue_id_des` FOREIGN KEY (`id_des`) REFERENCES `aero` (`id_aer`),
  CONSTRAINT `fk_vue_id_ori` FOREIGN KEY (`id_ori`) REFERENCES `aero` (`id_aer`)
) ENGINE=InnoDB AUTO_INCREMENT=121 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Vuelos programados';

CREATE TABLE `pas` (
  `id_pas` int NOT NULL AUTO_INCREMENT COMMENT 'Identificador del pasajero',
  `nom` varchar(100) NOT NULL COMMENT 'Nombre del pasajero',
  `pais` varchar(100) NOT NULL COMMENT 'País de residencia',
  PRIMARY KEY (`id_pas`)
) ENGINE=InnoDB AUTO_INCREMENT=101 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Pasajeros';

CREATE TABLE `res` (
  `id_res` int NOT NULL AUTO_INCREMENT COMMENT 'Identificador de la reserva',
  `id_vue` int NOT NULL COMMENT 'Vuelo reservado',
  `id_pas` int NOT NULL COMMENT 'Pasajero',
  `cla` varchar(30) NOT NULL COMMENT 'Clase de servicio',
  `equ_kg` int NOT NULL COMMENT 'Kilos de equipaje',
  PRIMARY KEY (`id_res`),
  KEY `fk_res_id_vue` (`id_vue`),
  KEY `fk_res_id_pas` (`id_pas`),
  CONSTRAINT `fk_res_id_pas` FOREIGN KEY (`id_pas`) REFERENCES `pas` (`id_pas`),
  CONSTRAINT `fk_res_id_vue` FOREIGN KEY (`id_vue`) REFERENCES `vue` (`id_vue`)
) ENGINE=InnoDB AUTO_INCREMENT=451 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Reservas de asientos';