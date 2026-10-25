CREATE TABLE `est` (
  `id_est` int NOT NULL AUTO_INCREMENT COMMENT 'Identificador del estadio',
  `nom` varchar(100) NOT NULL COMMENT 'Nombre del estadio',
  `ciu` varchar(100) NOT NULL COMMENT 'Ciudad donde se ubica',
  `cap` int NOT NULL COMMENT 'Capacidad de espectadores',
  PRIMARY KEY (`id_est`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Estadios';

CREATE TABLE `equ` (
  `id_equ` int NOT NULL AUTO_INCREMENT COMMENT 'Identificador del equipo',
  `nom` varchar(100) NOT NULL COMMENT 'Nombre del equipo',
  `id_est` int NOT NULL COMMENT 'Estadio donde juega de local',
  `fund` int NOT NULL COMMENT 'Año de fundación',
  PRIMARY KEY (`id_equ`),
  KEY `fk_equ_id_est` (`id_est`),
  CONSTRAINT `fk_equ_id_est` FOREIGN KEY (`id_est`) REFERENCES `est` (`id_est`)
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Equipos de la liga';

CREATE TABLE `jug` (
  `id_jug` int NOT NULL AUTO_INCREMENT COMMENT 'Identificador del jugador',
  `nom` varchar(100) NOT NULL COMMENT 'Nombre del jugador',
  `id_equ` int NOT NULL COMMENT 'Equipo al que pertenece',
  `pos` varchar(30) NOT NULL COMMENT 'Posición en el campo',
  `edad` int NOT NULL COMMENT 'Edad en años',
  `sal` decimal(10,2) NOT NULL COMMENT 'Salario mensual en quetzales',
  PRIMARY KEY (`id_jug`),
  KEY `fk_jug_id_equ` (`id_equ`),
  CONSTRAINT `fk_jug_id_equ` FOREIGN KEY (`id_equ`) REFERENCES `equ` (`id_equ`)
) ENGINE=InnoDB AUTO_INCREMENT=121 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Jugadores';

CREATE TABLE `par` (
  `id_par` int NOT NULL AUTO_INCREMENT COMMENT 'Identificador del partido',
  `id_loc` int NOT NULL COMMENT 'Equipo local',
  `id_vis` int NOT NULL COMMENT 'Equipo visitante',
  `fec_par` date NOT NULL COMMENT 'Fecha del partido',
  `jor` int NOT NULL COMMENT 'Número de jornada',
  PRIMARY KEY (`id_par`),
  KEY `fk_par_id_loc` (`id_loc`),
  KEY `fk_par_id_vis` (`id_vis`),
  CONSTRAINT `fk_par_id_loc` FOREIGN KEY (`id_loc`) REFERENCES `equ` (`id_equ`),
  CONSTRAINT `fk_par_id_vis` FOREIGN KEY (`id_vis`) REFERENCES `equ` (`id_equ`)
) ENGINE=InnoDB AUTO_INCREMENT=57 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Partidos jugados';

CREATE TABLE `gol` (
  `id_gol` int NOT NULL AUTO_INCREMENT COMMENT 'Identificador del gol',
  `id_par` int NOT NULL COMMENT 'Partido en que se anotó',
  `id_jug` int NOT NULL COMMENT 'Jugador que anotó',
  `min` int NOT NULL COMMENT 'Minuto del gol',
  PRIMARY KEY (`id_gol`),
  KEY `fk_gol_id_par` (`id_par`),
  KEY `fk_gol_id_jug` (`id_jug`),
  CONSTRAINT `fk_gol_id_jug` FOREIGN KEY (`id_jug`) REFERENCES `jug` (`id_jug`),
  CONSTRAINT `fk_gol_id_par` FOREIGN KEY (`id_par`) REFERENCES `par` (`id_par`)
) ENGINE=InnoDB AUTO_INCREMENT=151 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Goles anotados';

CREATE TABLE `tar` (
  `id_tar` int NOT NULL AUTO_INCREMENT COMMENT 'Identificador de la tarjeta',
  `id_par` int NOT NULL COMMENT 'Partido en que se mostró',
  `id_jug` int NOT NULL COMMENT 'Jugador sancionado',
  `tipo` varchar(30) NOT NULL COMMENT 'Tipo de tarjeta',
  PRIMARY KEY (`id_tar`),
  KEY `fk_tar_id_par` (`id_par`),
  KEY `fk_tar_id_jug` (`id_jug`),
  CONSTRAINT `fk_tar_id_jug` FOREIGN KEY (`id_jug`) REFERENCES `jug` (`id_jug`),
  CONSTRAINT `fk_tar_id_par` FOREIGN KEY (`id_par`) REFERENCES `par` (`id_par`)
) ENGINE=InnoDB AUTO_INCREMENT=121 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Tarjetas mostradas';