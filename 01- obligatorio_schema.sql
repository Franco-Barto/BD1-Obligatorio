

DROP DATABASE IF EXISTS obligatorio;
CREATE DATABASE obligatorio DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_spanish_ci;
USE obligatorio;


CREATE TABLE login(
    correo     VARCHAR(120) NOT NULL PRIMARY KEY,
    contraseña VARCHAR(56)  NOT NULL
);

CREATE TABLE admins (
   correo VARCHAR(120) NOT NULL PRIMARY KEY,
   es_administrador BOOLEAN NOT NULL,
   FOREIGN KEY (correo) REFERENCES login(correo)
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
   direccion VARCHAR(120) NOT NULL UNIQUE,
   telefono VARCHAR(20),
   correo VARCHAR(120) NOT NULL
);


CREATE TABLE maquinas (
   id INT AUTO_INCREMENT PRIMARY KEY,
   modelo VARCHAR(45) NOT NULL,
   id_cliente INT NOT NULL,
   ubicacion_cliente VARCHAR(120) NOT NULL,
   costo_alquiler_mensual DECIMAL(10,2) NOT NULL,
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
    PRIMARY KEY (id_tecnico,dia_semana),
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

drop user 'login';
drop user 'admin';
drop user 'noadmin';
create user 'login' identified by 'password';
grant select,insert on login to 'login';
grant select on admins to 'login';
flush privileges;
create user 'admin' identified by 'blablabla';
GRANT ALL PRIVILEGES ON * TO 'admin';
flush privileges;
create user 'noadmin' identified by 'blebleble';
grant select on * to 'noadmin';
flush privileges;
