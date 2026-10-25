CREATE TABLE `dep` (
  `id_dep` int NOT NULL AUTO_INCREMENT COMMENT 'Identificador del departamento',
  `nom` varchar(100) NOT NULL COMMENT 'Nombre del departamento',
  `ubi` varchar(100) NOT NULL COMMENT 'Ciudad de la oficina',
  PRIMARY KEY (`id_dep`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Departamentos de la empresa';

CREATE TABLE `pue` (
  `id_pue` int NOT NULL AUTO_INCREMENT COMMENT 'Identificador del puesto',
  `tit` varchar(100) NOT NULL COMMENT 'Título del puesto',
  `sal_base` decimal(10,2) NOT NULL COMMENT 'Salario base mensual',
  PRIMARY KEY (`id_pue`)
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Puestos de trabajo';

CREATE TABLE `emp` (
  `id_emp` int NOT NULL AUTO_INCREMENT COMMENT 'Identificador del empleado',
  `nom` varchar(100) NOT NULL COMMENT 'Nombre del empleado',
  `id_dep` int NOT NULL COMMENT 'Departamento al que pertenece',
  `id_pue` int NOT NULL COMMENT 'Puesto que ocupa',
  `fec_con` date NOT NULL COMMENT 'Fecha de contratación',
  `moda` varchar(30) NOT NULL COMMENT 'Modalidad de trabajo',
  PRIMARY KEY (`id_emp`),
  KEY `fk_emp_id_dep` (`id_dep`),
  KEY `fk_emp_id_pue` (`id_pue`),
  CONSTRAINT `fk_emp_id_dep` FOREIGN KEY (`id_dep`) REFERENCES `dep` (`id_dep`),
  CONSTRAINT `fk_emp_id_pue` FOREIGN KEY (`id_pue`) REFERENCES `pue` (`id_pue`)
) ENGINE=InnoDB AUTO_INCREMENT=101 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Empleados';

CREATE TABLE `asi` (
  `id_asi` int NOT NULL AUTO_INCREMENT COMMENT 'Identificador del registro',
  `id_emp` int NOT NULL COMMENT 'Empleado',
  `fecha` date NOT NULL COMMENT 'Fecha de asistencia',
  `hor_tra` decimal(10,2) NOT NULL COMMENT 'Horas trabajadas ese día',
  PRIMARY KEY (`id_asi`),
  KEY `fk_asi_id_emp` (`id_emp`),
  CONSTRAINT `fk_asi_id_emp` FOREIGN KEY (`id_emp`) REFERENCES `emp` (`id_emp`)
) ENGINE=InnoDB AUTO_INCREMENT=701 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Registro diario de asistencia';

CREATE TABLE `vac` (
  `id_vac` int NOT NULL AUTO_INCREMENT COMMENT 'Identificador de la solicitud',
  `id_emp` int NOT NULL COMMENT 'Empleado',
  `fec_ini` date NOT NULL COMMENT 'Fecha de inicio',
  `dias` int NOT NULL COMMENT 'Días tomados',
  PRIMARY KEY (`id_vac`),
  KEY `fk_vac_id_emp` (`id_emp`),
  CONSTRAINT `fk_vac_id_emp` FOREIGN KEY (`id_emp`) REFERENCES `emp` (`id_emp`)
) ENGINE=InnoDB AUTO_INCREMENT=121 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Vacaciones tomadas';