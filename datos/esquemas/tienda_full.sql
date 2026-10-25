CREATE TABLE `categorias` (
  `id_categoria` int NOT NULL AUTO_INCREMENT COMMENT 'Identificador de la categoría',
  `nombre` varchar(100) NOT NULL COMMENT 'Nombre de la categoría',
  PRIMARY KEY (`id_categoria`)
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Categorías de productos';

CREATE TABLE `clientes` (
  `id_cliente` int NOT NULL AUTO_INCREMENT COMMENT 'Identificador del cliente',
  `nombre` varchar(100) NOT NULL COMMENT 'Nombre completo del cliente',
  `correo` varchar(100) NOT NULL COMMENT 'Correo electrónico',
  `ciudad` varchar(100) NOT NULL COMMENT 'Ciudad de residencia',
  `fecha_registro` date NOT NULL COMMENT 'Fecha en que se registró',
  PRIMARY KEY (`id_cliente`)
) ENGINE=InnoDB AUTO_INCREMENT=61 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Clientes registrados en la tienda';

CREATE TABLE `productos` (
  `id_producto` int NOT NULL AUTO_INCREMENT COMMENT 'Identificador del producto',
  `nombre` varchar(100) NOT NULL COMMENT 'Nombre del producto',
  `id_categoria` int NOT NULL COMMENT 'Categoría del producto',
  `precio` decimal(10,2) NOT NULL COMMENT 'Precio de venta en quetzales',
  `stock` int NOT NULL COMMENT 'Unidades disponibles en inventario',
  PRIMARY KEY (`id_producto`),
  KEY `fk_productos_id_categoria` (`id_categoria`),
  CONSTRAINT `fk_productos_id_categoria` FOREIGN KEY (`id_categoria`) REFERENCES `categorias` (`id_categoria`)
) ENGINE=InnoDB AUTO_INCREMENT=41 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Catálogo de productos';

CREATE TABLE `pedidos` (
  `id_pedido` int NOT NULL AUTO_INCREMENT COMMENT 'Identificador del pedido',
  `id_cliente` int NOT NULL COMMENT 'Cliente que hizo el pedido',
  `fecha_pedido` date NOT NULL COMMENT 'Fecha del pedido',
  `estado` varchar(30) NOT NULL COMMENT 'Estado del pedido',
  `total` decimal(10,2) NOT NULL COMMENT 'Monto total del pedido en quetzales',
  PRIMARY KEY (`id_pedido`),
  KEY `fk_pedidos_id_cliente` (`id_cliente`),
  CONSTRAINT `fk_pedidos_id_cliente` FOREIGN KEY (`id_cliente`) REFERENCES `clientes` (`id_cliente`)
) ENGINE=InnoDB AUTO_INCREMENT=251 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Pedidos realizados por los clientes';

CREATE TABLE `detalle_pedido` (
  `id_detalle` int NOT NULL AUTO_INCREMENT COMMENT 'Identificador de la línea',
  `id_pedido` int NOT NULL COMMENT 'Pedido al que pertenece',
  `id_producto` int NOT NULL COMMENT 'Producto vendido',
  `cantidad` int NOT NULL COMMENT 'Unidades vendidas',
  `precio_unitario` decimal(10,2) NOT NULL COMMENT 'Precio unitario aplicado',
  PRIMARY KEY (`id_detalle`),
  KEY `fk_detalle_pedido_id_pedido` (`id_pedido`),
  KEY `fk_detalle_pedido_id_producto` (`id_producto`),
  CONSTRAINT `fk_detalle_pedido_id_pedido` FOREIGN KEY (`id_pedido`) REFERENCES `pedidos` (`id_pedido`),
  CONSTRAINT `fk_detalle_pedido_id_producto` FOREIGN KEY (`id_producto`) REFERENCES `productos` (`id_producto`)
) ENGINE=InnoDB AUTO_INCREMENT=601 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Líneas de cada pedido';