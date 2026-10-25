CREATE TABLE `mes` (
  `id_mes` int NOT NULL AUTO_INCREMENT COMMENT 'Identificador del mesero',
  `nom` varchar(100) NOT NULL COMMENT 'Nombre del mesero',
  `fec_con` date NOT NULL COMMENT 'Fecha de contratación',
  PRIMARY KEY (`id_mes`)
) ENGINE=InnoDB AUTO_INCREMENT=13 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Personal de servicio';

CREATE TABLE `mesas` (
  `id_mesa` int NOT NULL AUTO_INCREMENT COMMENT 'Identificador de la mesa',
  `cap` int NOT NULL COMMENT 'Personas que caben',
  `zona` varchar(30) NOT NULL COMMENT 'Zona del local',
  PRIMARY KEY (`id_mesa`)
) ENGINE=InnoDB AUTO_INCREMENT=16 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Mesas del restaurante';

CREATE TABLE `pla` (
  `id_pla` int NOT NULL AUTO_INCREMENT COMMENT 'Identificador del platillo',
  `nom` varchar(100) NOT NULL COMMENT 'Nombre del platillo',
  `cat` varchar(30) NOT NULL COMMENT 'Categoría del menú',
  `pre` decimal(10,2) NOT NULL COMMENT 'Precio en quetzales',
  PRIMARY KEY (`id_pla`)
) ENGINE=InnoDB AUTO_INCREMENT=16 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Menú';

CREATE TABLE `ord` (
  `id_ord` int NOT NULL AUTO_INCREMENT COMMENT 'Identificador de la orden',
  `id_mesa` int NOT NULL COMMENT 'Mesa atendida',
  `id_mes` int NOT NULL COMMENT 'Mesero responsable',
  `fecha` date NOT NULL COMMENT 'Fecha de la orden',
  `pro` decimal(10,2) NOT NULL COMMENT 'Propina recibida',
  PRIMARY KEY (`id_ord`),
  KEY `fk_ord_id_mesa` (`id_mesa`),
  KEY `fk_ord_id_mes` (`id_mes`),
  CONSTRAINT `fk_ord_id_mes` FOREIGN KEY (`id_mes`) REFERENCES `mes` (`id_mes`),
  CONSTRAINT `fk_ord_id_mesa` FOREIGN KEY (`id_mesa`) REFERENCES `mesas` (`id_mesa`)
) ENGINE=InnoDB AUTO_INCREMENT=301 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Órdenes atendidas';

CREATE TABLE `det_ord` (
  `id_det` int NOT NULL AUTO_INCREMENT COMMENT 'Identificador de la línea',
  `id_ord` int NOT NULL COMMENT 'Orden',
  `id_pla` int NOT NULL COMMENT 'Platillo pedido',
  `can` int NOT NULL COMMENT 'Cantidad pedida',
  PRIMARY KEY (`id_det`),
  KEY `fk_det_ord_id_ord` (`id_ord`),
  KEY `fk_det_ord_id_pla` (`id_pla`),
  CONSTRAINT `fk_det_ord_id_ord` FOREIGN KEY (`id_ord`) REFERENCES `ord` (`id_ord`),
  CONSTRAINT `fk_det_ord_id_pla` FOREIGN KEY (`id_pla`) REFERENCES `pla` (`id_pla`)
) ENGINE=InnoDB AUTO_INCREMENT=801 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Platillos de cada orden';