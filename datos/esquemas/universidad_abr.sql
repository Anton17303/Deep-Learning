CREATE TABLE `car` (
  `id_car` int NOT NULL AUTO_INCREMENT COMMENT 'Identificador de la carrera',
  `nom` varchar(100) NOT NULL COMMENT 'Nombre de la carrera',
  `fac` varchar(30) NOT NULL COMMENT 'Facultad a la que pertenece',
  PRIMARY KEY (`id_car`)
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Carreras que ofrece la universidad';

CREATE TABLE `est` (
  `id_est` int NOT NULL AUTO_INCREMENT COMMENT 'Identificador del estudiante',
  `nom` varchar(100) NOT NULL COMMENT 'Nombre del estudiante',
  `id_car` int NOT NULL COMMENT 'Carrera que cursa',
  `fec_ing` date NOT NULL COMMENT 'Fecha de ingreso',
  `pro` decimal(10,2) NOT NULL COMMENT 'Promedio general acumulado',
  `bec` varchar(30) NOT NULL COMMENT 'Indica si tiene beca',
  PRIMARY KEY (`id_est`),
  KEY `fk_est_id_car` (`id_car`),
  CONSTRAINT `fk_est_id_car` FOREIGN KEY (`id_car`) REFERENCES `car` (`id_car`)
) ENGINE=InnoDB AUTO_INCREMENT=81 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Estudiantes matriculados';

CREATE TABLE `pro` (
  `id_pro` int NOT NULL AUTO_INCREMENT COMMENT 'Identificador del profesor',
  `nom` varchar(100) NOT NULL COMMENT 'Nombre del profesor',
  `dep` varchar(30) NOT NULL COMMENT 'Departamento académico',
  `sal` decimal(10,2) NOT NULL COMMENT 'Salario mensual en quetzales',
  PRIMARY KEY (`id_pro`)
) ENGINE=InnoDB AUTO_INCREMENT=16 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Catedráticos';

CREATE TABLE `cur` (
  `id_cur` int NOT NULL AUTO_INCREMENT COMMENT 'Identificador del curso',
  `nom` varchar(100) NOT NULL COMMENT 'Nombre del curso',
  `id_pro` int NOT NULL COMMENT 'Profesor titular',
  `cre` int NOT NULL COMMENT 'Créditos del curso',
  PRIMARY KEY (`id_cur`),
  KEY `fk_cur_id_pro` (`id_pro`),
  CONSTRAINT `fk_cur_id_pro` FOREIGN KEY (`id_pro`) REFERENCES `pro` (`id_pro`)
) ENGINE=InnoDB AUTO_INCREMENT=13 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Cursos del catálogo';

CREATE TABLE `ins` (
  `id_ins` int NOT NULL AUTO_INCREMENT COMMENT 'Identificador de la inscripción',
  `id_est` int NOT NULL COMMENT 'Estudiante inscrito',
  `id_cur` int NOT NULL COMMENT 'Curso al que se inscribió',
  `sem` varchar(30) NOT NULL COMMENT 'Semestre de la inscripción',
  `nota` int NOT NULL COMMENT 'Nota final obtenida',
  PRIMARY KEY (`id_ins`),
  KEY `fk_ins_id_est` (`id_est`),
  KEY `fk_ins_id_cur` (`id_cur`),
  CONSTRAINT `fk_ins_id_cur` FOREIGN KEY (`id_cur`) REFERENCES `cur` (`id_cur`),
  CONSTRAINT `fk_ins_id_est` FOREIGN KEY (`id_est`) REFERENCES `est` (`id_est`)
) ENGINE=InnoDB AUTO_INCREMENT=401 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Inscripciones de estudiantes a cursos';