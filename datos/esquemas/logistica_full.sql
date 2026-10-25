CREATE TABLE `almacenes` (
  `id_almacen` int NOT NULL AUTO_INCREMENT COMMENT 'Identificador del almacén',
  `nombre` varchar(100) NOT NULL COMMENT 'Nombre del almacén',
  `ciudad` varchar(100) NOT NULL COMMENT 'Ciudad',
  PRIMARY KEY (`id_almacen`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Almacenes de la empresa';

CREATE TABLE `conductores` (
  `id_conductor` int NOT NULL AUTO_INCREMENT COMMENT 'Identificador del conductor',
  `nombre` varchar(100) NOT NULL COMMENT 'Nombre del conductor',
  `anios_licencia` int NOT NULL COMMENT 'Años con licencia',
  PRIMARY KEY (`id_conductor`)
) ENGINE=InnoDB AUTO_INCREMENT=21 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Conductores';

CREATE TABLE `productos` (
  `id_producto` int NOT NULL AUTO_INCREMENT COMMENT 'Identificador del producto',
  `nombre` varchar(100) NOT NULL COMMENT 'Nombre del producto',
  `peso_kg` decimal(10,2) NOT NULL COMMENT 'Peso por unidad en kilos',
  PRIMARY KEY (`id_producto`)
) ENGINE=InnoDB AUTO_INCREMENT=26 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Productos transportados';

CREATE TABLE `envios` (
  `id_envio` int NOT NULL AUTO_INCREMENT COMMENT 'Identificador del envío',
  `id_almacen` int NOT NULL COMMENT 'Almacén de salida',
  `id_conductor` int NOT NULL COMMENT 'Conductor asignado',
  `fecha_envio` date NOT NULL COMMENT 'Fecha de salida',
  `distancia_km` int NOT NULL COMMENT 'Distancia recorrida en km',
  `estado` varchar(30) NOT NULL COMMENT 'Estado del envío',
  PRIMARY KEY (`id_envio`),
  KEY `fk_envios_id_almacen` (`id_almacen`),
  KEY `fk_envios_id_conductor` (`id_conductor`),
  CONSTRAINT `fk_envios_id_almacen` FOREIGN KEY (`id_almacen`) REFERENCES `almacenes` (`id_almacen`),
  CONSTRAINT `fk_envios_id_conductor` FOREIGN KEY (`id_conductor`) REFERENCES `conductores` (`id_conductor`)
) ENGINE=InnoDB AUTO_INCREMENT=251 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Envíos realizados';

CREATE TABLE `detalle_envio` (
  `id_detalle` int NOT NULL AUTO_INCREMENT COMMENT 'Identificador de la línea',
  `id_envio` int NOT NULL COMMENT 'Envío',
  `id_producto` int NOT NULL COMMENT 'Producto enviado',
  `unidades` int NOT NULL COMMENT 'Unidades enviadas',
  PRIMARY KEY (`id_detalle`),
  KEY `fk_detalle_envio_id_envio` (`id_envio`),
  KEY `fk_detalle_envio_id_producto` (`id_producto`),
  CONSTRAINT `fk_detalle_envio_id_envio` FOREIGN KEY (`id_envio`) REFERENCES `envios` (`id_envio`),
  CONSTRAINT `fk_detalle_envio_id_producto` FOREIGN KEY (`id_producto`) REFERENCES `productos` (`id_producto`)
) ENGINE=InnoDB AUTO_INCREMENT=601 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Productos de cada envío';