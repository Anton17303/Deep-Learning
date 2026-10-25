CREATE TABLE `departamentos` (
  `id_departamento` int NOT NULL AUTO_INCREMENT COMMENT 'Identificador del departamento',
  `nombre` varchar(100) NOT NULL COMMENT 'Nombre del departamento',
  `ubicacion` varchar(100) NOT NULL COMMENT 'Ciudad de la oficina',
  PRIMARY KEY (`id_departamento`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Departamentos de la empresa';

CREATE TABLE `puestos` (
  `id_puesto` int NOT NULL AUTO_INCREMENT COMMENT 'Identificador del puesto',
  `titulo` varchar(100) NOT NULL COMMENT 'Título del puesto',
  `salario_base` decimal(10,2) NOT NULL COMMENT 'Salario base mensual',
  PRIMARY KEY (`id_puesto`)
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Puestos de trabajo';

CREATE TABLE `empleados` (
  `id_empleado` int NOT NULL AUTO_INCREMENT COMMENT 'Identificador del empleado',
  `nombre` varchar(100) NOT NULL COMMENT 'Nombre del empleado',
  `id_departamento` int NOT NULL COMMENT 'Departamento al que pertenece',
  `id_puesto` int NOT NULL COMMENT 'Puesto que ocupa',
  `fecha_contratacion` date NOT NULL COMMENT 'Fecha de contratación',
  `modalidad` varchar(30) NOT NULL COMMENT 'Modalidad de trabajo',
  PRIMARY KEY (`id_empleado`),
  KEY `fk_empleados_id_departamento` (`id_departamento`),
  KEY `fk_empleados_id_puesto` (`id_puesto`),
  CONSTRAINT `fk_empleados_id_departamento` FOREIGN KEY (`id_departamento`) REFERENCES `departamentos` (`id_departamento`),
  CONSTRAINT `fk_empleados_id_puesto` FOREIGN KEY (`id_puesto`) REFERENCES `puestos` (`id_puesto`)
) ENGINE=InnoDB AUTO_INCREMENT=101 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Empleados';

CREATE TABLE `asistencias` (
  `id_asistencia` int NOT NULL AUTO_INCREMENT COMMENT 'Identificador del registro',
  `id_empleado` int NOT NULL COMMENT 'Empleado',
  `fecha` date NOT NULL COMMENT 'Fecha de asistencia',
  `horas_trabajadas` decimal(10,2) NOT NULL COMMENT 'Horas trabajadas ese día',
  PRIMARY KEY (`id_asistencia`),
  KEY `fk_asistencias_id_empleado` (`id_empleado`),
  CONSTRAINT `fk_asistencias_id_empleado` FOREIGN KEY (`id_empleado`) REFERENCES `empleados` (`id_empleado`)
) ENGINE=InnoDB AUTO_INCREMENT=701 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Registro diario de asistencia';

CREATE TABLE `vacaciones` (
  `id_vacacion` int NOT NULL AUTO_INCREMENT COMMENT 'Identificador de la solicitud',
  `id_empleado` int NOT NULL COMMENT 'Empleado',
  `fecha_inicio` date NOT NULL COMMENT 'Fecha de inicio',
  `dias` int NOT NULL COMMENT 'Días tomados',
  PRIMARY KEY (`id_vacacion`),
  KEY `fk_vacaciones_id_empleado` (`id_empleado`),
  CONSTRAINT `fk_vacaciones_id_empleado` FOREIGN KEY (`id_empleado`) REFERENCES `empleados` (`id_empleado`)
) ENGINE=InnoDB AUTO_INCREMENT=121 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Vacaciones tomadas';