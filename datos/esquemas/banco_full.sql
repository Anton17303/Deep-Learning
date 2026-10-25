CREATE TABLE `sucursales` (
  `id_sucursal` int NOT NULL AUTO_INCREMENT COMMENT 'Identificador de la sucursal',
  `nombre` varchar(100) NOT NULL COMMENT 'Nombre de la sucursal',
  `ciudad` varchar(100) NOT NULL COMMENT 'Ciudad',
  PRIMARY KEY (`id_sucursal`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Sucursales del banco';

CREATE TABLE `clientes` (
  `id_cliente` int NOT NULL AUTO_INCREMENT COMMENT 'Identificador del cliente',
  `nombre` varchar(100) NOT NULL COMMENT 'Nombre del cliente',
  `fecha_alta` date NOT NULL COMMENT 'Fecha de alta',
  PRIMARY KEY (`id_cliente`)
) ENGINE=InnoDB AUTO_INCREMENT=81 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Clientes del banco';

CREATE TABLE `cuentas` (
  `id_cuenta` int NOT NULL AUTO_INCREMENT COMMENT 'Identificador de la cuenta',
  `id_cliente` int NOT NULL COMMENT 'Titular de la cuenta',
  `id_sucursal` int NOT NULL COMMENT 'Sucursal donde se abrió',
  `tipo` varchar(30) NOT NULL COMMENT 'Tipo de cuenta',
  `saldo` decimal(10,2) NOT NULL COMMENT 'Saldo actual',
  `fecha_apertura` date NOT NULL COMMENT 'Fecha de apertura',
  PRIMARY KEY (`id_cuenta`),
  KEY `fk_cuentas_id_cliente` (`id_cliente`),
  KEY `fk_cuentas_id_sucursal` (`id_sucursal`),
  CONSTRAINT `fk_cuentas_id_cliente` FOREIGN KEY (`id_cliente`) REFERENCES `clientes` (`id_cliente`),
  CONSTRAINT `fk_cuentas_id_sucursal` FOREIGN KEY (`id_sucursal`) REFERENCES `sucursales` (`id_sucursal`)
) ENGINE=InnoDB AUTO_INCREMENT=121 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Cuentas bancarias';

CREATE TABLE `transacciones` (
  `id_transaccion` int NOT NULL AUTO_INCREMENT COMMENT 'Identificador del movimiento',
  `id_cuenta` int NOT NULL COMMENT 'Cuenta afectada',
  `tipo` varchar(30) NOT NULL COMMENT 'Tipo de movimiento',
  `monto` decimal(10,2) NOT NULL COMMENT 'Monto del movimiento',
  `fecha` date NOT NULL COMMENT 'Fecha del movimiento',
  PRIMARY KEY (`id_transaccion`),
  KEY `fk_transacciones_id_cuenta` (`id_cuenta`),
  CONSTRAINT `fk_transacciones_id_cuenta` FOREIGN KEY (`id_cuenta`) REFERENCES `cuentas` (`id_cuenta`)
) ENGINE=InnoDB AUTO_INCREMENT=701 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Movimientos de las cuentas';

CREATE TABLE `prestamos` (
  `id_prestamo` int NOT NULL AUTO_INCREMENT COMMENT 'Identificador del préstamo',
  `id_cliente` int NOT NULL COMMENT 'Cliente que recibió el préstamo',
  `monto` decimal(10,2) NOT NULL COMMENT 'Monto otorgado',
  `plazo_meses` int NOT NULL COMMENT 'Plazo en meses',
  `estado` varchar(30) NOT NULL COMMENT 'Estado del préstamo',
  PRIMARY KEY (`id_prestamo`),
  KEY `fk_prestamos_id_cliente` (`id_cliente`),
  CONSTRAINT `fk_prestamos_id_cliente` FOREIGN KEY (`id_cliente`) REFERENCES `clientes` (`id_cliente`)
) ENGINE=InnoDB AUTO_INCREMENT=51 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Préstamos otorgados';