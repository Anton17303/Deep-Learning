CREATE TABLE `suc` (
  `id_suc` int NOT NULL AUTO_INCREMENT COMMENT 'Identificador de la sucursal',
  `nom` varchar(100) NOT NULL COMMENT 'Nombre de la sucursal',
  `ciu` varchar(100) NOT NULL COMMENT 'Ciudad',
  PRIMARY KEY (`id_suc`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Sucursales del banco';

CREATE TABLE `cli` (
  `id_cli` int NOT NULL AUTO_INCREMENT COMMENT 'Identificador del cliente',
  `nom` varchar(100) NOT NULL COMMENT 'Nombre del cliente',
  `fec_alta` date NOT NULL COMMENT 'Fecha de alta',
  PRIMARY KEY (`id_cli`)
) ENGINE=InnoDB AUTO_INCREMENT=81 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Clientes del banco';

CREATE TABLE `cue` (
  `id_cue` int NOT NULL AUTO_INCREMENT COMMENT 'Identificador de la cuenta',
  `id_cli` int NOT NULL COMMENT 'Titular de la cuenta',
  `id_suc` int NOT NULL COMMENT 'Sucursal donde se abrió',
  `tipo` varchar(30) NOT NULL COMMENT 'Tipo de cuenta',
  `sal` decimal(10,2) NOT NULL COMMENT 'Saldo actual',
  `fec_ape` date NOT NULL COMMENT 'Fecha de apertura',
  PRIMARY KEY (`id_cue`),
  KEY `fk_cue_id_cli` (`id_cli`),
  KEY `fk_cue_id_suc` (`id_suc`),
  CONSTRAINT `fk_cue_id_cli` FOREIGN KEY (`id_cli`) REFERENCES `cli` (`id_cli`),
  CONSTRAINT `fk_cue_id_suc` FOREIGN KEY (`id_suc`) REFERENCES `suc` (`id_suc`)
) ENGINE=InnoDB AUTO_INCREMENT=121 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Cuentas bancarias';

CREATE TABLE `tra` (
  `id_tra` int NOT NULL AUTO_INCREMENT COMMENT 'Identificador del movimiento',
  `id_cue` int NOT NULL COMMENT 'Cuenta afectada',
  `tipo` varchar(30) NOT NULL COMMENT 'Tipo de movimiento',
  `mon` decimal(10,2) NOT NULL COMMENT 'Monto del movimiento',
  `fecha` date NOT NULL COMMENT 'Fecha del movimiento',
  PRIMARY KEY (`id_tra`),
  KEY `fk_tra_id_cue` (`id_cue`),
  CONSTRAINT `fk_tra_id_cue` FOREIGN KEY (`id_cue`) REFERENCES `cue` (`id_cue`)
) ENGINE=InnoDB AUTO_INCREMENT=701 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Movimientos de las cuentas';

CREATE TABLE `pre` (
  `id_pre` int NOT NULL AUTO_INCREMENT COMMENT 'Identificador del préstamo',
  `id_cli` int NOT NULL COMMENT 'Cliente que recibió el préstamo',
  `mon` decimal(10,2) NOT NULL COMMENT 'Monto otorgado',
  `pla_mes` int NOT NULL COMMENT 'Plazo en meses',
  `est` varchar(30) NOT NULL COMMENT 'Estado del préstamo',
  PRIMARY KEY (`id_pre`),
  KEY `fk_pre_id_cli` (`id_cli`),
  CONSTRAINT `fk_pre_id_cli` FOREIGN KEY (`id_cli`) REFERENCES `cli` (`id_cli`)
) ENGINE=InnoDB AUTO_INCREMENT=51 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Préstamos otorgados';