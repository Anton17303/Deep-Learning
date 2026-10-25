CREATE TABLE `autores` (
  `id_autor` int NOT NULL AUTO_INCREMENT COMMENT 'Identificador del autor',
  `nombre` varchar(100) NOT NULL COMMENT 'Nombre del autor',
  `pais` varchar(100) NOT NULL COMMENT 'País de origen',
  PRIMARY KEY (`id_autor`)
) ENGINE=InnoDB AUTO_INCREMENT=16 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Autores de los libros';

CREATE TABLE `libros` (
  `id_libro` int NOT NULL AUTO_INCREMENT COMMENT 'Identificador del libro',
  `titulo` varchar(100) NOT NULL COMMENT 'Título del libro',
  `id_autor` int NOT NULL COMMENT 'Autor del libro',
  `anio_publicacion` int NOT NULL COMMENT 'Año de publicación',
  `paginas` int NOT NULL COMMENT 'Número de páginas',
  `genero` varchar(30) NOT NULL COMMENT 'Género literario',
  PRIMARY KEY (`id_libro`),
  KEY `fk_libros_id_autor` (`id_autor`),
  CONSTRAINT `fk_libros_id_autor` FOREIGN KEY (`id_autor`) REFERENCES `autores` (`id_autor`)
) ENGINE=InnoDB AUTO_INCREMENT=61 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Libros del acervo';

CREATE TABLE `socios` (
  `id_socio` int NOT NULL AUTO_INCREMENT COMMENT 'Identificador del socio',
  `nombre` varchar(100) NOT NULL COMMENT 'Nombre del socio',
  `fecha_alta` date NOT NULL COMMENT 'Fecha de alta como socio',
  PRIMARY KEY (`id_socio`)
) ENGINE=InnoDB AUTO_INCREMENT=71 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Socios de la biblioteca';

CREATE TABLE `prestamos` (
  `id_prestamo` int NOT NULL AUTO_INCREMENT COMMENT 'Identificador del préstamo',
  `id_libro` int NOT NULL COMMENT 'Libro prestado',
  `id_socio` int NOT NULL COMMENT 'Socio que lo solicitó',
  `fecha_prestamo` date NOT NULL COMMENT 'Fecha del préstamo',
  `dias_prestamo` int NOT NULL COMMENT 'Días de préstamo concedidos',
  `devuelto` varchar(30) NOT NULL COMMENT 'Indica si ya fue devuelto',
  PRIMARY KEY (`id_prestamo`),
  KEY `fk_prestamos_id_libro` (`id_libro`),
  KEY `fk_prestamos_id_socio` (`id_socio`),
  CONSTRAINT `fk_prestamos_id_libro` FOREIGN KEY (`id_libro`) REFERENCES `libros` (`id_libro`),
  CONSTRAINT `fk_prestamos_id_socio` FOREIGN KEY (`id_socio`) REFERENCES `socios` (`id_socio`)
) ENGINE=InnoDB AUTO_INCREMENT=351 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Préstamos de libros';