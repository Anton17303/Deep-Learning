CREATE TABLE `carreras` (
  `id_carrera` int NOT NULL AUTO_INCREMENT COMMENT 'Identificador de la carrera',
  `nombre` varchar(100) NOT NULL COMMENT 'Nombre de la carrera',
  `facultad` varchar(30) NOT NULL COMMENT 'Facultad a la que pertenece',
  PRIMARY KEY (`id_carrera`)
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Carreras que ofrece la universidad';

CREATE TABLE `estudiantes` (
  `id_estudiante` int NOT NULL AUTO_INCREMENT COMMENT 'Identificador del estudiante',
  `nombre` varchar(100) NOT NULL COMMENT 'Nombre del estudiante',
  `id_carrera` int NOT NULL COMMENT 'Carrera que cursa',
  `fecha_ingreso` date NOT NULL COMMENT 'Fecha de ingreso',
  `promedio` decimal(10,2) NOT NULL COMMENT 'Promedio general acumulado',
  `becado` varchar(30) NOT NULL COMMENT 'Indica si tiene beca',
  PRIMARY KEY (`id_estudiante`),
  KEY `fk_estudiantes_id_carrera` (`id_carrera`),
  CONSTRAINT `fk_estudiantes_id_carrera` FOREIGN KEY (`id_carrera`) REFERENCES `carreras` (`id_carrera`)
) ENGINE=InnoDB AUTO_INCREMENT=81 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Estudiantes matriculados';

CREATE TABLE `profesores` (
  `id_profesor` int NOT NULL AUTO_INCREMENT COMMENT 'Identificador del profesor',
  `nombre` varchar(100) NOT NULL COMMENT 'Nombre del profesor',
  `departamento` varchar(30) NOT NULL COMMENT 'Departamento académico',
  `salario` decimal(10,2) NOT NULL COMMENT 'Salario mensual en quetzales',
  PRIMARY KEY (`id_profesor`)
) ENGINE=InnoDB AUTO_INCREMENT=16 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Catedráticos';

CREATE TABLE `cursos` (
  `id_curso` int NOT NULL AUTO_INCREMENT COMMENT 'Identificador del curso',
  `nombre` varchar(100) NOT NULL COMMENT 'Nombre del curso',
  `id_profesor` int NOT NULL COMMENT 'Profesor titular',
  `creditos` int NOT NULL COMMENT 'Créditos del curso',
  PRIMARY KEY (`id_curso`),
  KEY `fk_cursos_id_profesor` (`id_profesor`),
  CONSTRAINT `fk_cursos_id_profesor` FOREIGN KEY (`id_profesor`) REFERENCES `profesores` (`id_profesor`)
) ENGINE=InnoDB AUTO_INCREMENT=13 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Cursos del catálogo';

CREATE TABLE `inscripciones` (
  `id_inscripcion` int NOT NULL AUTO_INCREMENT COMMENT 'Identificador de la inscripción',
  `id_estudiante` int NOT NULL COMMENT 'Estudiante inscrito',
  `id_curso` int NOT NULL COMMENT 'Curso al que se inscribió',
  `semestre` varchar(30) NOT NULL COMMENT 'Semestre de la inscripción',
  `nota` int NOT NULL COMMENT 'Nota final obtenida',
  PRIMARY KEY (`id_inscripcion`),
  KEY `fk_inscripciones_id_estudiante` (`id_estudiante`),
  KEY `fk_inscripciones_id_curso` (`id_curso`),
  CONSTRAINT `fk_inscripciones_id_curso` FOREIGN KEY (`id_curso`) REFERENCES `cursos` (`id_curso`),
  CONSTRAINT `fk_inscripciones_id_estudiante` FOREIGN KEY (`id_estudiante`) REFERENCES `estudiantes` (`id_estudiante`)
) ENGINE=InnoDB AUTO_INCREMENT=401 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Inscripciones de estudiantes a cursos';