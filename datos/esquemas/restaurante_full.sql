CREATE TABLE `meseros` (
  `id_mesero` int NOT NULL AUTO_INCREMENT COMMENT 'Identificador del mesero',
  `nombre` varchar(100) NOT NULL COMMENT 'Nombre del mesero',
  `fecha_contratacion` date NOT NULL COMMENT 'Fecha de contratación',
  PRIMARY KEY (`id_mesero`)
) ENGINE=InnoDB AUTO_INCREMENT=13 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Personal de servicio';

CREATE TABLE `mesas` (
  `id_mesa` int NOT NULL AUTO_INCREMENT COMMENT 'Identificador de la mesa',
  `capacidad` int NOT NULL COMMENT 'Personas que caben',
  `zona` varchar(30) NOT NULL COMMENT 'Zona del local',
  PRIMARY KEY (`id_mesa`)
) ENGINE=InnoDB AUTO_INCREMENT=16 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Mesas del restaurante';

CREATE TABLE `platillos` (
  `id_platillo` int NOT NULL AUTO_INCREMENT COMMENT 'Identificador del platillo',
  `nombre` varchar(100) NOT NULL COMMENT 'Nombre del platillo',
  `categoria` varchar(30) NOT NULL COMMENT 'Categoría del menú',
  `precio` decimal(10,2) NOT NULL COMMENT 'Precio en quetzales',
  PRIMARY KEY (`id_platillo`)
) ENGINE=InnoDB AUTO_INCREMENT=16 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Menú';

CREATE TABLE `ordenes` (
  `id_orden` int NOT NULL AUTO_INCREMENT COMMENT 'Identificador de la orden',
  `id_mesa` int NOT NULL COMMENT 'Mesa atendida',
  `id_mesero` int NOT NULL COMMENT 'Mesero responsable',
  `fecha` date NOT NULL COMMENT 'Fecha de la orden',
  `propina` decimal(10,2) NOT NULL COMMENT 'Propina recibida',
  PRIMARY KEY (`id_orden`),
  KEY `fk_ordenes_id_mesa` (`id_mesa`),
  KEY `fk_ordenes_id_mesero` (`id_mesero`),
  CONSTRAINT `fk_ordenes_id_mesa` FOREIGN KEY (`id_mesa`) REFERENCES `mesas` (`id_mesa`),
  CONSTRAINT `fk_ordenes_id_mesero` FOREIGN KEY (`id_mesero`) REFERENCES `meseros` (`id_mesero`)
) ENGINE=InnoDB AUTO_INCREMENT=301 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Órdenes atendidas';

CREATE TABLE `detalle_orden` (
  `id_detalle` int NOT NULL AUTO_INCREMENT COMMENT 'Identificador de la línea',
  `id_orden` int NOT NULL COMMENT 'Orden',
  `id_platillo` int NOT NULL COMMENT 'Platillo pedido',
  `cantidad` int NOT NULL COMMENT 'Cantidad pedida',
  PRIMARY KEY (`id_detalle`),
  KEY `fk_detalle_orden_id_orden` (`id_orden`),
  KEY `fk_detalle_orden_id_platillo` (`id_platillo`),
  CONSTRAINT `fk_detalle_orden_id_orden` FOREIGN KEY (`id_orden`) REFERENCES `ordenes` (`id_orden`),
  CONSTRAINT `fk_detalle_orden_id_platillo` FOREIGN KEY (`id_platillo`) REFERENCES `platillos` (`id_platillo`)
) ENGINE=InnoDB AUTO_INCREMENT=801 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Platillos de cada orden';