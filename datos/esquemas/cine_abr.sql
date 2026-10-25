CREATE TABLE `pel` (
  `id_pel` int NOT NULL AUTO_INCREMENT COMMENT 'Identificador de la película',
  `tit` varchar(100) NOT NULL COMMENT 'Título',
  `gen` varchar(30) NOT NULL COMMENT 'Género',
  `dur_min` int NOT NULL COMMENT 'Duración en minutos',
  `anio` int NOT NULL COMMENT 'Año de estreno',
  PRIMARY KEY (`id_pel`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Cartelera de películas';

CREATE TABLE `sal` (
  `id_sala` int NOT NULL AUTO_INCREMENT COMMENT 'Identificador de la sala',
  `nom` varchar(100) NOT NULL COMMENT 'Nombre de la sala',
  `cap` int NOT NULL COMMENT 'Número de butacas',
  PRIMARY KEY (`id_sala`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Salas del cine';

CREATE TABLE `fun` (
  `id_fun` int NOT NULL AUTO_INCREMENT COMMENT 'Identificador de la función',
  `id_pel` int NOT NULL COMMENT 'Película proyectada',
  `id_sala` int NOT NULL COMMENT 'Sala de proyección',
  `fecha` date NOT NULL COMMENT 'Fecha de la función',
  `pre_bol` decimal(10,2) NOT NULL COMMENT 'Precio por boleto',
  PRIMARY KEY (`id_fun`),
  KEY `fk_fun_id_pel` (`id_pel`),
  KEY `fk_fun_id_sala` (`id_sala`),
  CONSTRAINT `fk_fun_id_pel` FOREIGN KEY (`id_pel`) REFERENCES `pel` (`id_pel`),
  CONSTRAINT `fk_fun_id_sala` FOREIGN KEY (`id_sala`) REFERENCES `sal` (`id_sala`)
) ENGINE=InnoDB AUTO_INCREMENT=151 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Funciones programadas';

CREATE TABLE `cli` (
  `id_cli` int NOT NULL AUTO_INCREMENT COMMENT 'Identificador del cliente',
  `nom` varchar(100) NOT NULL COMMENT 'Nombre del cliente',
  `cor` varchar(100) NOT NULL COMMENT 'Correo electrónico',
  PRIMARY KEY (`id_cli`)
) ENGINE=InnoDB AUTO_INCREMENT=71 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Clientes frecuentes';

CREATE TABLE `bol` (
  `id_bol` int NOT NULL AUTO_INCREMENT COMMENT 'Identificador de la venta',
  `id_fun` int NOT NULL COMMENT 'Función',
  `id_cli` int NOT NULL COMMENT 'Cliente comprador',
  `can` int NOT NULL COMMENT 'Boletos comprados',
  PRIMARY KEY (`id_bol`),
  KEY `fk_bol_id_fun` (`id_fun`),
  KEY `fk_bol_id_cli` (`id_cli`),
  CONSTRAINT `fk_bol_id_cli` FOREIGN KEY (`id_cli`) REFERENCES `cli` (`id_cli`),
  CONSTRAINT `fk_bol_id_fun` FOREIGN KEY (`id_fun`) REFERENCES `fun` (`id_fun`)
) ENGINE=InnoDB AUTO_INCREMENT=601 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Boletos vendidos';