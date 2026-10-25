CREATE TABLE `alm` (
  `id_alm` int NOT NULL AUTO_INCREMENT COMMENT 'Identificador del almacén',
  `nom` varchar(100) NOT NULL COMMENT 'Nombre del almacén',
  `ciu` varchar(100) NOT NULL COMMENT 'Ciudad',
  PRIMARY KEY (`id_alm`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Almacenes de la empresa';

CREATE TABLE `con` (
  `id_con` int NOT NULL AUTO_INCREMENT COMMENT 'Identificador del conductor',
  `nom` varchar(100) NOT NULL COMMENT 'Nombre del conductor',
  `ani_lic` int NOT NULL COMMENT 'Años con licencia',
  PRIMARY KEY (`id_con`)
) ENGINE=InnoDB AUTO_INCREMENT=21 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Conductores';

CREATE TABLE `pro` (
  `id_pro` int NOT NULL AUTO_INCREMENT COMMENT 'Identificador del producto',
  `nom` varchar(100) NOT NULL COMMENT 'Nombre del producto',
  `peso_kg` decimal(10,2) NOT NULL COMMENT 'Peso por unidad en kilos',
  PRIMARY KEY (`id_pro`)
) ENGINE=InnoDB AUTO_INCREMENT=26 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Productos transportados';

CREATE TABLE `env` (
  `id_env` int NOT NULL AUTO_INCREMENT COMMENT 'Identificador del envío',
  `id_alm` int NOT NULL COMMENT 'Almacén de salida',
  `id_con` int NOT NULL COMMENT 'Conductor asignado',
  `fec_env` date NOT NULL COMMENT 'Fecha de salida',
  `dis_km` int NOT NULL COMMENT 'Distancia recorrida en km',
  `est` varchar(30) NOT NULL COMMENT 'Estado del envío',
  PRIMARY KEY (`id_env`),
  KEY `fk_env_id_alm` (`id_alm`),
  KEY `fk_env_id_con` (`id_con`),
  CONSTRAINT `fk_env_id_alm` FOREIGN KEY (`id_alm`) REFERENCES `alm` (`id_alm`),
  CONSTRAINT `fk_env_id_con` FOREIGN KEY (`id_con`) REFERENCES `con` (`id_con`)
) ENGINE=InnoDB AUTO_INCREMENT=251 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Envíos realizados';

CREATE TABLE `det_env` (
  `id_det` int NOT NULL AUTO_INCREMENT COMMENT 'Identificador de la línea',
  `id_env` int NOT NULL COMMENT 'Envío',
  `id_pro` int NOT NULL COMMENT 'Producto enviado',
  `uni` int NOT NULL COMMENT 'Unidades enviadas',
  PRIMARY KEY (`id_det`),
  KEY `fk_det_env_id_env` (`id_env`),
  KEY `fk_det_env_id_pro` (`id_pro`),
  CONSTRAINT `fk_det_env_id_env` FOREIGN KEY (`id_env`) REFERENCES `env` (`id_env`),
  CONSTRAINT `fk_det_env_id_pro` FOREIGN KEY (`id_pro`) REFERENCES `pro` (`id_pro`)
) ENGINE=InnoDB AUTO_INCREMENT=601 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Productos de cada envío';