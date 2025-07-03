

DROP DATABASE IF EXISTS obligatorio;
CREATE DATABASE obligatorio DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_spanish_ci;
USE obligatorio;


CREATE TABLE login (
   correo VARCHAR(120) NOT NULL PRIMARY KEY,
   contraseña VARCHAR(56) NOT NULL,
   es_administrador BOOLEAN NOT NULL
);


CREATE TABLE proveedores (
   id INT AUTO_INCREMENT PRIMARY KEY,
   nombre VARCHAR(45) NOT NULL,
   contacto VARCHAR(20) NOT NULL,
   tipo ENUM('servicio','insumo','maquinaria') NOT NULL
);


CREATE TABLE insumos (
   id INT AUTO_INCREMENT PRIMARY KEY,
   descripcion TEXT NOT NULL,
   tipo VARCHAR(50),
   precio_unitario DECIMAL(10,2) NOT NULL,
   id_proveedor INT NOT NULL,
   FOREIGN KEY (id_proveedor) REFERENCES proveedores(id)
);


CREATE TABLE clientes (
   id INT AUTO_INCREMENT PRIMARY KEY,
   nombre VARCHAR(50) NOT NULL,
   telefono VARCHAR(20),
   correo VARCHAR(120) NOT NULL
);

CREATE TABLE direcciones (
   id INT AUTO_INCREMENT PRIMARY KEY,
   id_cliente INT NOT NULL,
   direccion VARCHAR(120) NOT NULL,
   FOREIGN KEY (id_cliente) REFERENCES clientes(id) ON DELETE CASCADE
);

CREATE TABLE maquinas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    modelo VARCHAR (45) NOT NULL,
    fecha_compra DATE,
    disponibilidad BOOLEAN NOT NULL
);

CREATE TABLE maquinas_alquiler(
   id_maquina INT PRIMARY KEY,
   id_cliente INT NOT NULL,
   costo_alquiler_mensual DECIMAL(10,2) NOT NULL,
   fecha_alquiler DATE NOT NULL,
   FOREIGN KEY (id_maquina) REFERENCES maquinas(id),
   FOREIGN KEY (id_cliente) REFERENCES clientes(id)
);


CREATE TABLE registro_consumo (
   id INT AUTO_INCREMENT PRIMARY KEY,
   id_maquina INT NOT NULL,
   id_insumo INT NOT NULL,
   fecha DATE NOT NULL,
   cantidad_usada DECIMAL(6,2) NOT NULL,
   FOREIGN KEY (id_maquina) REFERENCES maquinas(id),
   FOREIGN KEY (id_insumo) REFERENCES insumos(id)
);


CREATE TABLE tecnicos (
   id INT AUTO_INCREMENT PRIMARY KEY,
   ci INT(8) UNIQUE,
   nombre VARCHAR(45) NOT NULL,
   apellido VARCHAR(45) NOT NULL,
   telefono VARCHAR(20)
);

CREATE TABLE horario_tecnicos (
    id_tecnico INT,
    dia_semana INT NOT NULL,
    hora_ingreso TIME NOT NULL,
    hora_salida TIME NOT NULL,
    FOREIGN KEY (id_tecnico) REFERENCES tecnicos(id)
);


CREATE TABLE mantenimientos (
   id INT AUTO_INCREMENT PRIMARY KEY,
   id_maquina INT NOT NULL,
   id_tecnico INT NOT NULL,
   tipo ENUM('preventivo', 'correctivo', 'predictivo') NOT NULL,
   fecha DATE NOT NULL,
   hora TIME NOT NULL,
   observaciones TEXT,
   FOREIGN KEY (id_maquina) REFERENCES maquinas(id),
   FOREIGN KEY (id_tecnico) REFERENCES tecnicos(id)
);
