CREATE TABLE `cat` (
  `id_cat` int NOT NULL AUTO_INCREMENT COMMENT 'Identificador de la categoría',
  `nom` varchar(100) NOT NULL COMMENT 'Nombre de la categoría',
  PRIMARY KEY (`id_cat`)
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Categorías de productos';

CREATE TABLE `cli` (
  `id_cli` int NOT NULL AUTO_INCREMENT COMMENT 'Identificador del cliente',
  `nom` varchar(100) NOT NULL COMMENT 'Nombre completo del cliente',
  `cor` varchar(100) NOT NULL COMMENT 'Correo electrónico',
  `ciu` varchar(100) NOT NULL COMMENT 'Ciudad de residencia',
  `fec_reg` date NOT NULL COMMENT 'Fecha en que se registró',
  PRIMARY KEY (`id_cli`)
) ENGINE=InnoDB AUTO_INCREMENT=61 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Clientes registrados en la tienda';

CREATE TABLE `pro` (
  `id_pro` int NOT NULL AUTO_INCREMENT COMMENT 'Identificador del producto',
  `nom` varchar(100) NOT NULL COMMENT 'Nombre del producto',
  `id_cat` int NOT NULL COMMENT 'Categoría del producto',
  `pre` decimal(10,2) NOT NULL COMMENT 'Precio de venta en quetzales',
  `sto` int NOT NULL COMMENT 'Unidades disponibles en inventario',
  PRIMARY KEY (`id_pro`),
  KEY `fk_pro_id_cat` (`id_cat`),
  CONSTRAINT `fk_pro_id_cat` FOREIGN KEY (`id_cat`) REFERENCES `cat` (`id_cat`)
) ENGINE=InnoDB AUTO_INCREMENT=41 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Catálogo de productos';

CREATE TABLE `ped` (
  `id_ped` int NOT NULL AUTO_INCREMENT COMMENT 'Identificador del pedido',
  `id_cli` int NOT NULL COMMENT 'Cliente que hizo el pedido',
  `fec_ped` date NOT NULL COMMENT 'Fecha del pedido',
  `est` varchar(30) NOT NULL COMMENT 'Estado del pedido',
  `tot` decimal(10,2) NOT NULL COMMENT 'Monto total del pedido en quetzales',
  PRIMARY KEY (`id_ped`),
  KEY `fk_ped_id_cli` (`id_cli`),
  CONSTRAINT `fk_ped_id_cli` FOREIGN KEY (`id_cli`) REFERENCES `cli` (`id_cli`)
) ENGINE=InnoDB AUTO_INCREMENT=251 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Pedidos realizados por los clientes';

CREATE TABLE `det_ped` (
  `id_det` int NOT NULL AUTO_INCREMENT COMMENT 'Identificador de la línea',
  `id_ped` int NOT NULL COMMENT 'Pedido al que pertenece',
  `id_pro` int NOT NULL COMMENT 'Producto vendido',
  `can` int NOT NULL COMMENT 'Unidades vendidas',
  `pre_uni` decimal(10,2) NOT NULL COMMENT 'Precio unitario aplicado',
  PRIMARY KEY (`id_det`),
  KEY `fk_det_ped_id_ped` (`id_ped`),
  KEY `fk_det_ped_id_pro` (`id_pro`),
  CONSTRAINT `fk_det_ped_id_ped` FOREIGN KEY (`id_ped`) REFERENCES `ped` (`id_ped`),
  CONSTRAINT `fk_det_ped_id_pro` FOREIGN KEY (`id_pro`) REFERENCES `pro` (`id_pro`)
) ENGINE=InnoDB AUTO_INCREMENT=601 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Líneas de cada pedido';