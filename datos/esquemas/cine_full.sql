CREATE TABLE `peliculas` (
  `id_pelicula` int NOT NULL AUTO_INCREMENT COMMENT 'Identificador de la película',
  `titulo` varchar(100) NOT NULL COMMENT 'Título',
  `genero` varchar(30) NOT NULL COMMENT 'Género',
  `duracion_min` int NOT NULL COMMENT 'Duración en minutos',
  `anio` int NOT NULL COMMENT 'Año de estreno',
  PRIMARY KEY (`id_pelicula`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Cartelera de películas';

CREATE TABLE `salas` (
  `id_sala` int NOT NULL AUTO_INCREMENT COMMENT 'Identificador de la sala',
  `nombre` varchar(100) NOT NULL COMMENT 'Nombre de la sala',
  `capacidad` int NOT NULL COMMENT 'Número de butacas',
  PRIMARY KEY (`id_sala`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Salas del cine';

CREATE TABLE `funciones` (
  `id_funcion` int NOT NULL AUTO_INCREMENT COMMENT 'Identificador de la función',
  `id_pelicula` int NOT NULL COMMENT 'Película proyectada',
  `id_sala` int NOT NULL COMMENT 'Sala de proyección',
  `fecha` date NOT NULL COMMENT 'Fecha de la función',
  `precio_boleto` decimal(10,2) NOT NULL COMMENT 'Precio por boleto',
  PRIMARY KEY (`id_funcion`),
  KEY `fk_funciones_id_pelicula` (`id_pelicula`),
  KEY `fk_funciones_id_sala` (`id_sala`),
  CONSTRAINT `fk_funciones_id_pelicula` FOREIGN KEY (`id_pelicula`) REFERENCES `peliculas` (`id_pelicula`),
  CONSTRAINT `fk_funciones_id_sala` FOREIGN KEY (`id_sala`) REFERENCES `salas` (`id_sala`)
) ENGINE=InnoDB AUTO_INCREMENT=151 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Funciones programadas';

CREATE TABLE `clientes` (
  `id_cliente` int NOT NULL AUTO_INCREMENT COMMENT 'Identificador del cliente',
  `nombre` varchar(100) NOT NULL COMMENT 'Nombre del cliente',
  `correo` varchar(100) NOT NULL COMMENT 'Correo electrónico',
  PRIMARY KEY (`id_cliente`)
) ENGINE=InnoDB AUTO_INCREMENT=71 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Clientes frecuentes';

CREATE TABLE `boletos` (
  `id_boleto` int NOT NULL AUTO_INCREMENT COMMENT 'Identificador de la venta',
  `id_funcion` int NOT NULL COMMENT 'Función',
  `id_cliente` int NOT NULL COMMENT 'Cliente comprador',
  `cantidad` int NOT NULL COMMENT 'Boletos comprados',
  PRIMARY KEY (`id_boleto`),
  KEY `fk_boletos_id_funcion` (`id_funcion`),
  KEY `fk_boletos_id_cliente` (`id_cliente`),
  CONSTRAINT `fk_boletos_id_cliente` FOREIGN KEY (`id_cliente`) REFERENCES `clientes` (`id_cliente`),
  CONSTRAINT `fk_boletos_id_funcion` FOREIGN KEY (`id_funcion`) REFERENCES `funciones` (`id_funcion`)
) ENGINE=InnoDB AUTO_INCREMENT=601 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Boletos vendidos';