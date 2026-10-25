CREATE TABLE `aut` (
  `id_aut` int NOT NULL AUTO_INCREMENT COMMENT 'Identificador del autor',
  `nom` varchar(100) NOT NULL COMMENT 'Nombre del autor',
  `pais` varchar(100) NOT NULL COMMENT 'País de origen',
  PRIMARY KEY (`id_aut`)
) ENGINE=InnoDB AUTO_INCREMENT=16 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Autores de los libros';

CREATE TABLE `lib` (
  `id_lib` int NOT NULL AUTO_INCREMENT COMMENT 'Identificador del libro',
  `tit` varchar(100) NOT NULL COMMENT 'Título del libro',
  `id_aut` int NOT NULL COMMENT 'Autor del libro',
  `anio_pub` int NOT NULL COMMENT 'Año de publicación',
  `pag` int NOT NULL COMMENT 'Número de páginas',
  `gen` varchar(30) NOT NULL COMMENT 'Género literario',
  PRIMARY KEY (`id_lib`),
  KEY `fk_lib_id_aut` (`id_aut`),
  CONSTRAINT `fk_lib_id_aut` FOREIGN KEY (`id_aut`) REFERENCES `aut` (`id_aut`)
) ENGINE=InnoDB AUTO_INCREMENT=61 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Libros del acervo';

CREATE TABLE `soc` (
  `id_soc` int NOT NULL AUTO_INCREMENT COMMENT 'Identificador del socio',
  `nom` varchar(100) NOT NULL COMMENT 'Nombre del socio',
  `fec_alta` date NOT NULL COMMENT 'Fecha de alta como socio',
  PRIMARY KEY (`id_soc`)
) ENGINE=InnoDB AUTO_INCREMENT=71 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Socios de la biblioteca';

CREATE TABLE `pre` (
  `id_pre` int NOT NULL AUTO_INCREMENT COMMENT 'Identificador del préstamo',
  `id_lib` int NOT NULL COMMENT 'Libro prestado',
  `id_soc` int NOT NULL COMMENT 'Socio que lo solicitó',
  `fec_pre` date NOT NULL COMMENT 'Fecha del préstamo',
  `dias_pre` int NOT NULL COMMENT 'Días de préstamo concedidos',
  `dev` varchar(30) NOT NULL COMMENT 'Indica si ya fue devuelto',
  PRIMARY KEY (`id_pre`),
  KEY `fk_pre_id_lib` (`id_lib`),
  KEY `fk_pre_id_soc` (`id_soc`),
  CONSTRAINT `fk_pre_id_lib` FOREIGN KEY (`id_lib`) REFERENCES `lib` (`id_lib`),
  CONSTRAINT `fk_pre_id_soc` FOREIGN KEY (`id_soc`) REFERENCES `soc` (`id_soc`)
) ENGINE=InnoDB AUTO_INCREMENT=351 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Préstamos de libros';