CREATE TABLE `especialidades` (
  `id_especialidad` int NOT NULL AUTO_INCREMENT COMMENT 'Identificador de la especialidad',
  `nombre` varchar(100) NOT NULL COMMENT 'Nombre de la especialidad',
  PRIMARY KEY (`id_especialidad`)
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Especialidades médicas';

CREATE TABLE `medicos` (
  `id_medico` int NOT NULL AUTO_INCREMENT COMMENT 'Identificador del médico',
  `nombre` varchar(100) NOT NULL COMMENT 'Nombre del médico',
  `id_especialidad` int NOT NULL COMMENT 'Especialidad del médico',
  `anios_experiencia` int NOT NULL COMMENT 'Años de experiencia',
  PRIMARY KEY (`id_medico`),
  KEY `fk_medicos_id_especialidad` (`id_especialidad`),
  CONSTRAINT `fk_medicos_id_especialidad` FOREIGN KEY (`id_especialidad`) REFERENCES `especialidades` (`id_especialidad`)
) ENGINE=InnoDB AUTO_INCREMENT=21 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Médicos de la clínica';

CREATE TABLE `pacientes` (
  `id_paciente` int NOT NULL AUTO_INCREMENT COMMENT 'Identificador del paciente',
  `nombre` varchar(100) NOT NULL COMMENT 'Nombre del paciente',
  `fecha_nacimiento` date NOT NULL COMMENT 'Fecha de nacimiento',
  `ciudad` varchar(100) NOT NULL COMMENT 'Ciudad de residencia',
  PRIMARY KEY (`id_paciente`)
) ENGINE=InnoDB AUTO_INCREMENT=91 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Pacientes registrados';

CREATE TABLE `medicamentos` (
  `id_medicamento` int NOT NULL AUTO_INCREMENT COMMENT 'Identificador del medicamento',
  `nombre` varchar(100) NOT NULL COMMENT 'Nombre del medicamento',
  `precio` decimal(10,2) NOT NULL COMMENT 'Precio unitario',
  PRIMARY KEY (`id_medicamento`)
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Medicamentos disponibles';

CREATE TABLE `citas` (
  `id_cita` int NOT NULL AUTO_INCREMENT COMMENT 'Identificador de la cita',
  `id_paciente` int NOT NULL COMMENT 'Paciente atendido',
  `id_medico` int NOT NULL COMMENT 'Médico que atendió',
  `fecha_cita` date NOT NULL COMMENT 'Fecha de la cita',
  `motivo` varchar(30) NOT NULL COMMENT 'Motivo de la consulta',
  `costo` decimal(10,2) NOT NULL COMMENT 'Costo de la consulta',
  PRIMARY KEY (`id_cita`),
  KEY `fk_citas_id_paciente` (`id_paciente`),
  KEY `fk_citas_id_medico` (`id_medico`),
  CONSTRAINT `fk_citas_id_medico` FOREIGN KEY (`id_medico`) REFERENCES `medicos` (`id_medico`),
  CONSTRAINT `fk_citas_id_paciente` FOREIGN KEY (`id_paciente`) REFERENCES `pacientes` (`id_paciente`)
) ENGINE=InnoDB AUTO_INCREMENT=301 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Citas médicas';

CREATE TABLE `recetas` (
  `id_receta` int NOT NULL AUTO_INCREMENT COMMENT 'Identificador de la receta',
  `id_cita` int NOT NULL COMMENT 'Cita en que se recetó',
  `id_medicamento` int NOT NULL COMMENT 'Medicamento recetado',
  `dias_tratamiento` int NOT NULL COMMENT 'Duración del tratamiento en días',
  PRIMARY KEY (`id_receta`),
  KEY `fk_recetas_id_cita` (`id_cita`),
  KEY `fk_recetas_id_medicamento` (`id_medicamento`),
  CONSTRAINT `fk_recetas_id_cita` FOREIGN KEY (`id_cita`) REFERENCES `citas` (`id_cita`),
  CONSTRAINT `fk_recetas_id_medicamento` FOREIGN KEY (`id_medicamento`) REFERENCES `medicamentos` (`id_medicamento`)
) ENGINE=InnoDB AUTO_INCREMENT=351 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Medicamentos recetados en cada cita';