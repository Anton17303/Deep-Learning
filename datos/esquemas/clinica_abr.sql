CREATE TABLE `esp` (
  `id_esp` int NOT NULL AUTO_INCREMENT COMMENT 'Identificador de la especialidad',
  `nom` varchar(100) NOT NULL COMMENT 'Nombre de la especialidad',
  PRIMARY KEY (`id_esp`)
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Especialidades médicas';

CREATE TABLE `med` (
  `id_med` int NOT NULL AUTO_INCREMENT COMMENT 'Identificador del médico',
  `nom` varchar(100) NOT NULL COMMENT 'Nombre del médico',
  `id_esp` int NOT NULL COMMENT 'Especialidad del médico',
  `ani_exp` int NOT NULL COMMENT 'Años de experiencia',
  PRIMARY KEY (`id_med`),
  KEY `fk_med_id_esp` (`id_esp`),
  CONSTRAINT `fk_med_id_esp` FOREIGN KEY (`id_esp`) REFERENCES `esp` (`id_esp`)
) ENGINE=InnoDB AUTO_INCREMENT=21 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Médicos de la clínica';

CREATE TABLE `pac` (
  `id_pac` int NOT NULL AUTO_INCREMENT COMMENT 'Identificador del paciente',
  `nom` varchar(100) NOT NULL COMMENT 'Nombre del paciente',
  `fec_nac` date NOT NULL COMMENT 'Fecha de nacimiento',
  `ciu` varchar(100) NOT NULL COMMENT 'Ciudad de residencia',
  PRIMARY KEY (`id_pac`)
) ENGINE=InnoDB AUTO_INCREMENT=91 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Pacientes registrados';

CREATE TABLE `medi` (
  `id_med` int NOT NULL AUTO_INCREMENT COMMENT 'Identificador del medicamento',
  `nom` varchar(100) NOT NULL COMMENT 'Nombre del medicamento',
  `pre` decimal(10,2) NOT NULL COMMENT 'Precio unitario',
  PRIMARY KEY (`id_med`)
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Medicamentos disponibles';

CREATE TABLE `cit` (
  `id_cita` int NOT NULL AUTO_INCREMENT COMMENT 'Identificador de la cita',
  `id_pac` int NOT NULL COMMENT 'Paciente atendido',
  `id_med` int NOT NULL COMMENT 'Médico que atendió',
  `fec_cita` date NOT NULL COMMENT 'Fecha de la cita',
  `mot` varchar(30) NOT NULL COMMENT 'Motivo de la consulta',
  `cos` decimal(10,2) NOT NULL COMMENT 'Costo de la consulta',
  PRIMARY KEY (`id_cita`),
  KEY `fk_cit_id_pac` (`id_pac`),
  KEY `fk_cit_id_med` (`id_med`),
  CONSTRAINT `fk_cit_id_med` FOREIGN KEY (`id_med`) REFERENCES `med` (`id_med`),
  CONSTRAINT `fk_cit_id_pac` FOREIGN KEY (`id_pac`) REFERENCES `pac` (`id_pac`)
) ENGINE=InnoDB AUTO_INCREMENT=301 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Citas médicas';

CREATE TABLE `rec` (
  `id_rec` int NOT NULL AUTO_INCREMENT COMMENT 'Identificador de la receta',
  `id_cita` int NOT NULL COMMENT 'Cita en que se recetó',
  `id_med` int NOT NULL COMMENT 'Medicamento recetado',
  `dias_tra` int NOT NULL COMMENT 'Duración del tratamiento en días',
  PRIMARY KEY (`id_rec`),
  KEY `fk_rec_id_cita` (`id_cita`),
  KEY `fk_rec_id_med` (`id_med`),
  CONSTRAINT `fk_rec_id_cita` FOREIGN KEY (`id_cita`) REFERENCES `cit` (`id_cita`),
  CONSTRAINT `fk_rec_id_med` FOREIGN KEY (`id_med`) REFERENCES `medi` (`id_med`)
) ENGINE=InnoDB AUTO_INCREMENT=351 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Medicamentos recetados en cada cita';